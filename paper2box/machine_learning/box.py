import json

class Box():
    current_id = 0
    def __init__(self, class_, confidence, XYXY):
        self.class_ = class_
        self.confidence = confidence
        self.XYXY = [int(val) for val in XYXY]
        self.text = ""
        self.children = []
        self.connections = []
        self.id = Box.current_id
        Box.current_id += 1

class BoxSerializer(json.JSONEncoder):
    def default(self, o):
        dict_ = o.__dict__
        dict_['class'] = dict_['class_']
        del dict_['class_']
        return dict_