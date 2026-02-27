from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QColorDialog, QLineEdit
from PyQt5.QtCore import Qt, pyqtSlot, QTime, pyqtSignal
from PyQt5.QtGui import QColor
from qt_windows.table import Ui_TableDialog
import numpy as np

# Цвета меток используются self.horizontalScrollBar (ScrollBarModified) и dialog.tableEvent (TableDialog)
#
# Словарь событий используют:
#
# TableDialog (отображение времени в таблице),
# ScrollBarModified (проставление временных меток),
# MainWindow (переход на временную метку)

class TimeEditDelegate(QLineEdit):
    def __init__(self, current_time, max_time, parent=None):
        super().__init__(parent)

        self.setInputMask("00:00:00:000")
        self.setPlaceholderText("00:00:00:000")
        self.setAlignment(Qt.AlignCenter)

        self.max_time = max_time
        self.textChanged.connect(self.on_text_changed)

        self.setText(current_time)

    @pyqtSlot(str)
    def on_text_changed(self, text):
        try:
            time = QTime.fromString(text, "hh:mm:ss:zzz")
            if time.isValid():
                if self.max_time < text:
                    text = self.max_time
                    self.setText(text)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('Неправильный формат времени')
                msg.setWindowTitle("Критическая ошибка")
                msg.exec_()

        except OSError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Неправильный формат времени')
            msg.setWindowTitle("Критическая ошибка")
            msg.exec_()


