from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5 import QtCore, QtGui
import numpy as np
import csv

from ui.SaveKnotsDialog import Ui_SaveKnotsDialog
from timeutil import time_int_to_str, time_str_to_int
from widgets.TimeEditDelegate import TimeEditDelegate
from windows.EventsTableDialog import EventsTableDialog


class SaveKnotsDialog(QDialog, Ui_SaveKnotsDialog):
    mode_updated = pyqtSignal(str)
    window_updated = pyqtSignal(int)
    stride_updated = pyqtSignal(int)
    criteria_updated = pyqtSignal(str)

    def __init__(
            self,
            time_now,
            time_max,
            freq,
            brainWidget,
            EEGProcessor,
            init_mode,
            init_window,
            init_stride,
            init_criteria,
            parent
        ):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Сохранение узлов ЭЭГ')

        self.freq = freq
        self.brainWidget = brainWidget
        self.EEGProcessor = EEGProcessor
        self.save_mode = init_mode
        self.frame_criteria = init_criteria
        self.last_path = None # Типа чтобы путь всего 1 раз задавать надо было

        self.all_zones = dict(map(lambda zn: (zn, True), self.parent().zones.keys()))
        self.original_zones = self.brainWidget.zones

        font = QtGui.QFont()
        font.setPointSize(12)
        self.timeStart = TimeEditDelegate(time_now, time_max, self)
        self.timeStart.setGeometry(QtCore.QRect(110, 50, 110, 30))
        self.timeStart.setFont(font)
        self.timeStart.setAlignment(QtCore.Qt.AlignCenter)
        self.timeStart.setObjectName('timeStart')
        self.timeStart.textChanged.connect(self.rewise_frames_num)
        self.timeEnd = TimeEditDelegate(time_max, time_max, self)
        self.timeEnd.setGeometry(QtCore.QRect(110, 90, 110, 30))
        self.timeEnd.setFont(font)
        self.timeEnd.setAlignment(QtCore.Qt.AlignCenter)
        self.timeEnd.setObjectName('timeEnd')
        self.timeEnd.textChanged.connect(self.rewise_frames_num)

        self.timeStartSetEventButton.clicked.connect(
            lambda: self.set_time_from_events_table(self.timeStart)
        )
        self.timeStartSetEnd5Button.clicked.connect(
            lambda: self.set_time_from_another_time(self.timeStart, self.timeEnd, -5)
        )
        self.timeStartSetEnd10Button.clicked.connect(
            lambda: self.set_time_from_another_time(self.timeStart, self.timeEnd, -10)
        )
        self.timeEndSetEventButton.clicked.connect(
            lambda: self.set_time_from_events_table(self.timeEnd)
        )
        self.timeEndSetStart5Button.clicked.connect(
            lambda: self.set_time_from_another_time(self.timeEnd, self.timeStart, +5)
        )
        self.timeEndSetStart10Button.clicked.connect(
            lambda: self.set_time_from_another_time(self.timeEnd, self.timeStart, +10)
        )

        self.saveMetadataCheck.stateChanged.connect(self.rewise_file_size)
        self.comboBox.currentIndexChanged.connect(self.rewise_zones_in_use)

        self.optionsContainer.setCurrentIndex(1 if self.save_mode == 'frame' else 0)
        self.optionsFrameRadio.toggled.connect(
            lambda c: self.set_save_mode('frame') if c else None
        )
        self.optionsFullRadio.toggled.connect(
            lambda c: self.set_save_mode('full') if c else None
        )

        self.windowSpin.setValue(init_window)
        self.windowSpin.valueChanged.connect(self.rewise_frames_num)
        self.strideSpin.setValue(init_stride)
        self.strideSpin.valueChanged.connect(self.rewise_frames_num)

        self.frameMaxRadio.setChecked(self.frame_criteria == 'max')
        self.frameMaxRadio.toggled.connect(
            lambda c: self.set_frame_criteria('max') if c else None
        )
        self.frameMinRadio.setChecked(self.frame_criteria == 'min')
        self.frameMinRadio.toggled.connect(
            lambda c: self.set_frame_criteria('min') if c else None
        )

        self.cancelButton.clicked.connect(self.cancel)
        self.saveButton.clicked.connect(self.apply)

        self.rewise_zones_in_use()
        self.rewise_frames_num()
    
    @pyqtSlot()
    def rewise_zones_in_use(self):
        if self.comboBox.currentIndex() == 1:
            self.brainWidget.zones = self.original_zones
        else:
            self.brainWidget.zones = self.all_zones

        data, used_vertices = self.EEGProcessor[0]
        self.points_num, _ = self.brainWidget.get_zones_data(
            data,
            used_vertices,
            False,
            False
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
            int((num_frames - 2 * int(self.windowSpin.value() / 2))
                / self.strideSpin.value())
        )

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
            1 if self.optionsContainer.currentIndex() == 1 else int(self.numFramesTotal.text()),
            8,
            2
        )

        size_names = ['байт', 'Кбайт', 'Мбайт', 'Гбайт', 'Тбайт']
        sizes = [1, 1024, 1024**2, 1024**3, 1024**4]

        for i in range(1, len(sizes)):
            if file_size < sizes[i]:
                self.fileInfo.setText(
                    f'Вес файла: {file_size / sizes[i - 1]:.2f} {size_names[i - 1]}'
                )
                return

    @pyqtSlot(str)
    def set_frame_criteria(self, new_criteria):
        self.frame_criteria = new_criteria
        self.criteria_updated.emit(new_criteria)

    @pyqtSlot(str)
    def set_save_mode(self, new_mode):
        self.save_mode = new_mode
        self.optionsContainer.setCurrentIndex(1 if new_mode == 'frame' else 0)
        self.mode_updated.emit(new_mode)
        self.rewise_file_size()

    @pyqtSlot()
    def set_time_from_another_time(self, widget_target, widget_source, delta_sec):
        time = (
            time_str_to_int(widget_source.text(), self.freq) + delta_sec * self.freq
        )
        widget_target.setText(time_int_to_str(time, self.freq))

    @pyqtSlot()
    def set_time_from_events_table(self, time_widget):
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
            lambda _, timestamp: time_widget.setText(timestamp)
        )

        dialog.colors_updated.connect(self.parent().horizontalScrollBar.set_colors)
        dialog.dict_updated.connect(self.parent().dict_update)
        dialog.events_updated.connect(self.parent().events_update)

        dialog.exec_()

    @pyqtSlot()
    def cancel(self):
        self.brainWidget.zones = self.original_zones
        self.close()

    def save_as_full(self, filename, fields):
        with open(filename, 'w', newline='') as file:
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
                data_with_zone = []

                for j in range(
                    i - int(self.windowSpin.value() / 2),
                    i - int(self.windowSpin.value() / 2) + self.windowSpin.value()
                ):
                    amplitudes, used_vertices = self.EEGProcessor[j]

                    _, data_with_zone = self.brainWidget.get_zones_data(
                        amplitudes,
                        used_vertices,
                        False,
                        self.saveMetadataCheck.isChecked()
                    )

                    _data.append(data_with_zone[:, 3])
                
                if len(data_with_zone) > 0:
                    data_with_zone[:, 3] = np.average(_data, 0)

                    if self.saveMetadataCheck.isChecked():
                        time_col = np.full((data_with_zone.shape[0], 1), i)
                        block_full = np.hstack((time_col, data_with_zone))
                    else:
                        block_full = data_with_zone

                    # Простое обрезание значений до 3-5 цифр после запятой
                    # позволяет уменьшить размер выходных данных во много раз!
                    block_compact = block_full.copy().astype(object)

                    for ci in range(block_full.shape[1]):
                        try:
                            block_compact[:, ci] = np.round(
                                block_full[:, ci].astype(float), 6
                            )
                        except (ValueError, TypeError):
                            pass
                    
                    writer.writerows(block_compact)

    def save_as_frame(self, filename, fields):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(fields)

            found_criteria = -1.0 if self.frame_criteria == 'max' else +1.0
            found_data = None
            found_timestamp = 0

            for i in range(
                time_str_to_int(self.timeStart.text(), self.freq),
                time_str_to_int(self.timeEnd.text(), self.freq)
            ):
                amplitudes, used_vertices = self.EEGProcessor[i]

                _, data_with_zone = self.brainWidget.get_zones_data(
                    amplitudes,
                    used_vertices,
                    False,
                    self.saveMetadataCheck.isChecked(),
                )

                criteria = float(np.mean(np.abs(amplitudes)))

                if (self.frame_criteria == 'max'):
                    # Максимальная средняя активация (по модулю) среди всех зон
                    found = criteria > found_criteria
                else:
                    # Минимальная средняя активация (по модулю) среди всех зон
                    found = criteria < found_criteria
                
                if found:
                    found_criteria = criteria
                    found_data = data_with_zone
                    found_timestamp = i

            if self.saveMetadataCheck.isChecked():
                time_col = np.full((found_data.shape[0], 1), found_timestamp)
                block_full = np.hstack((time_col, found_data))
            else:
                block_full = found_data
                
            # Простое обрезание значений до 3-5 цифр после запятой
            # позволяет уменьшить размер выходных данных во много раз!
            block_compact = block_full.copy().astype(object)

            for ci in range(block_full.shape[1]):
                try:
                    block_compact[:, ci] = np.round(
                        block_full[:, ci].astype(float), 6
                    )
                except (ValueError, TypeError):
                    pass
            
            writer.writerows(block_compact)

    @pyqtSlot()
    def apply(self):
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        self.fileInfo.setText('Сохранение…')

        filename = (
            f'./{self.timeStart.text().replace(':', '')}_'
            + f'{int(float(self.numFramesTotal.text())
                    / float(self.numFramesPS.text()) * 1000)}_'
            + (
                (f'{self.windowSpin.value()}_{self.strideSpin.value()}')
                if self.save_mode == 'full' else (f'f_{self.frame_criteria}')
            )
            + '.csv'
        )

        if not self.last_path:
            filepath, _ = QFileDialog.getSaveFileName(
                None,
                'Выберите место сохранения файлов',
                filename,
                '(*.csv);;All Files (*)'
            )
            if not filepath:
                self.rewise_file_size()
                self.saveButton.setEnabled(True)
                self.cancelButton.setEnabled(True)
                return

            self.last_path = Path(filepath).parent
            self.saveButton.setText('Сохранить')

        fields = ['X', 'Y', 'Z', 'Amplitude']
        if self.saveMetadataCheck.isChecked():
            fields = ['Time', 'Zone'] + fields

        if self.save_mode == 'full':
            self.save_as_full(str(self.last_path / filename), fields)
        else:
            self.save_as_frame(str(self.last_path / filename), fields)

        self.fileInfo.setText('Сохранено.')
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
