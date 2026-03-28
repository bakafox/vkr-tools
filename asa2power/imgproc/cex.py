import cv2
from PyQt6.QtGui import QColor
import numpy as np

from imgproc.utils import dbg_print_hsv


# Coefficient found through trial and error!
# Remember that OpenCV measures SV in 0..255, and H in 0..180
SAT_ARROW_THRES = 140 # 159 ?
HUE_ARROW_THMIN = 12
HUE_ARROW_THMAX = 24

SAT_BALLS_THRES = 163 # 185 ?
HUE_RBALL_THMIN = 1
HUE_RBALL_THMAX = 11
HUE_YBALL_THMIN = 27
HUE_YBALL_THMAX = 33
HUE_GBALL_THMIN = 50
HUE_GBALL_THMAX = 62

SAT_BOOST = 4.0 # 5.0 and above makes artifacts way too prominent

SAT_NOISE_THRES = 138 # 148 ?
VAL_NOISE_THRES = 100
VAL_GRIDS_THRES = 248


def get_currents_img(
    img: cv2.typing.MatLike,
    visualize = False
) -> cv2.typing.MatLike:
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    (h, s, v) = cv2.split(img_hsv)

    # BEFORE applying saturation boost, we'll try removing balls
    # and arrows using their already high saturation as a target:
    mask = (
        ((s > SAT_ARROW_THRES) & (h >= HUE_ARROW_THMIN) & (h <= HUE_ARROW_THMAX))
        | ((s > SAT_BALLS_THRES) & (h >= HUE_RBALL_THMIN) & (h <= HUE_RBALL_THMAX))
        | ((s > SAT_BALLS_THRES) & (h >= HUE_YBALL_THMIN) & (h <= HUE_YBALL_THMAX))
        | ((s > SAT_BALLS_THRES) & (h >= HUE_GBALL_THMIN) & (h <= HUE_GBALL_THMAX))
    )
    s[mask] = 0
    v[mask] = 0

    if visualize:
        img_vis = cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)
        cv2.imshow(f'Balls & Arrows masked via HSV thresholding', img_vis)
        cv2.setMouseCallback(
            'Balls & Arrows masked via HSV thresholding',
            lambda e, x, y, f, p,: dbg_print_hsv(cv2.merge([h, s, v]), e, x, y, f, p)
        )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # https://stackoverflow.com/questions/8535650/how-to-change-saturation-values-with-opencv
    s = np.clip(s * SAT_BOOST, 0, 255).astype(np.uint8)

    mask = (s < SAT_NOISE_THRES) | (v < VAL_NOISE_THRES) | (v > VAL_GRIDS_THRES)
    s[mask] = 0
    v[mask] = 0

    # I also thought of applying median filter, but can't really
    # figure out how to use it without either mixing up the blacks
    # or writing a 4-nested loop of supahslow Python code.

    img_res = cv2.merge([h, s, v])

    if visualize:
        img_vis = cv2.cvtColor(img_res, cv2.COLOR_HSV2BGR)
        cv2.imshow(f'JPEG compression masked via HSV thresholding', img_vis)
        cv2.setMouseCallback(
            'JPEG compression masked via HSV thresholding',
            lambda e, x, y, f, p,: dbg_print_hsv(img_res, e, x, y, f, p)
        )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return cv2.cvtColor(img_res, cv2.COLOR_HSV2RGB)


def get_colormap_hues(
    cmap: cv2.typing.MatLike,
) -> list[np.uint8]:
    cmap_hsv = cv2.cvtColor(cmap, cv2.COLOR_RGB2HSV)

    (h, s, v) = cv2.split(cmap_hsv)
    # s = np.clip(s * SAT_BOOST, 0, 255).astype(np.uint8)

    linear_hues = [np.uint8(0)]
    for i in range(h.shape[0]):
        if linear_hues and h[i][0] > linear_hues[-1]:
            linear_hues.append(h[i][0])
    
    return linear_hues


def extract_zone_avg_current(
    img: cv2.typing.MatLike,
    zone_info: tuple[str, dict, QColor],
    cmap_hues: list[np.uint8],
    hmap_min: float,
    hmap_max: float,
    visualize=False
) -> list[float]:
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    x1_s = int(zone_info[1]['x1'] * img.shape[1])
    x2_s = int(zone_info[1]['x2'] * img.shape[1])
    y1_s = int(zone_info[1]['y1'] * img.shape[0])
    y2_s = int(zone_info[1]['y2'] * img.shape[0])
    zone_img = img_hsv[y1_s:y2_s, x1_s:x2_s]

    cmap_powers = np.linspace(hmap_min, hmap_max, len(cmap_hues))

    # TODO: Учитывать не только Hue, но и Saturation (на самом деле
    # хз, надо ли оно, потому что главная проблема это их неучёта
    # связана как будто бы ток с визуализацией, плотность по ним не
    # посчитать из-за наложенного под активностями черно-белого МРТ,
    # а токи это находить мало мешает, ибо разница в Hue там есть)

    # Eucludian distance here was supah slow! So, a lookup table:
    cmap_lookup = np.interp(
        np.arange(cmap_hues[0], cmap_hues[-1]), cmap_hues, cmap_powers
    )

    if visualize:
        new_img = np.zeros(img.shape, dtype=np.uint8)

        for y in range(zone_img.shape[0]):
            for x in range(zone_img.shape[1]):
                if zone_img[y][x][2] < VAL_NOISE_THRES:
                    new_pixel = np.array([0, 0, 0])
                else:
                    try:
                        new_pixel = np.array([zone_img[y][x][0], 255, 200])
                    except IndexError:
                        new_pixel = np.array([0, 0, 255])

                new_img[y1_s + y, x1_s + x] = new_pixel

        cv2.imshow(zone_info[0], cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR))
        cv2.setMouseCallback(
            zone_info[0],
            lambda e, x, y, f, p: dbg_print_hsv(new_img, e, x, y, f, p)
        )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # TODO: Придумать, что же делать с вычислением активности не
        # только по активациям, но и по количеству точек вообще (сейчас
        # выходит, что если в области 2 шумных точки, она 100% активна)

    # print(cmap_lookup)
