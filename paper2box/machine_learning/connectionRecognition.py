import math


delta = 1

def check_intersection(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    area = max(0, xB - xA) * max(0, yB - yA)
    areaBoxA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    return area != 0 and not math.isclose(area, areaBoxA)


def check_for_neighboorhood(connection, box):
    b = connection.XYXY[2] - connection.XYXY[0]
    h = connection.XYXY[3] - connection.XYXY[1]
    x = connection.XYXY[0]
    y = connection.XYXY[1]
    left_bbox = (x - delta, y - delta, x + delta, y + h + delta)
    right_bbox = (x + b - delta, y - delta, x + b + delta, y + h + delta)
    top_bbox = (x - delta, y - delta, x + b + delta, y + delta)
    bottom_bbox = (x - delta, y - delta, x + b + delta, y + delta)

    neighbor = False
    neighbor = neighbor or check_intersection(left_bbox, box.XYXY)
    neighbor = neighbor or check_intersection(right_bbox, box.XYXY)
    neighbor = neighbor or check_intersection(top_bbox, box.XYXY)
    neighbor = neighbor or check_intersection(bottom_bbox, box.XYXY)

    return neighbor


def is_box(element):
    return element.class_ == "ClassNode" or element.class_ == "Package"


def find_connections(connection, elements):
    neighbors = []
    for element in elements:
        if is_box(element):
            neighbor = check_for_neighboorhood(connection, element)
            if neighbor:
                neighbors.append(element.id)
    return neighbors