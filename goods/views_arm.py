import logging
import os
import shutil
import time
import tensorflow as tf
import json
import numpy as np
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from .serializers import *
from dl import freezer2detection
from django.conf import settings
from goods.edge.contour_detect_3d import Contour_3d
import traceback
import math

logger = logging.getLogger("django")

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

class ArmImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = ArmImage.objects.order_by('-id')
    serializer_class = ArmImageSerializer

    def create(self, request, *args, **kwargs):
        logger.info('begin detect arm:')
        time0 = time.time()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        z_deviation = 0 #10 # 60 # 10
        detect = Contour_3d(serializer.instance.rgb_source.path, serializer.instance.depth_source.path, serializer.instance.table_z-z_deviation)
        min_rectes, z, boxes = detect.find_contour(False)

        time1 = time.time()
        detector = None
        image = None
        tmp_dir = None
        if len(min_rectes)>0:
            # 准备阶段
            detector = {
                '1':[66,69],
                '2':[69,160],
                '3':[62,103],
                # '7':[150,227],
                # '8':[165,167],
                '10':[80,180]
            }
            # last_normal_train_qs = TrainAction.objects.filter(state=goods2_common.TRAIN_STATE_COMPLETE).filter(
            #     deviceid='100000').exclude(action='TC').order_by('-id')
            # if len(last_normal_train_qs) > 0:
            #     last_train = last_normal_train_qs[0]
            #     last_normal_train_model = \
            #     TrainModel.objects.filter(train_action_id=last_train.pk).exclude(model_path='').order_by('-id')[0]
            #     detector = imagedetection.ImageDetectorFactory.get_static_detector(
            #         last_normal_train_model)
            #     image = Image.open(serializer.instance.rgb_source.path)
            #     tmp_dir = '{}/tmp'.format(os.path.dirname(serializer.instance.rgb_source.path))
            #     if not tf.gfile.Exists(tmp_dir):
            #         tf.gfile.MakeDirs(tmp_dir)
        else:
            deleted_dir = '{}/deleted'.format(os.path.dirname(serializer.instance.rgb_source.path))
            if not tf.gfile.Exists(deleted_dir):
                tf.gfile.MakeDirs(deleted_dir)
            deleted_rgb = '{}/{}'.format(deleted_dir, os.path.basename(serializer.instance.rgb_source.path))
            shutil.move(serializer.instance.rgb_source.path, deleted_rgb)
            deleted_depth = '{}/{}'.format(deleted_dir, os.path.basename(serializer.instance.depth_source.path))
            shutil.move(serializer.instance.depth_source.path, deleted_depth)

        ret = []
        index = 0
        for min_rect in min_rectes:
            # 检测类型
            upcs = [0,]
            scores = [0,]

            min_upc = 'none'
            min_distance = 1000000
            if detector is not None:
                w = min_rect[1][0]
                h = min_rect[1][1]
                if w > h:
                    w = min_rect[1][1]
                    h = min_rect[1][0]
                for upc in detector:
                    upc_w = detector[upc][0]
                    upc_h = detector[upc][1]
                    distance = math.sqrt((w-upc_w)*(w-upc_w) + (h-upc_h)*(h-upc_h))
                    if distance < min_distance:
                        min_upc = upc
                        min_distance = distance
            # if detector is not None:
            #     oneimage = image.crop((boxes[index][0], boxes[index][1], boxes[index][2], boxes[index][3]))
            #     one_image_path = os.path.join(tmp_dir,'%d_%d.jpg' % (serializer.instance.pk, index))
            #     oneimage.save(one_image_path, 'JPEG')
            #     upcs, scores = detector.detect(one_image_path)
            #     shutil.move(one_image_path,os.path.join(tmp_dir,'%d_%d_%s_%.2f.jpg' % (serializer.instance.pk, index, upcs[0], scores[0])))


            logger.info('center: %d,%d; w*h:%d,%d; theta:%d; z:%d, boxes: x1:%d, y1:%d, x2:%d, y2:%d, type:%s, score:%.2f' % (
            min_rect[0][0], min_rect[0][1], min_rect[1][0], min_rect[1][1], min_rect[2], z[index], boxes[index][0],
            boxes[index][1], boxes[index][2], boxes[index][3], min_upc, min_distance))
            one = {
                'x': min_rect[0][0],
                'y': min_rect[0][1],
                'z': z[index]+z_deviation,
                'w': min_rect[1][0],
                'h': min_rect[1][1],
                'angle': min_rect[2],
                'box': {
                    'xmin':boxes[index][0],
                    'ymin': boxes[index][1],
                    'xmax': boxes[index][2],
                    'ymax': boxes[index][3],
                },
                'upc': min_upc,
                'distance': min_distance
            }
            ret.append(one)
            index += 1
        serializer.instance.result = json.dumps(ret, cls=NumpyEncoder)
        serializer.instance.save()

        time2 = time.time()
        logger.info('end detect arm: %.2f, %.2f, %.2f' % (time2-time0, time1-time0, time2-time1))
        return Response(ret, status=status.HTTP_201_CREATED, headers=headers)
