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

logger = logging.getLogger("django")

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
        detector = freezer2detection.ImageDetectorFactory.get_static_detector('freezer2')
        detect_ret, aiinterval, _ = detector.detect(serializer.instance.source.path, step1_min_score_thresh=0.3)

        ret = json.dumps(detect_ret, cls=NumpyEncoder)
        serializer.instance.ret = ret
        serializer.instance.save()

        logger.info('end detect:{}'.format(serializer.instance.deviceid))
        return Response(serializer.instance.ret, status=status.HTTP_201_CREATED, headers=headers)
