from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QSlider, QStyleOptionSlider, QStyle, QApplication
from PyQt5.QtGui import QPainter, QColor

class DoubleSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._min_value = 0
        self._max_value = 100
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(0)
        self.setMaximum(100)
        self._pressed_control = QStyle.SC_None
        self._pressed_pos = None
        self._pressed_value = 0
        self._interval_color = QColor(100, 150, 255, 100) # Цвет интервала

    def setRange(self, min_value, max_value):
        self._min_value = min_value
        self._max_value = max_value
        self.update()

    def minValue(self):
        return self._min_value

    def maxValue(self):
        return self._max_value

    def setMinValue(self, value):
        self._min_value = min(value, self._max_value)
        self.update()

    def setMaxValue(self, value):
        self._max_value = max(value, self._min_value)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        # Рисуем интервал между ползунками
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        handle_width = self.style().pixelMetric(QStyle.PM_SliderLength, opt, self)
        min_pos = self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self._min_value, groove_rect.width() - handle_width)
        max_pos = self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self._max_value, groove_rect.width() - handle_width)
        interval_rect = QRect(min_pos, groove_rect.y(), max_pos - min_pos, groove_rect.height())
        painter.fillRect(interval_rect, self._interval_color)

        # Рисуем первый ползунок (минимум)
        opt.subControls = QStyle.SC_SliderHandle
        opt.sliderValue = self._min_value
        opt.sliderPosition = self._min_value
        self.style().drawComplexControl(QStyle.CC_Slider, opt, painter, self)

        # Рисуем второй ползунок (максимум)
        opt.sliderValue = self._max_value
        opt.sliderPosition = self._max_value
        self.style().drawComplexControl(QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        pos = event.pos()
        style = self.style()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        # Определяем, какой ползунок был нажат
        handle_rect_min = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        handle_rect_max = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        handle_rect_min.moveLeft(self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self._min_value, self.width() - handle_rect_min.width()))
        handle_rect_max.moveLeft(self.style().sliderPositionFromValue(self.minimum(), self.maximum(), self._max_value, self.width() - handle_rect_max.width()))

        if handle_rect_min.contains(pos):
            self._pressed_control = QStyle.SC_SliderHandle
            self._pressed_pos = pos
            self._pressed_value = self._min_value
        elif handle_rect_max.contains(pos):
            self._pressed_control = QStyle.SC_SliderHandle
            self._pressed_pos = pos
            self._pressed_value = self._max_value
        else:
            # Если клик был между ползунками, перемещаем ближайший ползунок
            mid_point = (handle_rect_min.center().x() + handle_rect_max.center().x()) / 2
            if pos.x() < mid_point:
                self._pressed_control = QStyle.SC_SliderHandle
                self._pressed_pos = pos
                self._pressed_value = self._min_value
            else:
                self._pressed_control = QStyle.SC_SliderHandle
                self._pressed_pos = pos
                self._pressed_value = self._max_value

    def mouseMoveEvent(self, event):
        if self._pressed_control == QStyle.SC_None:
            return

        pos = event.pos()
        distance = pos.x() - self._pressed_pos.x()
        value_range = self.maximum() - self.minimum()
        pixel_range = self.width() - self.style().pixelMetric(QStyle.PM_SliderLength, None, self)
        new_value = self._pressed_value + (distance * value_range) / pixel_range

        if self._pressed_value == self._min_value:
            self.setMinValue(int(new_value))
        elif self._pressed_value == self._max_value:
            self.setMaxValue(int(new_value))

        self._pressed_pos = pos
        self._pressed_value = new_value
        # self.valueChanged.emit(self._min_value, self._max_value)

    def mouseReleaseEvent(self, event):
        self._pressed_control = QStyle.SC_None
