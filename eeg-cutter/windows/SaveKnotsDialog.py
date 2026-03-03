from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore, QtGui
import numpy as np
import csv

from ui.saveKnots import Ui_saveKnotsDialog
from timeutil import time_int_to_str, time_str_to_int
from widgets.TimeEditDelegate import TimeEditDelegate
from windows.EventsTableDialog import EventsTableDialog


class SaveKnotsDialog(QDialog, Ui_saveKnotsDialog):
    window_updated = pyqtSignal(int)
    stride_updated = pyqtSignal(int)

    def __init__(
            self,
            time_now,
            time_max,
            freq,
            brainWidget,
            EEGProcessor,
            init_window,
            init_stride,
            parent
        ):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Сохранение узлов ЭЭГ')

        self.freq = freq
        self.brainWidget = brainWidget
        self.EEGProcessor = EEGProcessor

        font = QtGui.QFont()
        font.setPointSize(12)

        self.timeStart = TimeEditDelegate(time_now, time_max, self)
        self.timeStart.setGeometry(QtCore.QRect(120, 50, 100, 30))
        self.timeStart.setFont(font)
        self.timeStart.setAlignment(QtCore.Qt.AlignCenter)
        self.timeStart.setObjectName('timeStart')
        self.timeStart.textChanged.connect(self.rewise_frames_num)

        self.timeEnd = TimeEditDelegate(time_max, time_max, self)
        self.timeEnd.setGeometry(QtCore.QRect(120, 90, 100, 30))
        self.timeEnd.setFont(font)
        self.timeEnd.setAlignment(QtCore.Qt.AlignCenter)
        self.timeEnd.setObjectName('timeEnd')
        self.timeEnd.textChanged.connect(self.rewise_frames_num)

        self.windowSpin.setValue(init_window)
        self.windowSpin.valueChanged.connect(self.rewise_frames_num)
        self.strideSpin.setValue(init_stride)
        self.strideSpin.valueChanged.connect(self.rewise_frames_num)

        self.saveMetadataCheck.stateChanged.connect(self.rewise_file_size)
        self.comboBox.currentIndexChanged.connect(self.rewise_zones_in_use)

        self.all_active_zones = [i+1 for i in range(self.parent().zones_no)]
        self.original_active_zones = self.brainWidget.active_zones
        self.brainWidget.active_zones = self.all_active_zones

        self.timeStartSetEventButton.clicked.connect(
            lambda: self.time_from_events_table(self.timeStart)
        )
        self.timeStartSetEnd5Button.clicked.connect(
            lambda: self.time_from_another_time(self.timeStart, self.timeEnd, -5)
        )
        self.timeStartSetEnd10Button.clicked.connect(
            lambda: self.time_from_another_time(self.timeStart, self.timeEnd, -10)
        )
        self.timeEndSetEventButton.clicked.connect(
            lambda: self.time_from_events_table(self.timeEnd)
        )
        self.timeEndSetStart5Button.clicked.connect(
            lambda: self.time_from_another_time(self.timeEnd, self.timeStart, +5)
        )
        self.timeEndSetStart10Button.clicked.connect(
            lambda: self.time_from_another_time(self.timeEnd, self.timeStart, +10)
        )

        self.cancelButton.clicked.connect(self.cancel)
        self.saveButton.clicked.connect(self.apply)

        self.rewise_zones_in_use()
    
    @pyqtSlot()
    def rewise_zones_in_use(self):
        if self.comboBox.currentIndex() == 1:
            self.brainWidget.active_zones = self.original_active_zones
        else:
            self.brainWidget.active_zones = self.all_active_zones

        data, used_vertices = self.EEGProcessor[0]
        self.points_num, _ = self.brainWidget.get_zones_data(
            data,
            used_vertices,
            ampl=False
        )

        print(f'\n=== Число точек: {self.points_num}. ===\n')

        self.rewise_file_size()
    
    @pyqtSlot()
    def rewise_frames_num(self):
        # Кадры ДО прохода шагающих окном
        num_frames = max(
            0,
            time_str_to_int(self.timeEnd.text(), self.freq)
            - time_str_to_int(self.timeStart.text(), self.freq)
        )

        self.windowSpin.setMaximum(max(1, num_frames))
        self.strideSpin.setMaximum(max(1, num_frames))

        # Кадры ПОСЛЕ прохода шагающих окном
        num_frames = max(
            0,
            int(
                (num_frames - 2 * int(self.windowSpin.value() / 2))
                / self.strideSpin.value()
            )
        )

        # Сохраняем размеры окна и шага, потому что почему бы и нет
        self.window_updated.emit(int(self.windowSpin.value()))
        self.stride_updated.emit(int(self.strideSpin.value()))

        self.numFramesTotal.setText(f'{num_frames}')
        self.numFramesPS.setText(f'{self.freq / self.strideSpin.value()}')

        self.rewise_file_size()
    
    def precise_csv_size(self, points_num, num_frames, float_precision, int_max_digits):
        header_size = 25 if self.saveMetadataCheck.isChecked() else 15
        float_part = 4 * (1 + float_precision + 1 + 1)
        int_part = int_max_digits * self.saveMetadataCheck.isChecked()
        row_size = float_part + int_part + 2
        
        total_size = header_size + num_frames * row_size * points_num + num_frames
        return total_size

    @pyqtSlot()
    def rewise_file_size(self):
        file_size = self.precise_csv_size(
            self.points_num,
            int(self.numFramesTotal.text()),
            19,
            2
        )

        size_names = ['байт', 'Кбайт', 'Мбайт', 'Гбайт', 'Тбайт']
        sizes = [1, 1024, 1024**2, 1024**3, 1024**4]

        for i in range(1, len(sizes)):
            if file_size < sizes[i]:
                self.fileSize.setText(
                    f'{file_size / sizes[i - 1]:.2f} {size_names[i - 1]}'
                )
                return
        self.fileSize.setText(
            f'{file_size / sizes[4]:.2f} {size_names[4]}'
        )

    def set_time(self, value, time_widget):
        time_widget.setText(value)
    
    @pyqtSlot()
    def time_from_another_time(self, widget_target, widget_source, delta_sec):
        time = (
            time_str_to_int(widget_source.text(), self.freq) + delta_sec * self.freq
        )
        widget_target.setText(time_int_to_str(time, self.freq))

    @pyqtSlot()
    def time_from_events_table(self, time_widget):
        dialog = EventsTableDialog(
            self.parent().horizontalScrollBar.colors,
            self.parent().events_array,
            self.parent().events_dict,
            self.parent().reverse_events_dict,
            self.parent().freq,
            self.parent().len_frames,
            'Использовать время события',
            self
        )

        dialog.frame_selected.connect(
            lambda _, timestamp: self.set_time(timestamp, time_widget)
        )

        dialog.colors_updated.connect(self.parent().horizontalScrollBar.set_colors)
        dialog.dict_updated.connect(self.parent().dict_update)
        dialog.events_updated.connect(self.parent().events_update)

        dialog.exec_()

    @pyqtSlot()
    def cancel(self):
        self.brainWidget.active_zones = self.original_active_zones
        self.close()
    
    @pyqtSlot()
    def apply(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            'Сохранение файла CSV',
            f'./{self.timeStart.text().replace(':', '')}_'
            + f'{int(float(self.numFramesTotal.text())
                  / float(self.numFramesPS.text()) * 1000)}_'
            + f'{self.windowSpin.value()}_{self.strideSpin.value()}',
            '(*.csv);;All Files (*)'
        )

        fields = ['X', 'Y', 'Z', 'Amplitude']
        if self.saveMetadataCheck.isChecked():
            fields = ['Time', 'Zone'] + fields

        if filename:
            with open(f'{filename}.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(fields)

                for i in range(
                    time_str_to_int(self.timeStart.text(), self.freq)
                        + int(self.windowSpin.value() / 2),
                    time_str_to_int(self.timeEnd.text(), self.freq)
                        - int(self.windowSpin.value() / 2),
                    self.strideSpin.value()
                ):
                    _data = []
                    vertex_data_masked = []

                    for j in range(
                        i - int(self.windowSpin.value() / 2),
                        i - int(self.windowSpin.value() / 2) + self.windowSpin.value()
                    ):
                        data, used_vertices = self.EEGProcessor[j]
                        _, vertex_data_masked = self.brainWidget.get_zones_data(
                            data,
                            used_vertices,
                            include_zones=self.saveMetadataCheck.isChecked(),
                            ampl=False
                        )
                        _data.append(vertex_data_masked[:, 3])
                    
                    if len(vertex_data_masked) > 0:
                        vertex_data_masked[:, 3] = np.average(_data, 0)

                        if self.saveMetadataCheck.isChecked():
                            time_col = np.full((vertex_data_masked.shape[0], 1), i)
                            full_block = np.hstack((time_col, vertex_data_masked))
                            writer.writerows(full_block)
                        else:
                            writer.writerows(vertex_data_masked)

