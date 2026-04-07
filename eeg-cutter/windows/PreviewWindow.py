import os, csv
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog 

from ui.PreviewWindow import Ui_PreviewWindow
from zoneutil import ZONE_FULLNAMES


class PreviewWindow(QMainWindow, Ui_PreviewWindow):
    def __init__(self, new_canvas):
        super().__init__()
        self.setupUi(self)

        self._canvas = new_canvas(self.centralwidget)
        # self._canvas.setSizePolicy(
        #     QSizePolicy.Expanding,
        #     QSizePolicy.Expanding
        # )
        self.mainLayout.insertWidget(0, self._canvas)
        self.canvasLabel.hide()

        self._data = []
        self._power_min = 0.0
        self._power_max = 0.0

        self.btnBrowse.clicked.connect(self._browse)
        self.btnRotateCW.clicked.connect(lambda: self._rotation_changed(45))
        self.btnRotateCCW.clicked.connect(lambda: self._rotation_changed(-45))
        self.sliderElevation.sliderReleased.connect(self._elevation_changed)
        self.btnResetView.clicked.connect(self._reset_view)
        self.radioAllZones.toggled.connect(self._zone_changed)
        self.radioOneZone.toggled.connect(self._zone_changed)
        self.comboZone.currentIndexChanged.connect(self._zone_changed)
        self.sliderScale.sliderReleased.connect(self._scale_changed)
        self._canvas.pointClicked.connect(self._show_info)

        self._browse()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите экспортированный кадр ЭЭГ', '', '*.csv'
        )

        if path:
            self._load(path)

    def _load(self, path):
        data = []
        try:
            with open(path, newline='') as f:
                for row in csv.DictReader(f):
                    data.append({k: float(v) for k, v in row.items()})
        except Exception as ex:
            QMessageBox.critical(self, 'Критическая ошибка', str(ex)); return

        self._data = data
        powers = [r['Amplitude'] for r in data]
        self._power_min = min(powers)
        self._power_max = max(powers)

        zones = sorted(set(r['Zone'] for r in data))
        self.comboZone.blockSignals(True)
        self.comboZone.clear()
        for zone in zones:
            try:
                self.comboZone.addItem(ZONE_FULLNAMES[int(zone) - 1], userData=zone)
            except Exception:
                self.comboZone.addItem(str(zone), userData=zone)
        self.comboZone.blockSignals(False)

        self.lineEditFile.setText(os.path.basename(path))
        self.labelLegend.setText(
            f'СИН: {self._power_min:.2f} / ЗЕЛ: 0.00 / КРА: {self._power_max:.2f}'
        )

        self.radioAllZones.setChecked(True)
        self._refresh()

    def _zone_changed(self):
        self.comboZone.setEnabled(self.radioOneZone.isChecked())
        self._refresh()

    def _rotation_changed(self, deg):
        self._canvas.rotate(deg)
        self.labelRotation.setText(f'Поворот: {self._canvas._az} градусов')

    def _elevation_changed(self):
        self._canvas.set_elevation(self.sliderElevation.value())

    def _scale_changed(self):
        self.labelScale.setText(f'Масштаб: {self.sliderScale.value()} %')
        self._canvas.set_scale(self.sliderScale.value() / 100.0)

    def _reset_view(self):
        self.sliderElevation.setValue(20)
        self._elevation_changed()
        self.sliderScale.setValue(100)
        self._scale_changed()
        self._canvas.reset_view()
        self._rotation_changed(0)

    def _refresh(self):
        if not self._data:
            return

        zone = self.comboZone.currentData() if (
            self.radioOneZone.isChecked()
        ) else None
        self._canvas.set_curr_zone(zone)

        data = self._data if zone is None else (
            [r for r in self._data if r['Zone'] == zone]
        )
        self._canvas.set_data(data, self._power_min, self._power_max)

    def _show_info(self, row):
        self.textInfo.setPlainText(
            '\n'.join(f'{k}: {v}' for k, v in row.items()))