class TableDialog(QDialog, Ui_TableDialog):
    frame_selected = pyqtSignal(int)
    colors_selected = pyqtSignal(list)
    dict_updated = pyqtSignal(dict)
    events_updated = pyqtSignal(list)

    def __init__(self, colors, events_array, events_dict, reverse_events_dict, freq, max_len, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(700, 500)

        self.setWindowTitle("Выбор события")

        self.addButton.setFocusPolicy(Qt.NoFocus)
        self.acceptButton.setFocusPolicy(Qt.NoFocus)
        self.deleteButton.setFocusPolicy(Qt.NoFocus)

        self.events_array = events_array
        self.events_dict = events_dict
        self.reverse_events_dict = reverse_events_dict
        self.freq = freq
        self.colors = colors

        self.tableEvent.setRowCount(len(self.events_array))

        self.tableEvent.setColumnWidth(0, 120)
        self.tableEvent.setColumnWidth(3, 80)

        self.max_len = max_len
        self.max_time = self.time_int_to_str(self.max_len)

        for i in range(len(self.events_array)):
            time = self.time_int_to_str(self.events_array[i][0])
            item_time = TimeEditDelegate(time, self.max_time)
            item_time.editingFinished.connect(self.set_frame)

            item_frame = QTableWidgetItem()
            item_frame.setData(Qt.DisplayRole, self.events_array[i][0])

            color_item = QTableWidgetItem()
            color_item.setBackground(self.colors[i])
            color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)

            self.tableEvent.setItem(i, 0, item_frame)
            self.tableEvent.setCellWidget(i, 1, item_time)
            self.tableEvent.setItem(i, 2, QTableWidgetItem(self.reverse_events_dict[self.events_array[i][2]]))

            self.tableEvent.setItem(i, 3, color_item)

        self.acceptButton.clicked.connect(self.acceptClicked)

        self.tableEvent.cellDoubleClicked.connect(self.set_color_cell)

        self.tableEvent.cellChanged.connect(self.set_data)

        self.addButton.clicked.connect(self.add_row)
        self.deleteButton.clicked.connect(self.delete_row)

    @pyqtSlot()
    def acceptClicked(self):
        row = self.tableEvent.currentRow()
        if row != None:
            item = self.tableEvent.item(row, 0)

            if item:
                self.frame_selected.emit(item.data(Qt.DisplayRole))

                self.close()

    @pyqtSlot()
    def set_frame(self):
        row = self.tableEvent.currentRow()
        frame_item = self.tableEvent.item(row, 0)
        time_item = self.tableEvent.cellWidget(row, 1)

        frame_int = self.time_str_to_int(time_item.text())

        if time_item and frame_item:
            self.tableEvent.blockSignals(True)

            if frame_int in np.array(self.events_array)[:, 0]:
                time_item.setText(self.time_int_to_str(self.events_array[row][0]))
                self.tableEvent.blockSignals(False)
                return

            frame_item.setData(Qt.DisplayRole, frame_int)

            self.tableEvent.sortItems(0, Qt.AscendingOrder)
            self.tableEvent.blockSignals(False)

            # Сортировка массива
            self.events_array[row][0] = frame_int

            colors = [[i] for i in self.colors]
            for_sort = np.concatenate((self.events_array, colors), axis=1)
            for_split = np.array(sorted(for_sort.tolist(), key=lambda x: x[0]))
            self.events_array = for_split[:, 0:3].tolist()
            self.colors = for_split[:, 3].tolist()

    @pyqtSlot()
    def set_time(self):
        row = self.tableEvent.currentRow()
        frame_item = self.tableEvent.item(row, 0)
        time_item = self.tableEvent.cellWidget(row, 1)

        frame_int = frame_item.data(Qt.DisplayRole)

        if time_item and frame_item:
            self.tableEvent.blockSignals(True)

            if frame_int in np.array(self.events_array)[:, 0]:
                frame_item.setData(Qt.DisplayRole, self.events_array[row][0])
                self.tableEvent.blockSignals(False)
                return

            time_item.setText(self.time_int_to_str(frame_int))

            self.tableEvent.sortItems(0, Qt.AscendingOrder)
            self.tableEvent.blockSignals(False)

            # Сортировка массива
            self.events_array[row][0] = frame_int

            colors = [[i] for i in self.colors]
            for_sort = np.concatenate((self.events_array, colors), axis=1)
            for_split = np.array(sorted(for_sort.tolist(), key=lambda x: x[0]))
            self.events_array = for_split[:, 0:3].tolist()
            self.colors = for_split[:, 3].tolist()

    @pyqtSlot()
    def set_name(self):
        row = self.tableEvent.currentRow()
        name_item = self.tableEvent.item(row, 2)

        if name_item:
            name = name_item.text()

            if not name in self.events_dict.keys():
                self.events_dict[name] = max(self.reverse_events_dict.keys()) + 1
                self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}

            self.events_array[row][2] = self.events_dict[name]

    def set_data(self):
        column = self.tableEvent.currentColumn()
        if column == 0:
            self.set_time()
        elif column == 1:
            self.set_frame()
        elif column == 2:
            self.set_name()

    def add_row(self):
        self.tableEvent.blockSignals(True)

        if self.max_len == self.tableEvent.rowCount():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Невозможно создать ещё одну метку (на каждый кадр только одна метка)')
            msg.setWindowTitle("Критическая ошибка")
            msg.exec_()
            self.tableEvent.blockSignals(False)
            return

        row = self.tableEvent.rowCount()
        self.tableEvent.setRowCount(self.tableEvent.rowCount() + 1)

        frame = -1
        name = 'Name'

        events_int = np.array(self.events_array)[:, 0]

        for i in range(self.max_len):
            if i in events_int:
                continue
            else:
                frame = i
                break

        if not name in self.events_dict.keys():
            self.events_dict[name] = max(self.reverse_events_dict.keys()) + 1
            self.reverse_events_dict = {v: k for k, v in self.events_dict.items()}

        event = [frame, 0, self.events_dict[name]]

        self.events_array.append(event)
        self.colors.append(QColor(0, 0, 0))

        time = self.time_int_to_str(self.events_array[row][0])
        item_time = TimeEditDelegate(time, self.max_time)
        item_time.editingFinished.connect(self.set_frame)

        item_frame = QTableWidgetItem()
        item_frame.setData(Qt.DisplayRole, self.events_array[row][0])

        color_item = QTableWidgetItem()
        color_item.setBackground(self.colors[row])
        color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)

        self.tableEvent.setItem(row, 0, item_frame)
        self.tableEvent.setCellWidget(row, 1, item_time)
        self.tableEvent.setItem(row, 2, QTableWidgetItem(self.reverse_events_dict[self.events_array[row][2]]))

        self.tableEvent.setItem(row, 3, color_item)

        self.tableEvent.sortItems(0, Qt.AscendingOrder)

        colors = [[i] for i in self.colors]
        for_sort = np.concatenate((self.events_array, colors), axis=1)
        for_split = np.array(sorted(for_sort.tolist(), key=lambda x: x[0]))
        self.events_array = for_split[:, 0:3].tolist()
        self.colors = for_split[:, 3].tolist()

        self.tableEvent.blockSignals(False)

    def delete_row(self):
        self.tableEvent.blockSignals(True)
        row = self.tableEvent.currentRow()

        if self.tableEvent.rowCount() > 1:
            self.events_array = self.events_array[:row] + self.events_array[row + 1:]
            self.colors = self.colors[:row] + self.colors[row + 1:]
            self.tableEvent.removeRow(row)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Хотя бы одна строка должна остаться.')
            msg.setWindowTitle("Критическая ошибка")
            msg.exec_()

        self.tableEvent.blockSignals(False)

    @pyqtSlot(int, int)
    def set_color_cell(self, row, col):
        if col == 3:
            item = self.tableEvent.item(row, col)
            if item:
                color = QColorDialog.getColor()
                if color:
                    item.setBackground(color)
                    self.colors[row] = color

    def time_int_to_str(self, time):
        time = int(time / self.freq * 1000)
        return str((((time // 1000) // 60) // 60) % 24).zfill(2) + ':' + str(((time // 1000) // 60) % 60).zfill(
            2) + ':' + str((time // 1000) % 60).zfill(2) + ':' + str(time % 1000).zfill(3)

    def time_str_to_int(self, time):
        time = QTime.fromString(time, 'hh:mm:ss:zzz')
        return int((((time.hour() * 24 + time.minute()) * 60 + time.second()) * 1000 + time.msec()) * self.freq / 1000)

    def closeEvent(self, event):
        self.dict_updated.emit(self.events_dict)
        self.events_updated.emit(self.events_array)
        self.colors_selected.emit(self.colors)

        event.accept()
