import json, copy

def prediction2json(classes, prediciton):
    flat_box_array = extract_flat_box_array(classes, prediciton)
    box_array = create_forest_hierarchy(flat_box_array)
    #print(box_array)
    with open('prediction.json', 'w') as file:
        json.dump(box_array, file, indent=4)

def extract_flat_box_array(classes, prediciton):
    flat_box_array = []
    tensor = prediciton._fields
    mapped_classes = list(map(lambda x: classes[x], tensor['pred_classes']))
    zipped = zip(tensor['pred_boxes'].tensor.tolist(), tensor['scores'].tolist(), mapped_classes)
    for (box, confidence, class_) in zipped:
        flat_box_array.append({
            'class': class_,
            'confidence': confidence,
            'XYXY': box,
            'children': []
        }) 
    return flat_box_array

def find_relations(boxes):
    relations = []
    for i, outer_box in enumerate(boxes):
        outer_box = outer_box['XYXY']
        for j, inner_box in enumerate(boxes):
            inner_box = inner_box['XYXY']
            if i == j:
                continue
            if outer_box[0] < inner_box[0] and outer_box[1] < inner_box[1] and outer_box[2] > inner_box[2] and outer_box[3] > inner_box[3]:
                relations.append((i, j))
    return relations

def transitive_reduction(input_relations):
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

class TreeNode():
    def __init__(self, data):
        self.data = data
        self.children = []

    def __repr__(self):
        return f'data: {self.data}, children: {repr(self.children)}'

def build_forest(elements, relations):
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

def create_forest_hierarchy(boxes):
    relations = find_relations(boxes)
    relations = transitive_reduction(relations)
    elements = list(range(len(boxes)))
    forest = build_forest(elements, relations)
    box_forest = index_to_box(boxes, forest)
    return box_forest

def index_to_box(boxes, index_forest):
    box_forest = []
    for i in index_forest:
        box = boxes[i.data].copy()
        box['children'] = index_to_box(boxes, i.children)
        box_forest.append(box)
    return box_forest
