import tensorflow as tf
import os
from PIL import Image
import numpy as np
import logging
import time
from dl.step1_cnn import Step1CNN
from dl.util import caculate_level

logger = logging.getLogger("detect")


class ShelfDetectorFactory:
    _detector = {}

    @staticmethod
    def get_static_detector(export_dir):
        if export_dir not in ShelfDetectorFactory._detector:
            # FIXME 缓存对象有问题
            ShelfDetectorFactory._detector[export_dir] = ShelfDetector(export_dir)
        return ShelfDetectorFactory._detector[export_dir]

class ShelfDetector:
    def __init__(self, export_dir):
        file_path, _ = os.path.split(os.path.realpath(__file__))
        self.step1_cnn = Step1CNN(os.path.join(file_path, 'model', str(export_dir)))

        self.counter = 0
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True

    def load(self):
        if self.counter > 0:
            logger.info('waiting model to load (3s) ...')
            time.sleep(3)
            return
        self.counter = self.counter + 1
        if not self.step1_cnn.is_load():
            self.step1_cnn.load(self.config)


    def detect(self, image_path, step1_min_score_thresh=.5):
        if not self.step1_cnn.is_load():
            self.load()
            if not self.step1_cnn.is_load():
                logger.warning('loading model failed')
                return None


        # image_path = image_instance.source.path
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        (im_width, im_height) = image.size
        image_np = np.array(image)
        # Actual detection.
        (boxes, scores) = self.step1_cnn.detect(image_np)

        # data solving
        boxes = np.squeeze(boxes)
        # classes = np.squeeze(classes).astype(np.int32)
        scores_step1 = np.squeeze(scores)

        ret = []
        # logger.info('detect number:{}'.format(boxes.shape[0]))
        for i in range(boxes.shape[0]):
            if scores_step1[i] > step1_min_score_thresh:
                ymin, xmin, ymax, xmax = boxes[i]
                ymin = int(ymin * im_height)
                xmin = int(xmin * im_width)
                ymax = int(ymax * im_height)
                xmax = int(xmax * im_width)

                # newimage = image.crop((xmin, ymin, xmax, ymax))

                ret.append({'score': scores_step1[i],
                            'level': -1,
                            'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax,
                            })

        return ret
