from PyQt5.QtWidgets import QApplication
import sys

from windows.MainWindow import MainWindow


USE_CACHE = False # На текущий момент кэширование плохо работает из-за
                  # оптимизации размеров чанков (которые меняются при
                  # выходе из программы), поэтому сейчас оно отключено.


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow('EEG-Cutter v26-03-13', USE_CACHE)
    window.show()

    app.exec_()
