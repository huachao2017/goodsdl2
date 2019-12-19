import json
import logging

import requests
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *

logger = logging.getLogger("django")

class ShelfDisplayDebugViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    queryset = ShelfDisplayDebug.objects.order_by('-id')
    serializer_class = ShelfDisplayDebugSerializer
