from django.conf import settings
from tradition.matcher.matcher import Matcher
from goods.models import ShelfGoods
import os
import logging
import cv2
import numpy as np
import tensorflow as tf

logger = logging.getLogger("django")

class ShelfTraditionMatch:
    def __init__(self, upc):
        self._matcher = Matcher(visual=True)
        self._upc = upc
        self._init = True
        self.visual_image_path = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_goods_visual',
                                         '{}'.format(self._upc))
        if not tf.gfile.Exists(self.visual_image_path):
            tf.gfile.MakeDirs(self.visual_image_path)

        #TODO 目前接口只支持文件
        self.visual_image_path = os.path.join(self.visual_image_path,'t.jpg')

        logger.info('begin loading TraditionMatch:{}'.format(upc))
        sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample','{}'.format(upc))
        if not os.path.isdir(sample_dir):
            self._init = False

        if self._init:
            for sample in os.listdir(sample_dir):
                sample_image_path = os.path.join(sample_dir, sample)
                if os.path.isfile(sample_image_path):
                    self._matcher.add_baseline_image(sample_image_path, upc) # 基准样本不能被删除，所以直接调用_matcher的方法

        logger.info('end loading TraditionMatch:{}'.format(self._matcher.get_baseline_cnt()))

    def detect_one_with_path(self,image_path):
        if not self._init:
            return None
        upc, cnt = self._matcher.match_result(image_path)
        if upc == self._upc:
            return True
        else:
            if cnt >0:
                return False
            else:
                return None

    def detect_one_with_cv2array(self,cv2image):
        if not self._init:
            return None
        upc, cnt = self._matcher.match_image_best_one_with_nparray(self.visual_image_path, cv2.cvtColor(np.array(cv2image),cv2.COLOR_RGB2BGR))
        if upc == self._upc:
            return True
        else:
            if cnt >0:
                return False
            else:
                return None


    def detect_one_with_nparray(self,npimage):
        if not self._init:
            return None
        upc, cnt = self._matcher.match_image_best_one_with_nparray(self.visual_image_path, np.array(npimage))
        if upc == self._upc:
            return True
        else:
            if cnt >0:
                return False
            else:
                return None

