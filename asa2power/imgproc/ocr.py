import cv2
import pytesseract
import re


def read_hmap_digits(
        img: cv2.typing.MatLike,
        coords: dict,
        visualize = False
    ) -> float:
    x1_s = int(coords['x1'] * img.shape[0])
    y1_s = int(coords['y1'] * img.shape[1])
    x2_s = int(coords['x2'] * img.shape[0])
    y2_s = int(coords['y2'] * img.shape[1])

    # https://stackoverflow.com/questions/37745519/use-pytesseract-ocr-to-recognize-text-from-an-image#60161328
    img_gs = cv2.cvtColor(img[y1_s:y2_s, x1_s:x2_s], cv2.COLOR_RGB2GRAY)

    img_gsc = cv2.convertScaleAbs(img_gs, alpha=1.8, beta=-80)
    thres = cv2.threshold(img_gsc, 240, 255, cv2.THRESH_OTSU)[1]

    # Why don't we read letter e, dots etc.? Because tesseract
    # recognizes them really damn bad! In fact it seems to be
    # having a hard time just recognizing the digits! Which is
    # why we'll format manually as much stuff as we can:
    digit_raw = pytesseract.image_to_string(
        255 - thres, lang='eng', config='-c tessedit_char_whitelist=0123456789|'
    )

    digit_strip = re.sub(r'^[\d|]\n|[ |]', '', digit_raw)

    # Due to data consistency, we can even drop the second part
    # completely and just hardcode "e-08", because max current
    # always has this degree, and min current always equals 0:
    digit_str = digit_strip[0] + '.' + digit_strip[1:3] + 'e-08' # + 'e-' + digit_strip[-2:]

    if visualize:
        cv2.imshow(f'{digit_raw} // {digit_str} // {float(digit_str)}', 255 - thres)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return float(digit_str)
