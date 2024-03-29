import torch
import numpy as np
import torchvision.transforms as T
from torchvision import models


def resize(img, resize=256):
    trf = T.Compose([T.Resize(resize),
                     T.CenterCrop(resize)])
    return trf(img)


class SegmentModel:
    def __init__(self):
        self.resize = 256
        self._model = models.segmentation.fcn_resnet101(pretrained=True).eval()
        self._model.eval()

    def _decode_segmap(self, image, nc=21):
        # Define the helper function
        label_colors = np.array([(0, 0, 0),  # 0=background
                                 # 1=aeroplane, 2=bicycle, 3=bird, 4=boat, 5=bottle
                                 (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
                                 # 6=bus, 7=car, 8=cat, 9=chair, 10=cow
                                 (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
                                 # 11=dining table, 12=dog, 13=horse, 14=motorbike, 15=person
                                 (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
                                 # 16=potted plant, 17=sheep, 18=sofa, 19=train, 20=tv/monitor
                                 (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)])

        r = np.zeros_like(image).astype(np.uint8)
        g = np.zeros_like(image).astype(np.uint8)
        b = np.zeros_like(image).astype(np.uint8)

        for l in range(0, nc):
            idx = image == l
            r[idx] = label_colors[l, 0]
            g[idx] = label_colors[l, 1]
            b[idx] = label_colors[l, 2]

        rgb = np.stack([r, g, b], axis=2)
        return rgb

    def _transform(self, img):
        trf = T.Compose([T.Resize(self.resize),
                         T.CenterCrop(self.resize),
                         T.ToTensor(),
                         T.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])])
        return trf(img).unsqueeze(0)

    def find_segment(self, img):
        with torch.no_grad():
            inp = self._transform(img)
            out = self._model(inp)['out']
            out = torch.argmax(out.squeeze(), dim=0).detach().numpy()
            segmented_img = self._decode_segmap(out)
        return segmented_img
