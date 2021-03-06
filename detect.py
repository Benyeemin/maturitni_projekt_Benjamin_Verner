"""
Code taken and adapted from YOLOV4 examples.
"""
import tensorflow as tf
import pytesseract, cv2, sys, os, logging
from pathlib import Path
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from tensorflow.python.saved_model import tag_constants
import numpy as np

if getattr(sys, 'frozen', False):
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = str(Path(sys._MEIPASS)/'tesseract'/'tesseract.exe')
    elif os.name == 'posix':
        pytesseract.pytesseract.tesseract_cmd = str(Path(sys._MEIPASS) / 'tesseract' / 'tesseract')
    YOLOV_MODEL = str(Path(sys._MEIPASS)/'yolov4-416')
else:
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = str(Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe'))
    YOLOV_MODEL = str(Path(__file__).parent / 'yolov4-416')

def find_books(image_path):
    try:
        image = cv2.imread(image_path)
    except:
        return None
    if image is not None:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(image, (416, 416))
        image_data = image_data / 255.

        images_data = []
        images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)

        saved_model_loaded = tf.saved_model.load(YOLOV_MODEL, tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        batch_data = tf.constant(images_data)
        pred_bbox = infer(batch_data)
        for key, value in pred_bbox.items():
            boxes = value[:, :, 0:4]
            pred_conf = value[:, :, 4:]

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=0.45,
            score_threshold=0.25
        )

        text_list = []
        out_boxes = boxes.numpy()
        out_scores = scores.numpy()
        out_classes = classes.numpy()
        num_boxes = valid_detections.numpy()

        for object in range(num_boxes[0]):
            image_h, image_w, _ = image.shape
            class_ind = int(out_classes[0][object])
            if class_ind == 73: #book index in data/classes/coco.names
                coor = out_boxes[0][object]
                coor[0] = int(coor[0] * image_h)
                coor[2] = int(coor[2] * image_h)
                coor[1] = int(coor[1] * image_w)
                coor[3] = int(coor[3] * image_w)
                book = image[int(coor[0]):int(coor[2]), int(coor[1]):int(coor[3])]
                not_needed, book = cv2.threshold(book, 127, 255, cv2.THRESH_BINARY)

                for i in range(4):
                    text = pytesseract.image_to_string(book).split()
                    if text:
                        break
                    book = cv2.rotate(book, cv2.ROTATE_90_CLOCKWISE)
                text_list.append(text)
        logging.root.info(f'OCR results: {text_list}')
        return text_list
    return None