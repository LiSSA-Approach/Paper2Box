import copy, json
from machine_learning.connection_recognition import find_connections
from machine_learning.label_recognition import recognize_text
from machine_learning.box import Box, BoxSerializer

connection_classes = [
    'NAryAssociationDiamond', 
    'Aggregation', 
    'Composition', 
    'Extension', 
    'Dependency', 
    'Realization', 
    'CommentConnection', 
    'AssociationUnidirectional', 
    'AssociationBidirectional'
]

class Prediction():
    def __init__(self, image, classes, prediction):
        self.image = image
        self.boxes = self.extract_boxes(classes, prediction)
        self.attatch_connections()
        self.attatch_labels()
        self.forest = self.create_forest() 
    
    def extract_boxes(self, classes, prediction):
        boxes = []
        tensor = prediction._fields
        mapped_classes = list(map(lambda x: classes[x], tensor['pred_classes']))
        zipped = zip(tensor['pred_boxes'].tensor.tolist(), tensor['scores'].tolist(), mapped_classes)
        for (XYXY, confidence, class_) in zipped:
            boxes.append(Box(class_, confidence, XYXY)) 
        return boxes
    
    def attatch_connections(self):
        new_boxes = []
        for box in self.boxes:
            new_boxes.append(box)
            if box.class_ in connection_classes: continue
            box.connections = find_connections(box, self.boxes)
        return new_boxes
    
    def attatch_labels(self):
        new_boxes = []
        for box in self.boxes:
            new_boxes.append(box)
            if box.class_ != 'Label': continue
            (x1, y1, x2, y2) = box.XYXY
            box.text = recognize_text(self.image, x1, y1, x2, y2)
    
    def create_forest(self):
        relations = _find_relations(self.boxes)
        relations = _transitive_reduction(relations)
        elements = list(range(len(self.boxes)))
        forest = _build_forest(elements, relations)
        box_forest = _index_to_box(self.boxes, forest)
        return box_forest

    def forest_to_json(self):
        return json.dumps(self.forest, indent=4, cls=BoxSerializer)

    def to_json(self):
        return self.forest_to_json()
    



# private

class TreeNode():
    def __init__(self, data):
        self.data = data
        self.children = []

    def __repr__(self):
        return f'data: {self.data}, children: {repr(self.children)}'

def _build_forest(elements, relations):
    set_ = [TreeNode(e) for e in elements]
    for (parent, child) in relations:
        parent_node = [s for s in set_ if s.data == parent]
        if parent_node == []: continue
        parent_node = parent_node[0]
        child_node = [s for s in set_ if s.data == child]
        if child_node == []: continue
        child_node = child_node[0]
        parent_node.children.append(copy.copy(child_node))
        set_ = [s for s in set_ if s.data != child]
    return set_

def _index_to_box(boxes, index_forest):
    box_forest = []
    for i in index_forest:
        box = copy.copy(boxes[i.data])
        box.children = _index_to_box(boxes, i.children)
        box_forest.append(box)
    return box_forest

def _find_relations(boxes):
    relations = []
    for i, outer_box in enumerate(boxes):
        outer_box = outer_box.XYXY
        for j, inner_box in enumerate(boxes):
            inner_box = inner_box.XYXY
            if i == j:
                continue
            if outer_box[0] < inner_box[0] and outer_box[1] < inner_box[1] and outer_box[2] > inner_box[2] and outer_box[3] > inner_box[3]:
                relations.append((i, j))
    return relations

def _transitive_reduction(input_relations):
    relations = input_relations.copy()
    delete = []
    for  x in relations:
        for y in relations:
            for z in relations:
                if (x,y) != (y,z) and (x,y) != (x,z):
                    if (x,y) in relations and (y,z) in relations:
                        delete.append((x,z))
    for d in delete:
        relations.remove(d)
    return relations