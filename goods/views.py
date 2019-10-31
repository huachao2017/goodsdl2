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

logger = logging.getLogger("django")
from goods.freezer.keras_yolo3.yolo3 import yolo_freezer
from set_config import config
freezer_check_yolov3_switch = config.common_params['freezer_check_yolov3_switch']
# yolov3 = yolo_freezer.YOLO()
yolov3 = None
class Test(APIView):
    def get(self, request):
        print(request.query_params)
        import sys
        path = sys.path
        return Response({'Test': path})


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
class FreezerImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = FreezerImage.objects.order_by('-id')
    serializer_class = FreezerImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        logger.info('begin detect:{},{}'.format(serializer.instance.deviceid, serializer.instance.source.path))
        ret = []
        if freezer_check_yolov3_switch:
            detect_ret, aiinterval, visual_image_path = yolov3.detect(serializer.instance.source.path)
        else:
            detector = freezer2detection.ImageDetectorFactory.get_static_detector('freezer2')
            detect_ret, aiinterval, visual_image_path = detector.detect(serializer.instance.source.path, step1_min_score_thresh=0.3)

        ret = json.dumps(detect_ret, cls=NumpyEncoder)
        serializer.instance.ret = ret
        serializer.instance.visual = visual_image_path.replace(settings.MEDIA_ROOT,'')
        serializer.instance.save()

        logger.info('end detect:{}'.format(serializer.instance.deviceid))
        return Response(serializer.instance.ret, status=status.HTTP_201_CREATED, headers=headers)

class GoodsImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = GoodsImage.objects.order_by('-id')
    serializer_class = GoodsImageSerializer

    def create(self, request, *args, **kwargs):
        logger.info('begin detect goods:')
        time0 = time.time()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        z_deviation = 0 #10 # 60 # 10
        detect = Contour_3d(serializer.instance.rgb_source.path, serializer.instance.depth_source.path, serializer.instance.table_z-z_deviation,debug_type=2)
        min_rectes, z, boxes = detect.find_contour(False)

        time1 = time.time()

        index = 0
        for min_rect in min_rectes:
            w = min_rect[1][0]
            h = min_rect[1][1]
            if w > h:
                w = min_rect[1][1]
                h = min_rect[1][0]


            logger.info('center: %d,%d; w*h:%d,%d; theta:%d; z:%d, ' % (
            min_rect[0][0], min_rect[0][1], w, h, min_rect[2], z[index]))
            one = {
                'x': min_rect[0][0],
                'y': min_rect[0][1],
                'z': z[index]+z_deviation,
                'w': w,
                'h': h,
                'angle': min_rect[2]
            }
            ret = one
            index += 1
            break # 只采用一个商品
        serializer.instance.result = json.dumps(ret, cls=NumpyEncoder)
        serializer.instance.save()

        time2 = time.time()
        logger.info('end detect goods: %.2f, %.2f, %.2f' % (time2-time0, time1-time0, time2-time1))
        return Response(ret, status=status.HTTP_201_CREATED, headers=headers)
