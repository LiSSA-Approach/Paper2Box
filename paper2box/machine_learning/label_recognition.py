import cv2
import easyocr

from machine_learning.box import Box


def recognize_text(image):

    reader = easyocr.Reader(['en','de'])
    result = reader.readtext(image)

    labels = []

    for (bbox, text, prob) in result:
        label = Box("Label", prob, (bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]))
        label.text = text
        labels.append(label)
    
    return labels