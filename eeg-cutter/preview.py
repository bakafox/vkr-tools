import numpy as np
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

from windows.PreviewWindow import PreviewWindow


def amplitude_to_color(value, power_min, power_max):
    if power_max == power_min:
        return QtGui.QColor(0, 255, 0)

    t_real = max(0.0, min(1.0, (value - power_min) / (power_max - power_min)))
    t_zero = max(0.0, min(1.0, (0.0   - power_min) / (power_max - power_min)))

    if t_real <= t_zero:
        scaled = (t_real / t_zero) if t_zero else 0.0
        return QtGui.QColor(
            0, int(255 * scaled), int(255 * (1 - scaled))
        )
    else:
        scaled = ((t_real - t_zero) / (1 - t_zero)) if t_zero < 1 else 0.0
        return QtGui.QColor(int(255 * scaled), int(255 * (1 - scaled)), 0)


def project(xs, ys, zs, az_deg, el_deg, w, h, scale=1.0):
    az = np.radians(az_deg)
    el = np.radians(el_deg)
    xs, ys, zs = (np.asarray(a, float) for a in (xs, ys, zs))

    xr =  np.cos(az) * xs + np.sin(az) * ys
    yr = -np.sin(az) * xs + np.cos(az) * ys
    sx =  xr
    sy = -np.sin(el) * zs + np.cos(el) * yr

    deep = np.cos(el) * zs + np.sin(el) * yr
    span = max(sx.max() - sx.min(), sy.max() - sy.min(), 1e-9)
    base = min(w, h) * 0.7 / span

    sc   = base * scale
    px = sx * sc + w / 2
    py = sy * sc + h / 2

    return px, py, deep


class Canvas(QtWidgets.QLabel):
    pointClicked = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtCore.Qt.CrossCursor)
        self._data      = []
        self._power_min = 0.0
        self._power_max = 1.0
        self._az        = 0.0
        self._el        = 20.0
        self._scale     = 1.0
        self._curr_zone = None
        self._hits      = []

    def set_data(self, data, power_min, power_max):
        self._data = data
        self._power_min = power_min
        self._power_max = power_max
        self.redraw()

    def rotate(self, delta_deg):
        self._az = (self._az + delta_deg) % 360
        self.redraw()

    def set_elevation(self, el_deg):
        self._el = el_deg
        self.redraw()

    def set_scale(self, scale):
        self._scale = float(scale)
        self.redraw()

    def set_curr_zone(self, zone):
        self._curr_zone = zone
        self.redraw()

    def reset_view(self):
        self._az = 0.0
        self.set_elevation(20.0)
        self.set_scale(1.0)
        self.redraw()

    def _rows(self):
        if self._curr_zone is None:
            return self._data
        return [r for r in self._data if r['Zone'] == self._curr_zone]

    def redraw(self):
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return

        pm = QtGui.QPixmap(w, h)
        pm.fill(QtGui.QColor('#111'))
        p  = QtGui.QPainter(pm)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        rows = self._rows()
        if not rows:
            p.setPen(QtGui.QColor('white'))
            p.drawText(pm.rect(), QtCore.Qt.AlignCenter, 'Выберите файл для просмотра.')
            p.end()
            self.setPixmap(pm)
            return

        xs   = np.array([r['X']         for r in rows])
        ys   = np.array([r['Y']         for r in rows])
        zs   = np.array([r['Z']         for r in rows])
        amps = np.array([r['Amplitude'] for r in rows])

        px, py, depth = project(
            xs, ys, zs, self._az, self._el, w, h, self._scale
        )

        self._hits = []
        for i in np.argsort(depth):
            color = amplitude_to_color(amps[i], self._power_min, self._power_max)
            cx, cy = int(px[i]), int(py[i])
            radius = 1.66 * self._scale

            p.setPen(QtCore.Qt.NoPen)
            p.setBrush(color)
            p.drawEllipse(int(cx - radius), int(cy - radius), int(2 * radius), int(2 * radius))
            self._hits.append((cx, cy, rows[i]))

        self._draw_axes(p, w, h)
        p.end()
        self.setPixmap(pm)

    def _draw_axes(self, p, w, h):
        origin = QtCore.QPointF(50, h - 50)
        az, el = np.radians(self._az), np.radians(self._el)

        def tip(dx, dy, dz):
            xr =  np.cos(az) * dx + np.sin(az) * dy
            yr = -np.sin(az) * dx + np.cos(az) * dy
            return QtCore.QPointF(
                origin.x() + xr * 30,
                origin.y() + (-np.sin(el) * dz + np.cos(el) * yr) * 30
            )

        for color, dx, dy, dz, label in [
            ('#f55', 1,0,0, 'X'), ('#5f5', 0,1,0, 'Y'), ('#55f', 0,0,1, 'Z')
        ]:
            end = tip(dx, dy, dz)
            p.setPen(QtGui.QPen(QtGui.QColor(color), 2))
            p.drawLine(origin, end)
            p.drawText(int(end.x()) + 2, int(end.y()) + 4, label)

    def resizeEvent(self, e):
        self.redraw()
        super().resizeEvent(e)

    def mousePressEvent(self, e):
        if e.button() != QtCore.Qt.LeftButton:
            return

        radius = 1.66 * self._scale
        best, row = (radius * 3) ** 2, None
        mx, my = e.x(), e.y()

        for cx, cy, r in self._hits:
            d = (cx-mx) ** 2 + (cy-my) ** 2
            if d < best:
                best, row = d, r
        if row:
            self.pointClicked.emit(row)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PreviewWindow(Canvas)
    window.show()
    app.exec_()
