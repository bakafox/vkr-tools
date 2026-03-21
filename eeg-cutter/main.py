from PyQt5.QtWidgets import QApplication
import sys

from windows.MainWindow import MainWindow


# Если происходит ошибка "Failed to create an OpenGL context":
# 1. conda install -c anaconda libstdcxx-ng
# 2. conda install -c conda-forge libgcc
# 3. conda install -c conda-forge gcc=12.1.0
# 4. Перезайти в окружение Conda
# 5. Запуск: export PYOPENGL_PLATFORM=glx; python main.py 
# (https://www.reddit.com/r/opengl/comments/15qpdqd/)


USE_CACHE = False # На текущий момент кэширование плохо работает из-за
                  # оптимизации размеров чанков (которые меняются при
                  # выходе из программы), поэтому сейчас оно отключено.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow('EEG-Cutter v26-03-21', USE_CACHE)
    window.show()
    app.exec_()
