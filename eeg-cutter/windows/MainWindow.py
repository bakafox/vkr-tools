from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer, QTime, pyqtSlot
from PyQt5 import QtCore
import mne
import numpy as np
import sys

from eeglproc import LazyEEGProcessor
from timeutil import time_int_to_str, time_str_to_int
from zoneutil import ZONE_NAMES
from ui.MainWindow import Ui_MainWindow
from widgets.MiniVoxelVisualizer import MiniVoxelVisualizer
from widgets.VoxelVisualizer import VoxelVisualizer
from widgets.EventScrollBar import ScrollBarModified
from windows.EventsTableDialog import EventsTableDialog
from windows.SaveKnotsDialog import SaveKnotsDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, win_title, use_cache):
        super().__init__()
        self.setupUi(self)

        self.use_cache = use_cache
        self.freq = None
        self.events_array = None
        self.events_dict = None
        self.reverse_events_dict = None

        self.last_used_mode = 'frame'
        self.last_used_window = 1
        self.last_used_stride = 1
        self.last_used_criteria = 'max'

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_parameters)
        self.timer.setInterval(16) # Примерно 60 кадров в секунду
        self.time_rem = 0.0

        self.YZBrain = MiniVoxelVisualizer(0, self.centralWidget_)
        self.YZBrain.setGeometry(QtCore.QRect(970, 10, 300, 300))
        self.YZBrain.setObjectName('YZBrain')

        self.XZBrain = MiniVoxelVisualizer(1, self.centralWidget_)
        self.XZBrain.setGeometry(QtCore.QRect(640, 10, 300, 300))
        self.XZBrain.setObjectName('XZBrain')

        self.XYBrain = MiniVoxelVisualizer(2, self.centralWidget_)
        self.XYBrain.setGeometry(QtCore.QRect(640, 320, 300, 300))
        self.XYBrain.setObjectName('XYBrain')

        self.brainWidget = VoxelVisualizer(
            self.YZBrain,
            self.XZBrain,
            self.XYBrain,
            self.pointInfo,
            self.centralWidget_
        )
        self.brainWidget.setGeometry(QtCore.QRect(10, 10, 600, 610))
        self.brainWidget.setObjectName('brainWidget')

        self.nextButton.clicked.connect(self.nextButton_on_click)
        self.previousButton.clicked.connect(self.prevButton_on_click)
        self.timeButton.clicked.connect(self.toggle_time)

        self.YZScrollBar.setMinimum(0)
        self.YZScrollBar.setMaximum(max(0, self.YZBrain.maximum - 1))
        self.YZScrollBar.valueChanged.connect(self.YZScrollBar_slide)

        self.XZScrollBar.setMinimum(0)
        self.XZScrollBar.setMaximum(max(0, self.XZBrain.maximum - 1))
        self.XZScrollBar.valueChanged.connect(self.XZScrollBar_slide)

        self.XYScrollBar.setMinimum(0)
        self.XYScrollBar.setMaximum(max(0, self.XYBrain.maximum - 1))
        self.XYScrollBar.valueChanged.connect(self.XYScrollBar_slide)

        # self.fpsSpinBox.valueChanged.connect(self.fps_change)

        self.amplitudeSpinBox.valueChanged.connect(self.amplitude_change)
        self.moduleCheckBox.clicked.connect(self.module_change)
        self.hideCheckBox.clicked.connect(self.hiding_change)

        self.setEvent.clicked.connect(self.start_events_table)

        self.saveKnots.clicked.connect(self.start_save_knots)

        self.zones = dict(map(lambda zn: (zn, True), ZONE_NAMES))
        self.zonesLfCheckButton.clicked.connect(lambda: self.toggle_zone('LF'))
        self.zonesMfCheckButton.clicked.connect(lambda: self.toggle_zone('MF'))
        self.zonesRfCheckButton.clicked.connect(lambda: self.toggle_zone('RF'))
        self.zonesLtCheckButton.clicked.connect(lambda: self.toggle_zone('LT'))
        self.zonesMcCheckButton.clicked.connect(lambda: self.toggle_zone('MC'))
        self.zonesRtCheckButton.clicked.connect(lambda: self.toggle_zone('RT'))
        self.zonesLpCheckButton.clicked.connect(lambda: self.toggle_zone('LP'))
        self.zonesMpCheckButton.clicked.connect(lambda: self.toggle_zone('MP'))
        self.zonesRpCheckButton.clicked.connect(lambda: self.toggle_zone('RP'))
        self.zonesSelButton.clicked.connect(lambda: self.toggle_all_zones(True))
        self.zonesUnselButton.clicked.connect(lambda: self.toggle_all_zones(False))

        self.EEGProcessor = None

        try:
            self.load_file(win_title)
        except (OSError, FileNotFoundError):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                'Выбранный файл повреждён, имеет неверный формат или не имеет \n'
                + 'парного .fdt файла (у них должны быть одинаковые названия).'
            )
            sys.exit(msg.exec_()) # ОТКЛЮЧИТЬ ДЛЯ ОТЛАДКИ ИНТЕРФЕЙСА

    @pyqtSlot()
    def load_file(self, win_title=''):
        path_eeg = QFileDialog.getOpenFileName(
            self, 'Выберите файл записи ЭЭГ', '', '*.set'
        )[0]
        
        path_zones = 'ANT128_roi.txt'
        try:
            _ = open(path_zones, 'r')
            _.close()
        except (OSError, FileNotFoundError):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                'Не удалось найти файл распределения каналов. Убедитесь, что \n'
                + f'он называется "{path_zones}" и находится в корне программы.'
            )
            sys.exit(msg.exec_()) # ОТКЛЮЧИТЬ ДЛЯ ОТЛАДКИ ИНТЕРФЕЙСА


        if path_eeg != None:
            print('\n=== Идёт загрузка файла, подождите... ===\n')

            try:
                self.raw = mne.io.read_raw_eeglab(path_eeg, preload=True)
            except TypeError:
                self.raw = mne.io.read_epochs_eeglab(path_eeg, preload=True)

            # Проверка координат в raw.info на NaN
            bad_channels = []
            for ch in self.raw.info['chs']:
                if ch['kind'] == mne.io.constants.FIFF.FIFFV_EEG_CH:
                    if np.any(np.isnan(ch['loc'][:3])):
                        bad_channels.append(ch['ch_name'])

            if bad_channels:
                if len(bad_channels) != len(self.raw.info['chs']):
                    print(f'\n=== Удаление каналов с некорректными координатами: ===')
                    print(f'{bad_channels}', '\n')
                    self.raw.drop_channels(bad_channels)

                    self.EEGProcessor = LazyEEGProcessor(
                        path_eeg,
                        path_zones,
                        bad_channels,
                        self.use_cache
                    )

                else:
                    print(f'\n=== Координаты в ЭЭГ не были распознаны. Here be dragons! ===\n')

                    self.EEGProcessor = LazyEEGProcessor(
                        path_eeg,
                        path_zones,
                        [],
                        self.use_cache,
                        use_std_coords=True
                    )

            else:
                self.EEGProcessor = LazyEEGProcessor(
                    path_eeg,
                    path_zones,
                    [],
                    self.use_cache
                )

            print('\n=== Загрузка файла завершена. ===\n')

            if (win_title):
                self.setWindowTitle(f'{win_title} :: {path_eeg.split('/')[-1]}')
            else:
                self.setWindowTitle(f'{path_eeg.split('/')[-1]}')

            data, used_vertices = self.EEGProcessor[0]
            self.brainWidget.zone_texture = self.EEGProcessor.zone_texture
            self.brainWidget.add_data(data, used_vertices)

            self.XYScrollBar.setMaximum(
                max(0, self.XYBrain.maximum - self.XYBrain.windowBrain - 1)
            )
            self.XZScrollBar.setMaximum(
                max(0, self.XZBrain.maximum - self.XZBrain.windowBrain - 1)
            )
            self.YZScrollBar.setMaximum(
                max(0, self.YZBrain.maximum - self.YZBrain.windowBrain - 1)
            )

            self.len_frames = self.EEGProcessor.get_frames_len()
            self.freq = self.EEGProcessor.get_freq()

            self.fpsSpinBox.setMaximum(int(self.freq))
            self.fpsSpinBox.setValue(int(self.freq / 10)) # = 0.1 сек реальной записи

            self.events_array, self.events_dict = self.EEGProcessor.get_events()
            self.events_array = self.events_array.tolist()
            self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}

            self.timeEdit.timeChanged.connect(self.set_time)

            self.horizontalScrollBar_init()
            self.update_event_text()

    def horizontalScrollBar_init(self):
        self.horizontalScrollBar = ScrollBarModified(self.centralWidget_)
        self.horizontalScrollBar.set_data(
            self.EEGProcessor.get_frames_len() - 1,
            self.events_array
        )

        self.horizontalScrollBar.valueChanged.connect(self.horizontalScrollBar_slide)

    @pyqtSlot()
    def nextButton_on_click(self):
        self.horizontalScrollBar.setValue(self.horizontalScrollBar.value() + 1)
    
    @pyqtSlot()
    def prevButton_on_click(self):
        self.horizontalScrollBar.setValue(self.horizontalScrollBar.value() - 1)
    
    @pyqtSlot()
    def horizontalScrollBar_slide(self):
        data, used_vertices = self.EEGProcessor[self.horizontalScrollBar.value()]
        self.brainWidget.slider_frame(data)

        self.update_time()
        self.update_event_text()
    
    @pyqtSlot()
    def YZScrollBar_slide(self):
        self.YZBrain.slider_frame(self.YZScrollBar.value())

    @pyqtSlot()
    def XZScrollBar_slide(self):
        self.XZBrain.slider_frame(self.XZScrollBar.value())

    @pyqtSlot()
    def XYScrollBar_slide(self):
        self.XYBrain.slider_frame(self.XYScrollBar.value())

    # @pyqtSlot()
    # def fps_change(self):
    #     self.timer.setInterval(int(1000 / self.fpsSpinBox.value()))

    @pyqtSlot()
    def toggle_zone(self, zone):
        self.zones[zone] = not self.zones[zone]

        self.brainWidget.zones = self.zones
        self.brainWidget.update_buffers()
        self.brainWidget.update()

    @pyqtSlot()
    def toggle_all_zones(self, bool):

        for zone in self.zones.keys():
            self.zones[zone] = bool

        self.zonesLfCheckButton.setChecked(bool)
        self.zonesMfCheckButton.setChecked(bool)
        self.zonesRfCheckButton.setChecked(bool)
        self.zonesLtCheckButton.setChecked(bool)
        self.zonesMcCheckButton.setChecked(bool)
        self.zonesRtCheckButton.setChecked(bool)
        self.zonesLpCheckButton.setChecked(bool)
        self.zonesMpCheckButton.setChecked(bool)
        self.zonesRpCheckButton.setChecked(bool)

        self.brainWidget.zones = self.zones
        self.brainWidget.update_buffers()
        self.brainWidget.update()

    @pyqtSlot()
    def toggle_time(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timeButton.setText('Старт')
        else:
            self.timer.start()
            self.timeButton.setText('Пауза')

    @pyqtSlot()
    def update_time(self):
        time_str = time_int_to_str(self.horizontalScrollBar.value(), self.freq)
        time = QTime.fromString(time_str, 'hh:mm:ss:zzz')
        self.timeEdit.setTime(time)

    def update_event_text(self):
        if (self.events_array and self.reverse_events_dict):
            for i in range(len(self.events_array) - 1):
                if (
                    self.events_array[i][0] <= self.horizontalScrollBar.value()
                    and self.horizontalScrollBar.value() <= self.events_array[i + 1][0]
                ):
                    self.eventText.setText(
                        f'Зона: {self.reverse_events_dict[self.events_array[i][2]]}'
                    )

    @pyqtSlot()
    def set_time(self):
        time_str = self.timeEdit.time().toString('hh:mm:ss:zzz')
        frame_index = time_str_to_int(time_str, self.freq)
        self.horizontalScrollBar.setValue(frame_index)

    @pyqtSlot()
    def module_change(self):
        self.brainWidget.moduleVar = self.moduleCheckBox.isChecked()
        self.brainWidget.update()
        self.brainWidget.update_buffers()
    
    @pyqtSlot()
    def amplitude_change(self):
        self.brainWidget.amplitudeVar = self.amplitudeSpinBox.value()
        self.brainWidget.update()
        self.brainWidget.update_buffers()
    
    @pyqtSlot()
    def hiding_change(self):
        self.brainWidget.hidePoints = self.hideCheckBox.isChecked()
        self.brainWidget.update()
    
    def update_parameters(self):
        # Таймер имеет частоту 60 ФПС, поэтому делис заявленный ФПС на 60:
        self.time_rem += self.fpsSpinBox.value() / 60

        if self.horizontalScrollBar.value() + self.time_rem < self.horizontalScrollBar.maximum():
            time_update = int(self.time_rem)

            if (time_update > 0):
                self.horizontalScrollBar.setValue(
                    self.horizontalScrollBar.value() + time_update
                )
                self.time_rem -= time_update
        else:
            self.timer.stop()
            self.time_rem = 0.0

    @pyqtSlot(dict)
    def dict_update(self, value):
        self.events_dict = value
        self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}

    @pyqtSlot(list)
    def events_update(self, value):
        self.events_array = value
        self.horizontalScrollBar.set_data(self.len_frames, value)

    @pyqtSlot()
    def start_events_table(self):
        dialog = EventsTableDialog(
            self.horizontalScrollBar.colors,
            self.events_array,
            self.events_dict,
            self.reverse_events_dict,
            self.freq,
            self.len_frames,
            'Перейти к выбранному событию',
            self
        )

        dialog.frame_selected.connect(
            lambda frame, _: self.horizontalScrollBar.setValue(frame)
        )

        dialog.colors_updated.connect(self.horizontalScrollBar.set_colors)
        dialog.dict_updated.connect(self.dict_update)
        dialog.events_updated.connect(self.events_update)

        dialog.exec_()

    @pyqtSlot()
    def start_save_knots(self):
        dialog = SaveKnotsDialog(
            self.timeEdit.time().toString('hh:mm:ss:zzz'),
            time_int_to_str(self.horizontalScrollBar.maximum(), self.freq),
            self.freq,
            self.brainWidget,
            self.EEGProcessor,
            self.last_used_mode,
            self.last_used_window,
            self.last_used_stride,
            self.last_used_criteria,
            self
        )

        dialog.mode_updated.connect(
            lambda mode: setattr(self, 'last_used_mode', mode)
        )
        dialog.window_updated.connect(
            lambda window: setattr(self, 'last_used_window', window)
        )
        dialog.stride_updated.connect(
            lambda stride: setattr(self, 'last_used_stride', stride)
        )
        dialog.criteria_updated.connect(
            lambda criteria: setattr(self, 'last_used_criteria', criteria)
        )

        dialog.exec_()
