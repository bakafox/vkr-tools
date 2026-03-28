from pathlib import Path
from PyQt6.QtGui import QColor
import numpy as np

from imgproc.cex import extract_zone_avg_current, get_currents_img, get_colormap_hues
from imgproc.ocr import read_hmap_digits
from imgproc.utils import get_cropped_img


def process_cmap(
    cmap_path: Path,
    debug_arr: list[str] = []
) -> list[np.uint8]:
    cmap = get_cropped_img(cmap_path, tol=0)
    
    cmap_hues = get_colormap_hues(cmap)
    if ('che' in debug_arr):
        print(cmap_hues, len(cmap_hues))

    return cmap_hues


def process_img(
    img_path: Path,
    zones: list[tuple[str, dict, QColor]],
    cmap_hues: list[np.uint8],
    debug_arr: list[str] = []
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

    hmap_min = read_hmap_digits(img, hmap_min_coords, ('hdr' in debug_arr))
    hmap_max = read_hmap_digits(img, hmap_max_coords, ('hdr' in debug_arr))

    currents_img = get_currents_img(img, ('ipp' in debug_arr))

    currents = dict()
    for zone in zones:
        if zone[0] in ['HMAP_MAX', 'HMAP_MIN']:
            continue

        currents[zone[0]] = extract_zone_avg_current(
            currents_img,
            zone,
            cmap_hues,
            hmap_min,
            hmap_max,
            ('cex' in debug_arr)
        )
