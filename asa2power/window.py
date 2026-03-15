from pathlib import Path
import pyperclip

from PyQt6.QtWidgets import QMainWindow, QListWidgetItem
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QCoreApplication

from colors import generate_random_fg, generate_random_bg
from process import process_img
from ui.Preview import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(
            self,
            zones: list[tuple[str, dict]],
            img_paths: list[Path],
            out_dir: Path,
            debugging: bool
        ):
        super().__init__()

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self._index = 0
        colors = generate_random_bg(len(zones))
        self._zones: list[tuple[str, dict, QColor]] = [
            (name, coords, colors[i]) for i, (name, coords) in enumerate(zones)
        ]
        self._paths = img_paths
        self._out = out_dir
        self._debug = debugging

        self._populate_list()
        self._ui.canvas.set_zones(self._zones)

        self._ui.btnPrev.clicked.connect(self._prev)
        self._ui.btnNext.clicked.connect(self._next)
        self._ui.btnProcess.clicked.connect(self._process)
        self._ui.canvas.cursorMoved.connect(self._coords_update)
        self._ui.canvas.cursorClick.connect(self._coords_copy)

        self._refresh()

    def _populate_list(self):
        self._ui.zoneList.clear()
        for name, _, color in self._zones:
            item = QListWidgetItem(name)
            solid = QColor(color)
            solid.setAlpha(255)
            item.setBackground(solid)
            item.setForeground(generate_random_fg(solid))
            self._ui.zoneList.addItem(item)

    def _coords_update(self, mouse_x: float, mouse_y: float):
        result = self._ui.canvas.get_img_coords(mouse_x, mouse_y)

        if result is None:
            self._ui.lblCursor.setText(
                ' Наведите курсор на изображ-е, чтобы\n'
                + ' увидеть его координаты в px и в 0…1.'
            )
        else:
            px_x, px_y, rel_x, rel_y = result
            self._ui.lblCursor.setText(
                f' X: {px_x} ({rel_x:.6f}), Y: {px_y} ({rel_y:.6f})'
            )
    
    def _coords_copy(self, mouse_x: float, mouse_y: float, order: int):
        result = self._ui.canvas.get_img_coords(mouse_x, mouse_y)

        if result is None:
            return
        else:
            _, _, rel_x, rel_y = result
            pyperclip.copy(
                f'    - x{order}: {rel_x:.6f}\n'
                + f'    - y{order}: {rel_y:.6f}'
            )

    def _prev(self):
        if self._index > 0:
            self._index -= 1
            self._refresh()

    def _next(self):
        if self._index < len(self._paths) - 1:
            self._index += 1
            self._refresh()

    def _refresh(self):
        self._ui.lblCounter.setText(f'{self._index + 1} / {len(self._paths)}')
        self._ui.btnPrev.setEnabled(self._index > 0)
        self._ui.btnNext.setEnabled(self._index < len(self._paths) - 1)
        self._ui.canvas.set_image(self._paths[self._index])

    def _process(self):
        self._ui.btnPrev.setEnabled(False)
        self._ui.btnNext.setEnabled(False)
        self._ui.btnProcess.setEnabled(False)

        results = []
        for ii, ip in enumerate(self._paths):
            self._ui.lblCursor.setText(
                f'Обработка {ii + 1} изображения из {len(self._paths)}…'
            )
            QCoreApplication.processEvents() # Иначе не перерисует
            results.append(
                process_img(ip, self._zones, self._out, self._debug)
            )

        self._ui.lblCursor.setText(
            f'Обработка изображений завершена.'
        )
        self._ui.btnPrev.setEnabled(True)
        self._ui.btnNext.setEnabled(True)
        self._ui.btnProcess.setEnabled(True)
