import logging
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
