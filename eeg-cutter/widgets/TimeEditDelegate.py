from PyQt5.QtWidgets import QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, pyqtSlot, QTime


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
