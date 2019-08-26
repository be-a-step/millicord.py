import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from pathlib import Path
import numpy as np
import cv2
import urllib
from PIL import Image
from logging import getLogger, StreamHandler, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

DATA_TRANSFORM_RES = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
DATA_TRANSFORM_DENSE = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
])
MODEL_PATH = './resources/models/idol_recognition_{}.model'
CASCADE_PATH = './resources/cv2_cascade/lbpcascade_animeface.xml'
CLASSES_PATH = './resources/models/idol_recognition_classes.txt'
TRIMING_MARGIN = (20, 20, 20, 0)
MODEL_NAME = "densenet"


class IdolRecognition(object):

    def __init__(self):
        logger.info("load classes")
        self.classes = np.loadtxt(CLASSES_PATH, dtype="unicode")
        logger.debug(self.classes)
        logger.info("prepare model")
        self.model = self.prepare_model(MODEL_NAME)
        self.transformation = IdolRecognition.get_transform(MODEL_NAME)
        logger.info("prepare cascade")
        self.face_cascade = IdolRecognition.prepare_cascade()

    def prepare_model(self, name):
        model = self.get_model(name)
        if torch.cuda.is_available():
            model = model.cuda()
        model.eval()
        return model

    def get_transform(name):
        if name == "resnet":
            return DATA_TRANSFORM_RES
        elif name == "densenet":
            return DATA_TRANSFORM_DENSE

    def get_model(self, name):
        if name == 'resnet':
            model = models.resnet34(pretrained=True)
            num_features = model.fc.in_features
            model.fc = nn.Linear(num_features, len(self.classes))
        if name == "densenet":
            def squeeze_weights(m):
                m.weight.data = m.weight.data.sum(dim=1)[:, None]
                m.in_channels = 1
            model = models.densenet121(pretrained=True)
            num_features = model.classifier.in_features
            model.classifier = nn.Linear(num_features, len(self.classes))
        model_path = MODEL_PATH.format(name)
        param = torch.load(str(Path(model_path)))
        model.load_state_dict(param)
        return model

    def prepare_cascade():
        return cv2.CascadeClassifier(str(Path(CASCADE_PATH)))

    def recognize_idol(self, url, name):
        logger.info("get image")
        image = IdolRecognition.get_image(url)
        logger.info("recognize face")
        faces = self.triming_face(image)
        logger.info("predict")
        predicted = self.predict_faces(faces)
        for index in predicted:
            logger.debug(self.classes[index])
            if(self.classes[index] == name):
                return True
        return False

    def get_image(url):
        resp = urllib.request.urlopen(url)
        image_array = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = Image.fromarray(cv2.imdecode(image_array, cv2.IMREAD_COLOR))
        return image

    def triming_face(self, image):
        face_images = list()
        image_array = np.array(image, 'uint8')
        faces = self.face_cascade.detectMultiScale(image_array)
        for (x, y, w, h) in faces:
            # 顔画像領域のマージン設定
            resize_position = IdolRecognition.get_resize_position(
                x, y, w, h, TRIMING_MARGIN, image.width, image.height)
            # 顔を 64x64 サイズにリサイズ
            roi = cv2.resize(image_array[resize_position[1]: resize_position[3],
                                         resize_position[0]: resize_position[2]],
                             (64, 64),
                             interpolation=cv2.INTER_LINEAR)
            face_images.append(roi)
            # cv2.imwrite("test" + str(x) + ".png", roi)
            # logger.debug(str(x))
        return face_images

    def get_resize_position(x, y, w, h, margin, max_width, max_hight):
        margin_left = int(w * margin[0] / 100)
        margin_top = int(h * margin[1] / 100)
        margin_right = int(w * margin[2] / 100)
        margin_bottom = int(h * margin[3] / 100)

        pos_top = y - margin_top if y - margin_top > 0 else 0
        pos_bottom = y + h + margin_bottom if y + h + \
            margin_bottom < max_hight else max_hight
        pos_left = x - margin_left if x - margin_left > 0 else 0
        pos_right = x + w + margin_right if x + w + \
            margin_right < max_width else max_width

        return (pos_left, pos_top, pos_right, pos_bottom)

    def predict_faces(self, faces):
        prediction = list()
        for image in faces:
            predicted = self.predict(image)
            logger.debug(predicted)
            prediction.append(predicted)
        return prediction

    def predict(self, image):
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_tensor = self.transformation(image_pil)
        image_tensor = image_tensor.unsqueeze(0)
        if torch.cuda.is_available():
            image_tensor = image_tensor.cuda()
        with torch.no_grad():
            output = self.model(image_tensor)
        logger.debug(output)
        _, predicted = torch.max(output, 1)
        return predicted.item()
