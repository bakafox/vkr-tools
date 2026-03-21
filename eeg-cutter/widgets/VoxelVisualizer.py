from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from OpenGL.GLU import *
import numpy as np
from numpy.linalg import inv

from zoneutil import get_zone_name, ZONE_NAMES


def screen_pos_to_ray(x, y, width, height, view_matrix, projection_matrix):
    # Нормализованные координаты устройства (NDC)
    ndc_x = (2.0 * x) / width - 1.0
    ndc_y = (2.0 * y) / height - 1.0

    # Обратная проекция
    inv_proj = inv(projection_matrix)

    # Точка на ближней плоскости (z = -1)
    near_point = np.array([ndc_x, ndc_y, -1.0, 1.0])
    near_eye = inv_proj @ near_point
    near_eye /= near_eye[3]

    # Точка на дальней плоскости (z = 1)
    far_point = np.array([ndc_x, ndc_y, 0.0, 1.0])
    far_eye = inv_proj @ far_point
    far_eye /= far_eye[3]

    # Обратное преобразование вида
    inv_view = inv(view_matrix.T)

    # Преобразование в мировые координаты
    near_world = inv_view @ near_eye
    far_world = inv_view @ far_eye
    near_world /= near_world[3]
    far_world /= far_world[3]

    # Направление луча
    ray_dir = far_world[:3] - near_world[:3]
    ray_dir = ray_dir / np.linalg.norm(ray_dir)

    return near_world[:3], ray_dir


def find_intersected_point(cam_pos, ray_dir, vertices, point_radius=0.01):
    if len(vertices) == 0:
        return -1

    # Вектор от камеры к вершинам
    cam_to_vertices = vertices - cam_pos

    # Расстояние вдоль луча
    dist_along_ray = np.dot(cam_to_vertices, ray_dir)

    # Ближайшие точки на луче
    points_on_ray = cam_pos + dist_along_ray[:, np.newaxis] * ray_dir

    # Расстояния до вершин
    distances = np.linalg.norm(points_on_ray - vertices, axis=1)

    # Фильтр точек перед камерой в радиусе
    valid_mask = (dist_along_ray > 0) & (distances < point_radius)
    valid_indices = np.where(valid_mask)[0]

    if len(valid_indices) == 0:
        return -1

    # Ближайшая точка
    closest_idx = valid_indices[np.argmin(dist_along_ray[valid_mask])]
    return closest_idx


vertex_shader = """
#version 330 core
layout(location = 0) in float zone_id;
layout(location = 1) in vec3 position;
layout(location = 2) in float value;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform int moduleVar;
uniform bool hidePoints;
uniform float amplitudeVar;
uniform float heatmap_max;
uniform bool active_zones[10]; // 0 = unassigned, 1-9 = LF..RP

out vec4 color;

vec4 heatmap(float val, float alp) {
    val = val / heatmap_max;

    if (val < -1) {
        val = -1;
    }

    if (val <= 0.0) {
        return vec4(0.0, (1+val)*1.0*alp, -val*1.0*alp, 1.0);
    }
    else {
        return vec4(val*1.0*alp, (1-val)*1.0*alp, 0.0, 1.0);
    }
}

void main() {
    bool zone_active = active_zones[int(zone_id)];

    bool condition;
    if (moduleVar == 1) {
        condition = abs(value) > abs(amplitudeVar);
    } else {
        if (amplitudeVar >= 0.0) {
            condition = value >= amplitudeVar;
        } else {
            condition = value < amplitudeVar;
        }
    }

    gl_Position = projection * view * model * vec4(position, 1.0);

    if (!zone_active) {
        gl_Position = vec4(-2.0, -2.0, -2.0, 1.0);
        gl_PointSize = 0.0;
    } else if (hidePoints && !condition) {
        gl_Position = vec4(-2.0, -2.0, -2.0, 1.0);
        gl_PointSize = 0.0;
    } else if (!condition) {
        color = heatmap(value, 0.3); // Прозрачность 70%
        gl_PointSize = 4.0;
    } else {
        color = heatmap(value, 1.0);
        gl_PointSize = 6.0; // 8.0;
    }
}
"""


fragment_shader = """
#version 330 core
in vec4 color;
out vec4 frag_color;

void main() {
    frag_color = color;
}
"""


