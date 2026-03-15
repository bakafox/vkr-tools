from pathlib import Path

from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal

from process import cimg2qimg, get_cropped_img


class ImageCanvas(QLabel):
    cursorMoved = pyqtSignal(float, float)
    cursorClick = pyqtSignal(float, float, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pixmap: QPixmap | None = None
        self._zones: list[tuple[str, dict, QColor]] = []

    def set_image(self, img_path: Path):
        img = cimg2qimg(get_cropped_img(img_path))

        self._pixmap = QPixmap.fromImage(img)
        self.update()

    def set_zones(self, zones: list[tuple[str, dict, QColor]]):
        self._zones = zones
        self.update()

    def get_img_coords(self, mouse_x: float, mouse_y: float):
        if not self._pixmap or self._pixmap.isNull():
            return None

        widget_w, widget_h = self.width(), self.height()
        scaled = self._pixmap.scaled(
            widget_w, widget_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        ox = (widget_w - scaled.width()) // 2
        oy = (widget_h - scaled.height()) // 2
        ix = mouse_x - ox
        iy = mouse_y - oy
        iw, ih = scaled.width(), scaled.height()
        if not (0 <= ix <= iw and 0 <= iy <= ih):
            return None
        rel_x = ix / iw
        rel_y = iy / ih
        abs_x = round(rel_x * self._pixmap.width())
        abs_y = round(rel_y * self._pixmap.height())

        return abs_x, abs_y, rel_x, rel_y

    def mouseMoveEvent(self, event):
        self.cursorMoved.emit(
            event.position().x(),
            event.position().y()
        )
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() in [Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton]:
            self.cursorClick.emit(
                event.position().x(),
                event.position().y(),
                1 if event.button() == Qt.MouseButton.LeftButton else 2
            )
        super().mousePressEvent(event)
 
    def leaveEvent(self, event):
        self.cursorMoved.emit(-1.0, -1.0)
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._pixmap or self._pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        widget_w, widget_h = self.width(), self.height()
        scaled = self._pixmap.scaled(
            widget_w, widget_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        ox = (widget_w - scaled.width()) // 2
        oy = (widget_h - scaled.height()) // 2
        iw, ih = scaled.width(), scaled.height()
        painter.drawPixmap(ox, oy, scaled)

        pen_width = 2 # max(2, min(iw, ih) // 200)
        font_size = max(7, min(iw, ih) // 70)

        for name, coords, color in self._zones:
            x1_s = int(coords['x1'] * iw + ox)
            y1_s = int(coords['y1'] * ih + oy)
            x2_s = int(coords['x2'] * iw + ox)
            y2_s = int(coords['y2'] * ih + oy)

            border = QColor(color)
            painter.setPen(QPen(border, pen_width))
            painter.drawRect(x1_s, y1_s, x2_s - x1_s, y2_s - y1_s)

            painter.setFont(QFont('Sans', font_size, 700))
            painter.setPen(border)
            painter.drawText(x1_s - 2, y1_s - pen_width - 2, name)

        painter.end()
