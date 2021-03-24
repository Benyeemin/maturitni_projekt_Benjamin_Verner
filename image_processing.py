import cv2, pytesseract, sqlite3, psycopg2
from pyzbar import pyzbar
from contextlib import closing
import application_ui as ui
import method1_SQL as sqlsearch
import method2_fulltext_search as fulltextsearch

def find_books():
    image = cv2.imread("IMG_{}.png".format(ui.MainScreen.img_name))
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.Canny(img, 10, 250)

    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            x_max = 0
            x_min = 10 ** 6
            y_max = 0
            y_min = 10 ** 6
            for x in range(len(contour)):
                if contour[x][0][0] < y_min:
                    y_min = contour[x][0][0]
                if contour[x][0][0] > y_max:
                    y_max = contour[x][0][0]
                if contour[x][0][1] < x_min:
                    x_min = contour[x][0][1]
                if contour[x][0][1] > x_max:
                    x_max = contour[x][0][1]
            book = image[x_min:x_max, y_min:y_max]

            book = cv2.resize(book, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            # posterization, then possibly invert - not done yet
            color_count = {}
            book_flatten = book.flatten
            for pixel in book_flatten:
                if pixel in color_count:
                    color_count[pixel] += 1
                else:
                    color_count[pixel] = 1
            background_color = sorted(color_count, key=color_count.__getitem__, reverse=True)[0]
            if background_color == 0:
                book = cv2.bitwise_not(book)
            #

            text = pytesseract.image_to_string(book).split()
            return text

def find_barcodes():
    image = cv2.imread("IMG_{}.png".format(ui.MainScreen.img_name))
    barcodes = pyzbar.decode(image)
    return barcodes