class VoxelVisualizer(QOpenGLWidget):
    def __init__(self, YZBrain, XZBrain, XYBrain, pointInfo, parent=None):
        super().__init__(parent)
        self.points = None
        self.vertices = None             # Координаты вокселей
        self.data = None                 # Значения активности вокселей
        self.object_rotation = [0, 0]    # Углы поворота по осям X и Y
        self.object_translation = [0, 0] # Смещение по осям X и Y
        self.object_scale = 1.0          # Масштаб объекта
        self.last_mouse_position = None

        self.flag_s = 0

        self.moduleVar = 1
        self.amplitudeVar = 0
        self.hidePoints = 0

        self.heatmap_max = 7.0
        self.colors = None

        self.pointInfo = pointInfo
        self.miniBrains = [YZBrain, XZBrain, XYBrain]

        self.shader_program = None
        self.vao = None
        self.vbo = None
        self.vbo_alphas = None
        self.ebo = None
        self.vertex_count = 0

        # Матрицы
        self.projection = np.eye(4, dtype=np.float32)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)

        self.zone_texture = None
        self.debug_ray = None    # ОТЛАДКА
        self.selected_point = -1 # Индекс выбранной точки
    
    def add_data(self, data, vertices):
        self.data = data
        self.vertices = vertices
        self.colors = np.zeros((len(self.vertices), 4))

        self.object_rotation = [0, 0]    # Поворот по осям X и Y
        self.object_translation = [0, 0] # Смещение по осям X и Y
        self.object_scale = 0.1          # Масштаб объекта
        self.last_mouse_position = None

        self.moduleVar = 1
        self.amplitudeVar = 0

        for miniBrain in self.miniBrains:
            miniBrain.add_vertices(self.vertices)
            miniBrain.update_frame(self.data)

        self.update()

    def slider_frame(self, data):
        self.data = data

        for miniBrain in self.miniBrains:
            miniBrain.update_frame(self.data)

        self.update_buffers()
        self.update()

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0) # Чёрный фон для стирания

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SMOOTH) # Сглаживание точек

        self.zones = {name: True for name in ZONE_NAMES}

        # Компиляция шейдеров
        self.shader_program = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )

        # Создание буферов
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # self.vbo_alphas = glGenBuffers(1)
        # glBindBuffer(GL_ARRAY_BUFFER, self.vbo_alphas)

        # Настройка атрибутов
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0) # ID зоны
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(4))
        glEnableVertexAttribArray(1) # Координаты
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(16))
        glEnableVertexAttribArray(2) # Амплитуда
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.update_buffers()

    def get_zones_data(
            self,
            data,
            vertices,
            amp_thres,
            add_z_ids,
        ):
        if data is None:
            data = self.data
        if vertices is None:
            vertices = self.vertices

        if self.vertices is None or self.data is None:
            return 0, None

        if amp_thres:
            active_idx = np.unique(self.zone_texture[data > self.amplitudeVar])
            self.zones = {name: (i+1) in active_idx for i, name in enumerate(ZONE_NAMES)}

        # if not self.flag_s:
        #     np.save('zones.npy', self.zone_texture)
        #     np.save('vertices.npy', self.vertices)
        #     self.flag_s = 1

        active_idx = [i+1 for i, name in enumerate(ZONE_NAMES) if self.zones[name]]
        mask = np.isin(self.zone_texture, active_idx)

        if add_z_ids:
            vertex_data = np.hstack([
                self.zone_texture[mask, np.newaxis], # ID зоны
                vertices[mask],                      # Координаты
                data[mask, np.newaxis]               # Алмплитуда
            ]).astype(np.float32)
        else:
            vertex_data = np.hstack([
                vertices[mask],        # Координаты
                data[mask, np.newaxis] # Амплитуда
            ]).astype(np.float32)

        return len(vertices[mask]), vertex_data

    def update_buffers(self):
        if self.vertices is None or self.data is None or self.zone_texture is None:
            return

        vertex_count, vertex_data = self.get_zones_data(
            None,
            None,
            False,
            True
        )
        self.vertex_count = vertex_count # len(self.vertices)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_DYNAMIC_DRAW)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        if self.selected_point != -1:
            point = self.vertices[self.selected_point]

            self.pointInfo.setText(
                f'=== Информация о точке № {self.selected_point} ===\n'
                + f'X: {point[0]:7.4f} \tY: {point[1]:7.4f} \tZ: {point[2]:7.4f}\n'
                + f'Область: {get_zone_name(self.zone_texture[self.selected_point])}\n'
                + f'Амплитуда: {self.data[self.selected_point]:7.4f} мВ'
            )
        else:
            self.pointInfo.setText('')


    def resizeGL(self, w, h):
        # Настройка области просмотра
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 1, 1000) # Перспективная проекция
        glMatrixMode(GL_MODELVIEW)
    
    def heatmap(self, value):
        value = max(-1, value / self.heatmap_max)
            
        if value <= 0.0:
            return 0.0, (1 + value)*1.0, -value*1.0
        else:
            return value*1.0, (1-value)*1.0, 0.0

    def paintGL(self):
        if self.data is None:
            return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Стираем предыдущий кадр
        glUseProgram(self.shader_program) # Применяем шейдер
        self.update_matrices() # Обновление матриц

        zones_list = [True] + [self.zones[name] for name in ZONE_NAMES]

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "projection"),
            1, GL_TRUE, self.projection
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "view"),
            1, GL_TRUE, self.view
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "model"),
            1, GL_TRUE, self.model
        )
        glUniform1i(
            glGetUniformLocation(self.shader_program, "moduleVar"),
            self.moduleVar
        )
        glUniform1i(
            glGetUniformLocation(self.shader_program, "hidePoints"),
            self.hidePoints
        )
        glUniform1iv(
            glGetUniformLocation(self.shader_program, "active_zones"),
            10, np.array(zones_list, dtype=np.int32)
        )
        glUniform1f(
            glGetUniformLocation(self.shader_program, "amplitudeVar"),
            self.amplitudeVar
        )
        glUniform1f(
            glGetUniformLocation(self.shader_program, "heatmap_max"),
            self.heatmap_max
        )

        # Отрисовка
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.vertex_count)
        glBindVertexArray(0)

        if self.selected_point != -1:
            self.draw_selested_point()

        if self.debug_ray:
            start, direction = self.debug_ray
            self.draw_ray(start, direction)

    def update_matrices(self):
        # Инициализация матриц
        self.projection = np.eye(4, dtype=np.float32)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)

        self.projection = self.perspective(45, self.width() / self.height(), 0.1, 100)
        # Модельные преобразования
        self.model = self.translate_matrix(self.model, [self.object_translation[0], self.object_translation[1], 0.0])
        self.model = self.rotate_matrix(self.model, self.object_rotation[0], [1.0, 0.0, 0.0])
        self.model = self.rotate_matrix(self.model, self.object_rotation[1], [0.0, 0.0, 1.0])
        self.model = self.scale_matrix(self.model, [self.object_scale] * 3)

    def perspective(self, fov, aspect, near, far):
        f = 1.0 / np.tan(np.radians(fov) / 2.0)
        return np.array([
            [f / aspect, 0,  0,  0],
            [0,          f,  0,  0],
            [0,          0,  1,  0],
            [0,          0,  0,  1]
        ], dtype=np.float32)

    def translate_matrix(self, matrix, vec):
        result = np.eye(4)
        result[:3, 3] = vec
        return matrix @ result

    def scale_matrix(self, matrix, vec):
        result = np.eye(4)
        result[0, 0] = vec[0]
        result[1, 1] = vec[1]
        result[2, 2] = vec[2]
        return matrix @ result

    def rotate_matrix(self, matrix, angle, axis):
        angle = np.radians(angle)
        axis = axis / np.linalg.norm(axis)
        x, y, z = axis
        c, s = np.cos(angle), np.sin(angle)
        rot = np.array([
            [c + x ** 2 * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s, 0],
            [y * x * (1 - c) + z * s, c + y ** 2 * (1 - c), y * z * (1 - c) - x * s, 0],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z ** 2 * (1 - c), 0],
            [0, 0, 0, 1]
        ])
        return matrix @ rot

    def draw_selested_point(self):
        # Сохраняем текущие настройки шейдера
        current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        glUseProgram(0)

        # Сохраняем текущие матрицы
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadMatrixf(self.projection.T)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadMatrixf(self.model.T)

        # Рисуем точку
        glPointSize(15.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        glVertex3f(*self.vertices[self.selected_point])
        glEnd()

        # Восстанавливаем матрицы
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Восстанавливаем шейдер
        glUseProgram(current_program)

    def draw_ray(self, start, direction, length=10.0):
        # Вычисляем конечную точку луча
        end = start + direction * length

        # Сохраняем текущие настройки шейдера
        current_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        glUseProgram(0)

        # Сохраняем текущие матрицы
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadMatrixf(self.projection.T)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadMatrixf(self.model.T)

        # Устанавливаем цвет и толщину линии
        glColor3f(1.0, 0.0, 0.0)
        glLineWidth(2.0)

        # Рисуем луч
        glBegin(GL_LINES)
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
        glEnd()

        # Рисуем небольшую сферу в начале луча
        glPointSize(10.0)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_POINTS)
        glVertex3f(start[0], start[1], start[2])
        glEnd()

        # Восстанавливаем матрицы
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Восстанавливаем шейдер
        glUseProgram(current_program)

    def mousePressEvent(self, event):
        self.last_mouse_position = event.pos()
        if event.buttons() == Qt.LeftButton: # Qt.MiddleButton:
            cam_pos, ray_dir = screen_pos_to_ray(
                event.x(), self.height() - event.y() - 1,
                self.width(), self.height(),
                self.model, self.projection
            )

            # self.debug_ray = (cam_pos, ray_dir) # ОТЛАДКА

            self.selected_point = find_intersected_point(
                cam_pos, ray_dir,
                self.vertices,
                point_radius=1e-1
            )
            self.update_buffers()
            self.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        abs_max_val = float(0.5)

        if event.buttons() == Qt.LeftButton: # Вращение объекта
            delta = event.pos() - self.last_mouse_position
            self.object_rotation[0] += delta.y() * 0.5
            self.object_rotation[1] += delta.x() * 0.5
        elif event.buttons() == Qt.RightButton: # Перемещение объекта
            delta = event.pos() - self.last_mouse_position
            self.object_translation[0] = np.minimum(abs_max_val, np.maximum(-abs_max_val, self.object_translation[0] + delta.x() * 0.001))
            self.object_translation[1] = np.minimum(abs_max_val, np.maximum(-abs_max_val, self.object_translation[1] - delta.y() * 0.001))

        self.last_mouse_position = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.object_scale += delta * 0.0002
        self.object_scale = max(0.1, min(10.0, self.object_scale))

        self.update()
