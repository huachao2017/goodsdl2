import json
import logging
import time
from rest_framework.response import Response
from rest_framework import status

import numpy as np
from rest_framework.views import APIView

logger = logging.getLogger("django")

g_data = [
  ('00', 0, 0),
  ('01', 3, 2),
  ('02', 3, 1),
  ('03', 2, 2),
  ('04', 12, 8),
  ('05', 19, 15),
  ('06', 40, 27),
  ('07', 82, 60),
  ('08', 240, 192),
  ('09', 382, 283),
  ('10', 377, 260),
  ('11', 332, 265),
  ('12', 301, 221),
  ('13', 233, 173),
  ('14', 223, 172),
  ('15', 278, 201),
  ('16', 302, 228),
  ('17', 220, 166),
  ('18', 210, 154),
  ('19', 122, 88),
  ('20', 62, 51),
  ('21', 32, 21),
  ('22', 21, 15),
  ('23', 4, 2),
]


class Interface1(APIView):
  def get(self, request):
    cur_hour = time.strftime('%H', time.localtime(time.time()))
    value = 0
    for i in range(cur_hour - 1):
      value += g_data[i][1]
    ret = [
      {
        "name": "",
        "number": value,
        "value": value
      }
    ]
    return Response(ret, status=status.HTTP_200_OK)


class Interface2(APIView):
  def get(self, request):
    cur_hour = time.strftime('%H', time.localtime(time.time()))
    paymentRate = 0
    faceRate = 0
    for i in range(cur_hour - 1):
      faceRate += g_data[i][1]
      paymentRate += g_data[i][2]
    ret = [
      {
        "paymentRate": paymentRate,
        "faceRate": faceRate,
        "conversionRate": '{}%'.format(int(paymentRate * 100 / faceRate))
      }
    ]
    return Response(ret, status=status.HTTP_200_OK)


class Interface3(APIView):
  def get(self, request):
    cur_hour = time.strftime('%H', time.localtime(time.time()))
    ret = []
    for i in range(cur_hour - 1):
      ret.append({
        'x':g_data[i][0],
        'y':g_data[i][1]
      })
    return Response(ret, status=status.HTTP_200_OK)


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
