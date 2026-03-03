from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


# TODO: мб попытаться унаследовать этот класс от VoxelVisualizer, или
# более абстрактного класса, от которого будет наследоваться и VoxelVisualizer?
class MiniVoxelVisualizer(QOpenGLWidget):
    def __init__(self, direction, parent=None):
        super().__init__(parent)
        self.vertices = None                # Координаты вокселей
        self.frame = None                   # Значения активности вокселей
        self.direction = direction
        self.setMinimumSize(300, 300)

        self.object_rotations = [[-90, 0, 90], [-90, 0, 0], [0, 0, 90]]
        self.object_translations = [[0, -1], [0, -1], [0, 0]]

        self.object_translation = self.object_translations[self.direction]
        self.object_rotation = self.object_rotations[self.direction]
        self.object_scale = 1.0             # Масштаб объекта
        self.d = 0
        self.last_mouse_position = None
        
        self.maximum = 0
        self.windowBrain = 10

        self.moduleVar = 1
        self.amplitudeVar = 0

        self.heatmap_max = 7.0
    
    def add_vertices(self, vertices):
        self.vertices = vertices

        self.unique = sorted(np.unique(self.vertices[:, self.direction]))
        self.maximum = len(self.unique)

        # self.object_rotation = [0, 0]     # Углы поворота по осям X и Y
        self.object_translation = self.object_translations[self.direction]
        self.object_scale = 1.0             # Масштаб объекта
        self.d = 0
        self.last_mouse_position = None

        self.moduleVar = 1
        self.amplitudeVar = 0
        
        self.slice_vertices = self.vertices[(self.unique[self.d] <= self.vertices[:, self.direction]) & (self.vertices[:, self.direction] <= self.unique[self.d + self.windowBrain]),]

    def update_frame(self, frame):
        self.frame = frame
        self.update()
    
    def slider_frame(self, val):
        
        self.d = val
        
        self.slice_vertices = self.vertices[(self.unique[self.d] <= self.vertices[:, self.direction]) & (self.vertices[:, self.direction] <= self.unique[self.d + self.windowBrain]),]
        self.update()  # Запускаем перерисовку

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0) # Черный фон
        glEnable(GL_DEPTH_TEST) # Включение теста глубины
        glEnable(GL_POINT_SMOOTH) # Сглаживание точек
        glPointSize(5.0) # Размер точек

    def resizeGL(self, w, h):
        # Настройка области просмотра
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1, 1000)  # Перспективная проекция
        glMatrixMode(GL_MODELVIEW)
    
    def heatmapGL(self, value):
        value = max(-1, value / self.heatmap_max)
            
        if value <= 0.0:
            return 0.0, (1 + value)*1.0, -value*1.0, 1.0
        else:
            return value*1.0, (1-value)*1.0, 0.0, 1.0

    def paintGL(self):
        if self.frame is None:
            return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Очистка экрана

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -10.0)

        # Настройка камеры
        glTranslatef(self.object_translation[0], self.object_translation[1], 0.0)
        glScalef(self.object_scale, self.object_scale, self.object_scale)
        glRotatef(self.object_rotation[0], 1, 0, 0)  # Поворот вокруг оси X
        glRotatef(self.object_rotation[1], 0, 1, 0)  # Поворот вокруг оси Y
        glRotatef(self.object_rotation[2], 0, 0, 1)  # Поворот вокруг оси Z
        data = self.frame

        # Отрисовка вокселей
        glBegin(GL_POINTS)
        
        #s lice_vertices = self.vertices[(self.unique[self.d] <= self.vertices[:, self.direction]) & (self.vertices[:, self.direction] <= self.unique[self.d + self.windowBrain]),]

        for i, vertex in enumerate(self.slice_vertices):
            x, y, z = vertex
            value = data[i]  # Значение активности

            # Отрисовка всего мозга
            # #
            # glColor4f(value, value, value, 0.01)  # Цвет точки (градации серого)

            # # Отрисовка через "чёрные точки", внутри ничего не будет видно
            # # 
            # if self.moduleVar == 1:
            #     if abs(value) < abs(self.amplitudeVar):  # Меньше порогового значения
            #         value = 0
            # else:
            #     if self.amplitudeVar >= 0 and value < self.amplitudeVar:
            #         value = 0
            #     elif self.amplitudeVar < 0 and value >= self.amplitudeVar:
            #         value = 0
            # #
            # glColor4f(value, value, value, 0.01)
            # #
            # glVertex3f(x, y, z)

            # Отрисовка без "чёрных точек", тогда не будет видно их при окрашивании в разные цвета
            # XYScrollBar
            #if self.unique[self.d] <= vertex[self.direction] <= self.unique[self.d + self.windowBrain]:
            if self.moduleVar == 1:
                if abs(value) > abs(self.amplitudeVar):  # Меньше порогового значения
                    # glColor4f(value, value, value, 0.01)
                    glColor4f(*self.heatmapGL(value))
                    self.glVertex3f_xyz(x, y, z)
            else:
                if self.amplitudeVar >= 0 and value >= self.amplitudeVar:
                    # glColor4f(value, value, value, 0.01)
                    glColor4f(*self.heatmapGL(value))
                    self.glVertex3f_xyz(x, y, z)
                elif self.amplitudeVar < 0 and value < self.amplitudeVar:
                    # glColor4f(value, value, value, 0.01)
                    glColor4f(*self.heatmapGL(value))
                    self.glVertex3f_xyz(x, y, z)

        glEnd()
        glFlush()

    def glVertex3f_xyz(self, x, y, z):
        if self.direction == 0:
            glVertex3f(0, y, z)
        if self.direction == 1:
            glVertex3f(x, 0, z)
        if self.direction == 2:
            glVertex3f(x, y, 0)

    def draw_background(self):
        # Устанавливаем цвет очистки (R, G, B, A)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Очищаем буфер цвета (закрашивает весь экран)
        # Также полезно очистить буфер глубины (GL_DEPTH_BUFFER_BIT), 
        # чтобы новые объекты рисовались корректно
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши"""
        self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перемещения"""
        if event.buttons() == Qt.RightButton:  # Перемещение объекта
            delta = event.pos() - self.last_mouse_position
            self.object_translation[0] += delta.x() * 0.01
            self.object_translation[1] -= delta.y() * 0.01

        self.last_mouse_position = event.pos()
        self.update()

    def wheelEvent(self, event):
        """Обработка колесика мыши для масштабирования"""
        delta = event.angleDelta().y()
        self.object_scale += delta * 0.001
        self.object_scale = max(0.1, min(10.0, self.object_scale))  # Ограничение масштаба
        self.update()