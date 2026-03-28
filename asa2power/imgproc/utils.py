from pathlib import Path
import cv2
import numpy as np

from PyQt6.QtGui import QImage


def get_cropped_img(
        img_path: Path,
        color = np.zeros(3),
        tol = 50
    ) -> np.ndarray:
    img = cv2.imread(str(img_path))
    if img is None:
        raise Exception(f'Не удалось прочитать "{img_path}"!')

    thres = cv2.bitwise_not(
        cv2.inRange(img, color - tol, color + tol)
    )
    coords = cv2.findNonZero(thres)
    x, y, w, h = cv2.boundingRect(coords)

    img_new = cv2.cvtColor(img[y : y + h, x : x + w], cv2.COLOR_BGR2RGB)
    return img_new


def cimg2qimg(img_cv2: np.ndarray) -> QImage:
    h, w, ch = img_cv2.shape
    qimg = QImage(bytes(img_cv2.data), w, h, ch * w, QImage.Format.Format_RGB888)
    return qimg.copy()


def dbg_print_hsv(img, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = img[y, x]
        print(f'H: {pixel[0]}, S: {pixel[1]}, V: {pixel[2]} // X: {x}, Y: {y})')
