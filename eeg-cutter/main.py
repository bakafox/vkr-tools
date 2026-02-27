from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem, QDialog
from PyQt5.QtCore import QTimer, QTime, Qt, pyqtSlot
from PyQt5 import QtCore, QtGui
import mne
import numpy as np
import sys
import csv

from qt_windows.front import Ui_MainWindow
from qt_windows.saveKnots import Ui_saveKnotsDialog
from widgets.MiniVoxelVisualizer import MiniVoxelVisualizer
from widgets.VoxelVisualizer import VoxelVisualizer
from widgets.EventsProcessing import TableDialog, TimeEditDelegate
from widgets.EventScrollBar import ScrollBarModified
from eeg_processor import LazyEEGProcessor


def time_str_to_int(time_str, freq=1):
    time = QTime.fromString(time_str, 'hh:mm:ss:zzz')

    return int(
        (((time.hour() * 24 + time.minute()) * 60 + time.second()) * 1000 + time.msec())
        * freq / 1000
    )

def time_int_to_str(time_int, freq=1):
    total = int(time_int * 1000 / freq)

    msec = total % 1000
    total //= 1000
    
    seconds = total % 60
    total //= 60

    minutes = total % 60
    hours = total // 60

    time = QTime(hours, minutes, seconds, msec)
    return time.toString('hh:mm:ss:zzz')


