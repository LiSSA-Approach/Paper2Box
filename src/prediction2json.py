import json

def prediction2json(classes, prediciton):
    flat_box_array = extract_flat_box_array(classes, prediciton)
    box_array = create_tree_hierarchy(flat_box_array)
    print(box_array)
    with open('pediction.json', 'w') as file:
        json.dump(flat_box_array, file, indent=4)

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

#def build_hierarchy(flat_box_array):
    #hierarchy = []
    #for i, box1 in enumerate(flat_box_array):
        #hierarchy.append(box1)
        #box1 = box1['XYXY']
        #for j, box2 in enumerate(flat_box_array):
            #box2 = box2['XYXY']
            #if i == j: continue
            #if box1[0] > box2[0] and box1[1] > box2[1] and box1[2] < box2[2] and box1[3] < box2[3]:
                #hierarchy[i]['children'].append(hierarchy[j])
    #return hierarchy

def find_relations(boxes):
    relations = []
    for i, box1 in enumerate(boxes):
        box1 = box1['XYXY']
        for j, box2 in enumerate(boxes):
            box2 = box2['XYXY']
            if i == j:
                continue
            if box1[0] > box2[0] and box1[1] > box2[1] and box1[2] < box2[2] and box1[3] < box2[3]:
                relations.append((i, j))
    return relations

class TreeNode():
    def __init__(self, data):
        self.data = data
        self.children = []

def build_tree(elements, relations):
    set_ = [TreeNode(e) for e in elements]
    for (parent, child) in relations:
        parent_node = [s for s in set_ if s.data == parent]
        child_node = [s for s in set_ if s.data == child]
        parent_node.children.append(child_node)

def create_tree_hierarchy(boxes):
    lin_hierarchy = create_linear_hierarchy(boxes)
    tree_hiera
    print(lin_hierarchy)
    while lin_hierarchy != []:



