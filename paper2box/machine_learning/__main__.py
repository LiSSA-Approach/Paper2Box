from prediction2json import prediciton2json
from detectron2 import get_prediciton

def get_json_prediction(image_file):
    prediction = get_prediciton(image_file)
    json_prediction = prediciton2json(prediction)
    return json_prediction

