from PyQt5.QtWidgets import QApplication
import sys

from windows.MainWindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow('EEG-Cutter v26-03-03')
    window.show()

    app.exec_()