class SaveKnotDialog(QDialog, Ui_saveKnotsDialog):
    def __init__(self, time_now, time_max, freq, brainWidget, EEGProcessor):
        super().__init__()
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

        self.timeEnd = TimeEditDelegate(time_max, time_max, self)
        self.timeEnd.setGeometry(QtCore.QRect(310, 50, 100, 30))
        self.timeEnd.setFont(font)
        self.timeEnd.setAlignment(QtCore.Qt.AlignCenter)
        self.timeEnd.setObjectName('timeEnd')

        self.timeStart.textChanged.connect(self.rewise_frames_num)
        self.timeEnd.textChanged.connect(self.rewise_frames_num)
        self.windowSpin.valueChanged.connect(self.rewise_frames_num)
        self.strideSpin.valueChanged.connect(self.rewise_frames_num)

        self.saveZonesCheck.stateChanged.connect(self.rewise_file_size)
        self.comboBox.currentIndexChanged.connect(self.rewise_zones_in_use)

        self.all_active_zones = [i+1 for i in range(52)] # TODO: Расхардкодить вот это
        self.original_active_zones = self.brainWidget.active_zones
        self.brainWidget.active_zones = self.all_active_zones

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
            False,
            data,
            used_vertices,
            ampl=False
        )

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

        self.numFramesTotal.setText(f'{num_frames}')
        self.numFramesPS.setText(f'{self.freq / self.strideSpin.value()}')

        self.rewise_file_size()
    
    def precise_csv_size(self, points_num, num_frames, float_precision, int_max_digits):
        header_size = 20

        float_part = 4 * (1 + float_precision + 1 + 1)
        int_part = int_max_digits * self.saveZonesCheck.isChecked()
        row_size = float_part + int_part + 2
        total_size = header_size + num_frames * row_size * points_num + num_frames
        
        return total_size

    @pyqtSlot()
    def rewise_file_size(self):
        # int(self.numEntitiesAfter.text()) - num of frames
        # self.points_num                   - num of points in one frame
        
        file_size = self.precise_csv_size(
            self.points_num,
            int(self.numFramesTotal.text()),
            5.0,
            2.0
        )

        size_names = ['байт', 'Кбайт', 'Мбайт', 'Гбайт', 'Тбайт']
        sizes = [1, 1024, 1024**2, 1024**3, 1024**4]

        for i in range(1, len(sizes)):
            if file_size < sizes[i]:
                self.fileSize.setText(f'{file_size / sizes[i - 1]:.2f} {size_names[i - 1]}')
                return
        self.fileSize.setText(f'{file_size / sizes[4]:.2f} {size_names[4]}')
    
    @pyqtSlot()
    def cancel(self):
        self.brainWidget.active_zones = self.original_active_zones
        self.close()
    
    @pyqtSlot()
    def apply(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, 'Сохранение файла CSV', '.', '(*.csv);;All Files (*)'
        )
        if self.saveZonesCheck.isChecked():
            fields = ['Zone', 'X', 'Y', 'Z', 'Amplitude']
        else:
            fields = ['X', 'Y', 'Z', 'Amplitude']
        
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
                    vertex_data_masked = None

                    for j in range(
                        i - int(self.windowSpin.value() / 2),
                        i - int(self.windowSpin.value() / 2) + self.windowSpin.value()
                    ):
                        data, used_vertices = self.EEGProcessor[j]
                        _, vertex_data_masked = self.brainWidget.get_zones_data(
                            False,
                            data,
                            used_vertices,
                            self.saveZonesCheck.isChecked(),
                            False,
                            False,
                        )
                        _data.append(vertex_data_masked[:, 3])
                    
                    if vertex_data_masked is not None:
                        vertex_data_masked[:, 3] = np.average(_data, 0)
                        writer.writerows(vertex_data_masked)

        self.cancel()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('EEG-Cutter v26-02-26')

        # What am I doing with my life... I am so screwed... I am so doomed...

        self.freq = None
        self.events_array = None
        self.events_dict = None
        self.reverse_events_dict = None
        self.active_zones = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_parameters)
        self.timer.setInterval(int(1000 / 1))

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

        self.fpsSpinBox.valueChanged.connect(self.fps_change)

        self.amplitudeSpinBox.valueChanged.connect(self.amplitude_change)
        self.moduleCheckBox.clicked.connect(self.module_change)
        self.hideCheckBox.clicked.connect(self.hiding_change)

        self.setEvent.clicked.connect(self.startTableDialog)

        self.listZones.itemClicked.connect(self.show_zone_info)
        self.selectAll.clicked.connect(self.select_all)
        self.disselectAll.clicked.connect(self.disselect_all)

        self.saveKnots.clicked.connect(self.startSaveKnots)

        self.zone_descriptions = {
            1: 'Первичная соматосенсорная кора - обработка тактильной информации от тела',
            2: 'Вторичная соматосенсорная кора - интеграция тактильных ощущений',
            3: 'Первичная соматосенсорная кора (подзоны 3a и 3b) - обработка проприоцепции и тактильных сигналов',
            4: 'Первичная моторная кора - контроль произвольных движений',
            5: 'Ассоциативная соматосенсорная кора - интеграция сенсорной информации',
            6: 'Премоторная кора и дополнительная моторная область - планирование движений',
            7: 'Ассоциативная теменная кора - зрительно-пространственная обработка',
            8: 'Фронтальное глазное поле - контроль движений глаз',
            9: 'Дорсолатеральная префронтальная кора - рабочая память, исполнительные функции',
            10: 'Передняя префронтальная кора - сложные когнитивные функции, метапознание',
            11: 'Орбитофронтальная кора - принятие решений, социальное поведение',
            12: 'Орбитофронтальная кора (часть) - обработка социальной информации',
            13: 'Островковая доля (часть) - интероцепция, эмоциональная обработка',
            14: 'Островковая доля (передняя часть) - обоняние и вкус',
            15: 'Височная кора (передняя часть) - функции недостаточно изучены',
            16: 'Височная кора (часть) - функции недостаточно изучены',
            17: 'Первичная зрительная кора (V1) - обработка базовых зрительных сигналов',
            18: 'Вторичная зрительная кора (V2) - ранняя зрительная обработка',
            19: 'Ассоциативная зрительная кора (V3-V5) - сложная зрительная обработка',
            20: 'Нижняя височная кора - распознавание зрительных объектов',
            21: 'Средняя височная кора - обработка слуховой и зрительной информации',
            22: 'Верхняя височная кора (часть зоны Вернике) - понимание речи',
            23: 'Задняя поясная кора - часть лимбической системы, эмоции и память',
            24: 'Передняя поясная кора - когнитивный контроль, эмоциональная регуляция',
            25: 'Субгенуальная кора - регуляция настроения, депрессивные состояния',
            26: 'Ретросплениальная кора - пространственная память, навигация',
            27: 'Парагиппокампальная кора (передняя часть) - обонятельная обработка',
            28: 'Энторинальная кора - интерфейс между гиппокампом и неокортексом',
            29: 'Ретросплениальная кора (часть) - память и навигация',
            30: 'Ретросплениальная кора (часть) - память и навигация',
            31: 'Задняя поясная кора (дорсальная часть) - самореференциальная обработка',
            32: 'Дорсальная передняя поясная кора - когнитивный контроль, конфликт мониторинга',
            33: 'Прегенуальная поясная кора - эмоциональная регуляция',
            34: 'Парагиппокампальная кора (задняя часть) - обонятельная память',
            35: 'Периринальная кора - память и распознавание объектов',
            36: 'Парагиппокампальная кора - пространственная память и контекстуальная обработка',
            37: 'Затылочно-височная кора - распознавание лиц и объектов',
            38: 'Височный полюс - семантическая память, социальное познание',
            39: 'Угловая извилина - чтение, математические операции, семантическая обработка',
            40: 'Надкраевая извилина - фонологическая обработка, рабочая память',
            41: 'Первичная слуховая кора (A1) - обработка базовых слуховых сигналов',
            42: 'Вторичная слуховая кора - обработка сложных звуков',
            43: 'Операкулярная кора - вкусовая обработка',
            44: 'Зона Брока (передняя часть) - речевое производство',
            45: 'Зона Брока (задняя часть) - семантическая обработка речи',
            46: 'Дорсолатеральная префронтальная кора - рабочая память, когнитивная гибкость',
            47: 'Вентролатеральная префронтальная кора - семантическая обработка, контроль эмоций',
            48: 'Ретроинсулярная кора - слуховая и вестибулярная обработка',
            49: 'Парасубкулум - функции недостаточно изучены (есть только у приматов)',
            50: 'Пресубкулум - функции недостаточно изучены',
            51: 'Препириформная кора - обонятельная обработка',
            52: 'Параинсулярная кора - интеграция слуховой и соматосенсорной информации'
        }

        self.EEGProcessor = None

        try:
            self.load_file()
        except (OSError, FileNotFoundError):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                'Выбранный файл повреждён, имеет неверный формат или не имеет \n'
                + 'парного .fdt файла (у них должны быть одинаковые названия).'
            )
            sys.exit(msg.exec_())

    @pyqtSlot()
    def load_file(self):
        filepath = QFileDialog.getOpenFileName(
            self, 'Выберите файл записи ЭЭГ', '', '*.set'
        )[0]

        if filepath != None:
            print('\n=== Идёт загрузка файла, подождите... ===\n')

            try:
                self.raw = mne.io.read_raw_eeglab(filepath, preload=True)
            except TypeError:
                self.raw = mne.io.read_epochs_eeglab(filepath, preload=True)

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

                    self.EEGProcessor = LazyEEGProcessor(filepath, bad_channels)
                
                else:
                    [print(f'\n=== Координаты в этом файле ЭЭГ не были распознаны. Here be dragons! ===\n')]

                    self.EEGProcessor = LazyEEGProcessor(filepath, [])
            
            else:
                self.EEGProcessor = LazyEEGProcessor(filepath, [])
            
            print('\n=== Загрузка файла завершена. ===\n')

            data, used_vertices = self.EEGProcessor[0]
            self.brainWidget.brodmann_texture = self.EEGProcessor.brodmann_texture
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

            self.events_array, self.events_dict = self.EEGProcessor.get_events()
            self.events_array = self.events_array.tolist()
            self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}

            self.timeEdit.timeChanged.connect(self.set_time)

            # TODO: Возможны проблемы с максимумом времени, надо как-то пофиксить
            time = int(self.len_frames / self.freq * 1000)
            time = QTime(
                (((time // 1000) // 60) // 60) % 24,
                ((time // 1000) // 60) % 60,
                (time // 1000) % 60,
                time % 1000
            )

            self.init_horizontalscrollbar()
            self.update_event_text()

    def init_horizontalscrollbar(self):
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
        self.update_zones_list()
    
    @pyqtSlot()
    def YZScrollBar_slide(self):
        self.YZBrain.slider_frame(self.YZScrollBar.value())

    @pyqtSlot()
    def XZScrollBar_slide(self):
        self.XZBrain.slider_frame(self.XZScrollBar.value())

    @pyqtSlot()
    def XYScrollBar_slide(self):
        self.XYBrain.slider_frame(self.XYScrollBar.value())

    @pyqtSlot()
    def fps_change(self):
        self.timer.setInterval(int(1000 / self.fpsSpinBox.value()))
    
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
        time = int(self.horizontalScrollBar.value() / self.freq * 1000)

        time = QTime(
            (((time // 1000) // 60) // 60) % 24,
            ((time // 1000) // 60) % 60,
            (time // 1000) % 60,
            time % 1000
        )

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
        time = self.timeEdit.time()
        frame_index = int(
            (((time.hour() * 24 + time.minute()) * 60 + time.second()) * 1000 + time.msec())
            * self.freq / 1000
        )
        self.horizontalScrollBar.setValue(frame_index)

    @pyqtSlot()
    def module_change(self):
        self.brainWidget.moduleVar = self.moduleCheckBox.isChecked()
        self.brainWidget.update()
        self.brainWidget.update_buffers()
        self.update_zones_list()
    
    @pyqtSlot()
    def amplitude_change(self):
        self.brainWidget.amplitudeVar = self.amplitudeSpinBox.value()
        self.brainWidget.update()
        self.brainWidget.update_buffers()
        self.update_zones_list()
    
    @pyqtSlot()
    def hiding_change(self):
        self.brainWidget.hidePoints = self.hideCheckBox.isChecked()
        self.brainWidget.update()
    
    def update_parameters(self):
        if self.horizontalScrollBar.value() < self.horizontalScrollBar.maximum():
            self.nextButton_on_click()
        else:
            self.timer.stop()

    @pyqtSlot(int)
    def set_event(self, value):
        self.horizontalScrollBar.setValue(value)

    @pyqtSlot(dict)
    def dict_update(self, value):
        self.events_dict = value
        self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}
    
    @pyqtSlot(list)
    def events_update(self, value):
        self.events_array = value
        self.horizontalScrollBar.set_data(self.len_frames, value)

    def zone_change(self, item):
        self.active_zones = self.brainWidget.active_zones

        if len(item.text()[5::1]) > 2:
            number = 0
        else:
            number = int(item.text()[5::1])
        
        if number in self.active_zones:
            self.active_zones.remove(number)
        else:
            self.active_zones.append(number)
        
        self.brainWidget.active_zones = self.active_zones
        self.brainWidget.update_buffers()
        self.brainWidget.update()

    @pyqtSlot()
    def select_all(self):
        self.listZones.blockSignals(True)

        for index in range(self.listZones.count()):
            if (self.listZones.item(index).flags() & Qt.ItemFlag.ItemIsEnabled):
                self.listZones.item(index).setCheckState(Qt.Checked)
        
        self.listZones.blockSignals(False)

        self.active_zones = [i+1 for i in range(52)] # TODO: Расхардкодить вот это
        self.brainWidget.active_zones = self.active_zones
        self.brainWidget.update_buffers()
        self.brainWidget.update()
    
    @pyqtSlot()
    def disselect_all(self):
        self.listZones.blockSignals(True)

        for index in range(self.listZones.count()):
            if (self.listZones.item(index).flags() & Qt.ItemFlag.ItemIsEnabled):
                self.listZones.item(index).setCheckState(Qt.Unchecked)

        self.listZones.blockSignals(False)
        
        self.active_zones = []
        self.brainWidget.active_zones = self.active_zones
        self.brainWidget.update_buffers()
        self.brainWidget.update()

    def update_zones_list(self):
        active_zones = self.brainWidget.active_zones
        self.listZones.clear()
        availale_zones = list(map(lambda x: int(x), active_zones))
        
        for zone_id in [i+1 for i in range(52)]: # TODO: Расхардкодить вот это
            item = QListWidgetItem(f'Зона {zone_id}')
            item.setData(1, zone_id)

            if (zone_id in availale_zones):
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.Checked)
            else:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)

            self.listZones.addItem(item)
    
    def show_zone_info(self, item):
        zone_id = item.data(1)
        description = self.zone_descriptions.get(zone_id, 'Информация о зоне отсутствует')
        info_text = f'=== Зона {zone_id} ===\n\n{description}'
        
        self.zoneInfo.setPlainText(info_text)

    @pyqtSlot()
    def startTableDialog(self):
        dialog = TableDialog(
            self.horizontalScrollBar.colors,
            self.events_array,
            self.events_dict,
            self.reverse_events_dict,
            self.freq,
            self.len_frames,
            self
        )

        dialog.colors_selected.connect(self.horizontalScrollBar.set_colors)
        dialog.frame_selected.connect(self.set_event)
        dialog.dict_updated.connect(self.dict_update)
        dialog.events_updated.connect(self.events_update)

        dialog.exec_()
    
    @pyqtSlot()
    def startSaveKnots(self):
        dialog = SaveKnotDialog(
            self.timeEdit.time().toString('hh:mm:ss:zzz'),
            time_int_to_str(self.horizontalScrollBar.maximum(), self.freq),
            self.freq,
            self.brainWidget,
            self.EEGProcessor
        )
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
