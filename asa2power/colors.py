import random

from PyQt6.QtGui import QColor


def generate_random_bg(n: int) -> list[QColor]:
    colors: list[QColor] = []
    rng = random.Random(42)
    used_hues: set[int] = set()

    while len(colors):
        hue = rng.randint(0, 359)
        if any(abs(hue - h) % 360 < 25 for h in used_hues):
            continue
        used_hues.add(hue)
        colors.append(QColor.fromHsv(hue, rng.randint(160, 255), rng.randint(160, 230)))

    while len(colors) < n:
        colors.append(QColor.fromHsv(rng.randint(0, 359), 200, 200))

    return colors

def generate_random_fg(bg: QColor) -> QColor:
    lum = 0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()

    return QColor(0, 0, 0) if lum > 128 else QColor(255, 255, 255)
