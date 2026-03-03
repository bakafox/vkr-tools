from PyQt5.QtWidgets import QScrollBar, QStyle, QStyleOptionSlider
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QColor
from PyQt5 import QtCore


class ScrollBarModified(QScrollBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setGeometry(QtCore.QRect(10, 650, 1420, 40))
        self.setPageStep(1)
        self.setOrientation(Qt.Horizontal)
        self.setObjectName("horizontalScrollBar")
        self.full_len = None
        self.events_array = None
        self.colors = None

        self.setMinimum(0)

    def set_data(self, full_len, events_array):
        self.full_len = full_len
        self.events_array = events_array
        self.setMaximum(max(0, self.full_len))

        if isinstance(self.colors, type(None)):
            self.colors = [QColor(0,0,0) for i in events_array]

        self.update()

    @pyqtSlot(list)
    def set_colors(self, new_colors):
        self.colors = new_colors

    def paintEvent(self, event):
        super().paintEvent(event)

        if not isinstance(self.full_len, type(None)) and not isinstance(self.events_array, type(None)) and not isinstance(self.colors, type(None)):
            painter = QPainter(self)

            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            rect = self.style().subControlRect(QStyle.CC_ScrollBar, opt, QStyle.SC_ScrollBarGroove, self)

            width = rect.width()
            height = rect.height()

            start_x = rect.x()
            width = width - rect.x()

            # Можно для одинаковых ивентов установить одинаковые цвета, используй
            #                   self.color[self.events_array[i, 2]]

            # for frame_dot in self.events_array[:, 0]:
            for i in range(len(self.events_array)):
                painter.setPen(self.colors[i])
                width_relative = int((self.events_array[i][0] / self.full_len) * width)
                painter.drawLine(start_x + width_relative, 0, start_x + width_relative, height)

            painter.end()
