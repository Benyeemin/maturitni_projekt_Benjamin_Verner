import cv2, pytesseract

def find_books(img_path): #book detection using cv2, currently not used
    try:
        image = cv2.imread(img_path)
    except:
        return None
    if image is not None:
        text_list = []
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
                not_needed, book = cv2.threshold(book, 127, 255, cv2.THRESH_BINARY)

                text = pytesseract.image_to_string(book).split()
                text_list.append(text)
        return text_list
    return None