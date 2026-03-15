from pathlib import Path
import cv2
import numpy as np
import pytesseract
import re

from PyQt6.QtGui import QImage, QColor


def get_cropped_img(
        img_path: Path,
        color = np.zeros(3),
        tolerance = 50
    ) -> np.ndarray:
    img = cv2.imread(str(img_path))
    if img is None:
        raise Exception(f'Не удалось прочитать "{img_path}"!')

    thres = cv2.bitwise_not(
        cv2.inRange(img, color - tolerance, color + tolerance)
    )

    coords = cv2.findNonZero(thres)
    x, y, w, h = cv2.boundingRect(coords)

    img_new = cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_BGR2RGB)
    return img_new


def read_hmap_digits(
        img: cv2.typing.MatLike,
        coords: dict,
        visualize = False
    ) -> float:
    # https://stackoverflow.com/questions/37745519/use-pytesseract-ocr-to-recognize-text-from-an-image#60161328
    x1_s = int(coords['x1'] * img.shape[0])
    y1_s = int(coords['y1'] * img.shape[1])
    x2_s = int(coords['x2'] * img.shape[0])
    y2_s = int(coords['y2'] * img.shape[1])

    img_gs = cv2.cvtColor(
        img[y1_s:y2_s, x1_s:x2_s],
        cv2.COLOR_BGR2GRAY
    )
    img_gsc = cv2.convertScaleAbs(img_gs, alpha=1.8, beta=-80)
    thres = cv2.threshold(img_gsc, 240, 255, cv2.THRESH_OTSU)[1]

    # Почему мы не распознаём букву e, точки и т.п.? Потому что
    # tesseract их распознаёт очень и очень плохо! Вместо этого
    # мы вставим позже вручную, пользуясь однотипностью данных.
    digit_raw = pytesseract.image_to_string(
        255 - thres, lang='eng', config='-c tessedit_char_whitelist=0123456789|'
    )

    digit_strip = re.sub(r'^[\d|]\n|[ |]', '', digit_raw)

    # По идее, можно даже вторую часть с цифрами заменить на
    # константу "e-08", потому что измеряем мы в am/m всегда,
    # а ноль в любой системе все равно останется нулём.
    digit_str = digit_strip[0] + '.' + digit_strip[1:3] + 'e-08' # + 'e-' + digit_strip[-2:]

    if visualize:
        cv2.imshow(f'{digit_raw} // {digit_str} // {float(digit_str)}', 255 - thres)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return float(digit_str)


def process_img(
        img_path: Path,
        zones: list[tuple[str, dict, QColor]],
        out_path: Path,
        debug = False
    ):
    hmap_max_coords = filter(lambda z: z[0] == 'HMAP_MAX', zones)
    try:
        hmap_max_coords = next(hmap_max_coords)[1]
    except StopIteration:
        raise Exception(f'Не найдена обязательная зона "HMAP_MAX"!')

    hmap_min_coords = filter(lambda z: z[0] == 'HMAP_MIN', zones)
    try:
        hmap_min_coords = next(hmap_min_coords)[1]
    except StopIteration:
        raise Exception(f'Не найдена обязательная зона "HMAP_MIN"!')

    img = get_cropped_img(img_path)

    hmap_min = read_hmap_digits(img, hmap_min_coords, debug)
    hmap_max = read_hmap_digits(img, hmap_max_coords, debug)

    currents = []
    for zone in zones:
        if zone[0] in ['HMAP_MAX', 'HMAP_MIN']:
            continue

        # current = (zone[0], calc_zone_current(img, zone[1], debug))
        # currents.append(current)

    # Ну и тут типа запись идёт в yaml


def cimg2qimg(img_cv2: np.ndarray) -> QImage:
    h, w, ch = img_cv2.shape
    qimg = QImage(bytes(img_cv2.data), w, h, ch * w, QImage.Format.Format_RGB888)
    return qimg.copy()
