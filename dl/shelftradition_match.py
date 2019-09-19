from django.conf import settings
from tradition.matcher.matcher import Matcher
from goods.models import ShelfGoods
import os
import logging
import cv2
import numpy as np

logger = logging.getLogger("django")

class ShelfTraditionMatch:
    def __init__(self, upc):
        self._matcher = Matcher(visual=True)

        logger.info('begin loading TraditionMatch:{}'.format(upc))
        sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample','{}'.format(upc))
        for sample in os.listdir(sample_dir):
            sample_image_path = os.path.join(sample_dir, sample)
            if os.path.isfile(sample_image_path):
                self._matcher.add_baseline_image(sample_image_path, upc) # 基准样本不能被删除，所以直接调用_matcher的方法

        logger.info('end loading TraditionMatch:{}'.format(self._matcher.get_baseline_cnt()))

    def detect_one_with_path(self,image_path):
        upc, score = self._matcher.match_image_best_one(image_path)
        return upc, score

    def detect_one_with_cv2array(self,visual_image_path,cv2image):
        upc, score = self._matcher.match_image_best_one_with_nparray(visual_image_path, cv2.cvtColor(np.array(cv2image),cv2.COLOR_RGB2BGR))
        return upc, score

    def detect_one_with_nparray(self,visual_image_path,npimage):
        upc, score = self._matcher.match_image_best_one_with_nparray(visual_image_path, np.array(npimage))
        return upc, score
