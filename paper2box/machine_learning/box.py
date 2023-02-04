import copy, json


class Box():
    current_id = 0
    def __init__(self, class_, confidence, XYXY, children):
        self.class_ = class_
        self.confidence = confidence
        self.XYXY = XYXY
        self.children = children
        self.id = Box.current_id
        Box.current_id += 1

class BoxSerializer(json.JSONEncoder):
    def default(self, o):
        dict_ = o.__dict__
        dict_['class'] = dict_['class_']
        del dict_['class_']
        return dict_

def extract_boxes(classes, prediction):
    box_list = []
    tensor = prediction._fields
    mapped_classes = list(map(lambda x: classes[x], tensor['pred_classes']))
    zipped = zip(tensor['pred_boxes'].tensor.tolist(), tensor['scores'].tolist(), mapped_classes)
    for (XYXY, confidence, class_) in zipped:
        box_list.append(Box(class_, confidence, XYXY, [])) 
    return box_list

def create_forest(boxes):
    relations = _find_relations(boxes)
    relations = _transitive_reduction(relations)
    elements = list(range(len(boxes)))
    forest = _build_forest(elements, relations)
    box_forest = _index_to_box(boxes, forest)
    return box_forest

def forest_to_json(boxes):
    return json.dumps(boxes, indent=4, cls=BoxSerializer)

def pred_to_json(classes, prediction):
    return forest_to_json(create_forest(extract_boxes(classes, prediction)))


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