import cv2
import easyocr


def recognize_text(image, x1, y1, x2, y2):

    cropped_img = image[max(0, y1 - 5): min(len(image)- 1, y2 + 5), max(0, x1 - 5): min(len(image[0])-1, x2 + 5)]
    # cv2.imwrite('cropped_image2.png', cropped_img[:, :, ::-1])
    scaled = cv2.resize(cropped_img, (2 * cropped_img.shape[1], 2 * cropped_img.shape[0]), interpolation=cv2.INTER_AREA)
    # cv2.imwrite('scaled_image2.png', scaled[:, :, ::-1])

    reader = easyocr.Reader(['en','de'])
    result = reader.readtext(scaled)

    text = " ".join(list(map( lambda tuple: tuple[1], result)))
    return text