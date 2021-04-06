import cv2
from pyzbar import pyzbar

def find_barcodes(img_path):
    try:
        image = cv2.imread(img_path)
    except:
        return None
    if image is not None:
        barcodes = pyzbar.decode(image)
        return barcodes
    return None