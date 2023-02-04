from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from detectron2 import model_zoo

from matplotlib import pyplot as plt
import matplotlib

def read_json(directory, name):
    json_file = os.path.join(directory, name + ".json")
    with open(json_file) as f:
        imgs_anns = json.load(f)
    return imgs_anns

def get_dicts(directory, name):
    data = read_json(directory, f"{name}")
    dataset_dicts = []
    for image in data["images"]:
        record = {}
        filename = os.path.join(directory, "images", image["file_name"])
        image_id = image["id"]
        height = image["height"]
        width = image["width"]
        record["file_name"] = filename
        record["image_id"] = image_id
        record["height"] = height
        record["width"] = width

        annotations = list(filter(lambda a: a["image_id"] == image_id, data["annotations"]))
        for anno in annotations:
            anno["bbox_mode"] = BoxMode.XYXY_ABS
            bbox = anno["bbox"]
            anno["bbox"] = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]
        record["annotations"] = annotations
        dataset_dicts.append(record)
    return dataset_dicts

def show_img(img):
    # Some DPI Scaling ..
    dpi = matplotlib.rcParams['figure.dpi'] / 1.5
    # Determine the figures size in inches to fit your image
    height, width, depth = img.shape
    figsize = width / float(dpi), height / float(dpi)
    plt.figure(figsize=figsize)
    # Some color shifting
    plt.imshow(img[..., ::-1])  # RGB-> BGR
    # plt.imshow(img)
    plt.xticks([]), plt.yticks([])
    plt.show()

def get_predicion(image_file, visualize=False):
    # Model config
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 1e-10
    cfg.MODEL.WEIGHTS = './model/model_final.pth'
    cfg.MODEL.DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    predictor = DefaultPredictor(cfg)
    im = cv2.imread('./data/images/ex_02.jpg')

    output = predictor(im)
    if not visualize: return output["instances"].to("cpu")

    # Draw predictions using visualizer
    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    # Draw predictions on image
    out = v.draw_instance_predictions(output["instances"].to("cpu"))
    # Show image
    show_img(out.get_image()[:, :, ::-1])
    return output["instances"].to("cpu")



