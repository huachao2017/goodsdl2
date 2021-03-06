import logging
import os
import shutil
import time
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
import urllib.request
import urllib.parse
import requests
import traceback
from django.db import connections

logger = logging.getLogger("django")
from goods.freezer.keras_yolo3.yolo3 import yolo_freezer
from goods.freezer.keras_yolo3.yolo3 import yolo_mengniu
from set_config import config
freezer_check_yolov3_switch = config.common_params['freezer_check_yolov3_switch']
# yolov3 = yolo_freezer.YOLO()
yolov3 = None
# mengniu_yolov3 = yolo_mengniu.YOLO()
mengniu_yolov3 = None
class Test(APIView):
    def get(self, request):
        url = "https://autodisplay:xianlife2018@taizhang.aicvs.cn/api/autoDisplay"
        print(url)
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json"
        }

        a = '{"taizhang_id": 1199, "shelfs": [{"shelf_id": 1100, "levels": [{"level_id": 0, "height": 50, "goods": [{"mch_good_code": "2004638", "upc": "6954767413877", "width": 108, "height": 338, "depth": 108, "displays": [{"top": 338, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2004092", "upc": "6921168520015", "width": 85, "height": 325, "depth": 85, "displays": [{"top": 325, "left": 108, "row": 0, "col": 0}, {"top": 325, "left": 193, "row": 0, "col": 1}, {"top": 325, "left": 278, "row": 0, "col": 2}, {"top": 325, "left": 363, "row": 0, "col": 3}]}, {"mch_good_code": "2019540", "upc": "6921581540270", "width": 63, "height": 220, "depth": 63, "displays": [{"top": 220, "left": 448, "row": 0, "col": 0}]}, {"mch_good_code": "2042696", "upc": "6917878054780", "width": 56, "height": 164, "depth": 56, "displays": [{"top": 164, "left": 511, "row": 0, "col": 0}]}, {"mch_good_code": "2021662", "upc": "6917878030623", "width": 58, "height": 166, "depth": 58, "displays": [{"top": 166, "left": 567, "row": 0, "col": 0}]}, {"mch_good_code": "2035957", "upc": "6921168593811", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 625, "row": 0, "col": 0}]}, {"mch_good_code": "2035958", "upc": "6921168593804", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 678, "row": 0, "col": 0}]}, {"mch_good_code": "2037750", "upc": "6921168593880", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 731, "row": 0, "col": 0}]}, {"mch_good_code": "2034860", "upc": "898999000022", "width": 55, "height": 145, "depth": 55, "displays": [{"top": 145, "left": 784, "row": 0, "col": 0}]}]}, {"level_id": 1, "height": 438, "goods": [{"mch_good_code": "2026210", "upc": "6921168558049", "width": 60, "height": 204, "depth": 60, "displays": [{"top": 204, "left": 0, "row": 0, "col": 0}, {"top": 204, "left": 60, "row": 0, "col": 1}, {"top": 204, "left": 120, "row": 0, "col": 2}]}, {"mch_good_code": "2044244", "upc": "6972215667535", "width": 60, "height": 225, "depth": 60, "displays": [{"top": 225, "left": 180, "row": 0, "col": 0}]}, {"mch_good_code": "2044180", "upc": "6956416205956", "width": 55, "height": 210, "depth": 55, "displays": [{"top": 210, "left": 240, "row": 0, "col": 0}]}, {"mch_good_code": "2043144", "upc": "8806002016917", "width": 72, "height": 209, "depth": 72, "displays": [{"top": 209, "left": 295, "row": 0, "col": 0}]}, {"mch_good_code": "2029398", "upc": "6905069200030", "width": 70, "height": 209, "depth": 70, "displays": [{"top": 209, "left": 367, "row": 0, "col": 0}]}, {"mch_good_code": "2034858", "upc": "6927216920011", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 437, "row": 0, "col": 0}]}, {"mch_good_code": "2034859", "upc": "6927216920059", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 512, "row": 0, "col": 0}]}, {"mch_good_code": "2042505", "upc": "6938888889803", "width": 88, "height": 155, "depth": 88, "displays": [{"top": 155, "left": 587, "row": 0, "col": 0}]}, {"mch_good_code": "2045483", "upc": "6907305713328", "width": 70, "height": 145, "depth": 70, "displays": [{"top": 145, "left": 675, "row": 0, "col": 0}]}]}, {"level_id": 2, "height": 713, "goods": [{"mch_good_code": "2004998", "upc": "6921581596048", "width": 65, "height": 209, "depth": 65, "displays": [{"top": 209, "left": 0, "row": 0, "col": 0}, {"top": 209, "left": 65, "row": 0, "col": 1}, {"top": 209, "left": 130, "row": 0, "col": 2}]}, {"mch_good_code": "2005413", "upc": "6925303721367", "width": 66, "height": 220, "depth": 66, "displays": [{"top": 220, "left": 195, "row": 0, "col": 0}]}, {"mch_good_code": "2003963", "upc": "4891599338393", "width": 65, "height": 115, "depth": 65, "displays": [{"top": 115, "left": 261, "row": 0, "col": 0}]}, {"mch_good_code": "2040855", "upc": "6917878056197", "width": 52, "height": 119, "depth": 52, "displays": [{"top": 119, "left": 326, "row": 0, "col": 0}]}, {"mch_good_code": "2044181", "upc": "4897036691175", "width": 52, "height": 120, "depth": 52, "displays": [{"top": 120, "left": 378, "row": 0, "col": 0}]}, {"mch_good_code": "2004353", "upc": "6920202888883", "width": 64, "height": 91, "depth": 64, "displays": [{"top": 91, "left": 430, "row": 0, "col": 0}]}, {"mch_good_code": "2012607", "upc": "6920180209601", "width": 65, "height": 115, "depth": 65, "displays": [{"top": 115, "left": 494, "row": 0, "col": 0}]}, {"mch_good_code": "2044177", "upc": "6954767417684", "width": 56, "height": 145, "depth": 56, "displays": [{"top": 145, "left": 559, "row": 0, "col": 0}, {"top": 145, "left": 615, "row": 0, "col": 1}]}, {"mch_good_code": "2043574", "upc": "6970399920415", "width": 66, "height": 205, "depth": 66, "displays": [{"top": 205, "left": 671, "row": 0, "col": 0}, {"top": 205, "left": 737, "row": 0, "col": 1}]}]}, {"level_id": 3, "height": 983, "goods": [{"mch_good_code": "2018241", "upc": "6902538005141", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2004326", "upc": "6902538004045", "width": 73, "height": 209, "depth": 73, "displays": [{"top": 209, "left": 75, "row": 0, "col": 0}]}, {"mch_good_code": "2025479", "upc": "6921168550098", "width": 66, "height": 190, "depth": 66, "displays": [{"top": 190, "left": 148, "row": 0, "col": 0}]}, {"mch_good_code": "2025480", "upc": "6921168550128", "width": 66, "height": 190, "depth": 66, "displays": [{"top": 190, "left": 214, "row": 0, "col": 0}]}, {"mch_good_code": "2026253", "upc": "6922255451427", "width": 60, "height": 230, "depth": 60, "displays": [{"top": 230, "left": 280, "row": 0, "col": 0}, {"top": 230, "left": 340, "row": 0, "col": 1}]}, {"mch_good_code": "2004083", "upc": "6921168509256", "width": 62, "height": 229, "depth": 62, "displays": [{"top": 229, "left": 400, "row": 0, "col": 0}, {"top": 229, "left": 462, "row": 0, "col": 1}, {"top": 229, "left": 524, "row": 0, "col": 2}, {"top": 229, "left": 586, "row": 0, "col": 3}]}, {"mch_good_code": "2021612", "upc": "6906907907012", "width": 58, "height": 240, "depth": 58, "displays": [{"top": 240, "left": 648, "row": 0, "col": 0}, {"top": 240, "left": 706, "row": 0, "col": 1}]}, {"mch_good_code": "2019634", "upc": "6954767423579", "width": 64, "height": 232, "depth": 64, "displays": [{"top": 232, "left": 764, "row": 0, "col": 0}, {"top": 232, "left": 828, "row": 0, "col": 1}]}]}, {"level_id": 4, "height": 1273, "goods": [{"mch_good_code": "2043903", "upc": "6902538007664", "width": 70, "height": 210, "depth": 70, "displays": [{"top": 210, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2009198", "upc": "6932529211107", "width": 65, "height": 212, "depth": 65, "displays": [{"top": 212, "left": 70, "row": 0, "col": 0}]}, {"mch_good_code": "2013136", "upc": "6902083886455", "width": 67, "height": 197, "depth": 67, "displays": [{"top": 197, "left": 135, "row": 0, "col": 0}]}, {"mch_good_code": "2023591", "upc": "6925303730574", "width": 55, "height": 219, "depth": 55, "displays": [{"top": 219, "left": 202, "row": 0, "col": 0}]}, {"mch_good_code": "2044894", "upc": "4710094106118", "width": 67, "height": 225, "depth": 67, "displays": [{"top": 225, "left": 257, "row": 0, "col": 0}]}, {"mch_good_code": "2036473", "upc": "6921581597076", "width": 82, "height": 285, "depth": 82, "displays": [{"top": 285, "left": 324, "row": 0, "col": 0}]}, {"mch_good_code": "2041439", "upc": "6921317998825", "width": 100, "height": 310, "depth": 90, "displays": [{"top": 310, "left": 406, "row": 0, "col": 0}]}, {"mch_good_code": "2020054", "upc": "6921168500956", "width": 64, "height": 200, "depth": 64, "displays": [{"top": 200, "left": 506, "row": 0, "col": 0}]}, {"mch_good_code": "2031718", "upc": "6921168559244", "width": 64, "height": 200, "depth": 64, "displays": [{"top": 200, "left": 570, "row": 0, "col": 0}]}, {"mch_good_code": "2030338", "upc": "6922279400265", "width": 65, "height": 203, "depth": 65, "displays": [{"top": 203, "left": 634, "row": 0, "col": 0}]}, {"mch_good_code": "2032659", "upc": "6921581540089", "width": 61, "height": 223, "depth": 61, "displays": [{"top": 223, "left": 699, "row": 0, "col": 0}]}]}]}]}'
        json_info = json.dumps(a)
        data = bytes(json_info, 'utf8')
        resp = requests.post(url=url,data=data,headers=headers)
        print(resp)
        # request = urllib.request.Request(url=url, data=data, headers=headers)

        # response = urllib.request.urlopen(request)
        # print(response.read().decode())
        return Response()


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

class FreezerImageViewSet1(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    # queryset = FreezerImage.objects.order_by('-id')
    serializer_class = FreezerImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        logger.info('begin detect:{},{}'.format(serializer.instance.deviceid, serializer.instance.source.path))
        ret = []
        ret = json.dumps(ret, cls=NumpyEncoder)
        logger.info('end detect:{}'.format(serializer.instance.deviceid))
        return Response(serializer.instance.ret, status=status.HTTP_201_CREATED, headers=headers)

class MengniuFreezerImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = MengniuFreezerImage.objects.order_by('-id')
    serializer_class = MengniuFreezerImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        logger.info('begin detect:{},{}'.format(serializer.instance.deviceid, serializer.instance.source.path))
        ret = []
        detect_ret, aiinterval, visual_image_path = mengniu_yolov3.detect(serializer.instance.source.path)

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

class AllWorkFlowBatchViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = AllWorkFlowBatch.objects.order_by('-id')
    serializer_class = AllWorkFlowBatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response('OK', status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # TODO 开始陈列


        # TODO 开始订货
        return Response(serializer.data)

class BeginSelectGoods(APIView):
    def get(self, request):
        try:
            uc_shopid = int(request.query_params['ucshopid'])
            batch_id = request.query_params['batchid']
            workflow = AllWorkFlowBatch.objects.create(
                uc_shopid=uc_shopid,
                batch_id=batch_id,
                type=0,
                select_goods_status = 1
            )
        except Exception as e:
            logger.error('BeginSelectGoods error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)
        # TODO 开始选品
        return Response()


class BeginAutoDisplay(APIView):
    def get(self, request):
        try:
            uc_shopid = int(request.query_params['ucshopid'])
            batch_id = request.query_params['batchid']
            workflow = AllWorkFlowBatch.objects.filter(uc_shopid=uc_shopid).filter(batch_id=batch_id).filter(type=0).get()
            workflow.auto_display_status = 1
            workflow.save()
        except Exception as e:
            logger.error('BeginAutoDisplay error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        # TODO 开始陈列
        return Response()


class BeginOrderGoods(APIView):
    def get(self, request):
        cursor = connections['ucenter'].cursor()
        cursor_dmstore = connections['dmstore'].cursor()
        try:
            batch_id = request.query_params['batchid']
            type = int(request.query_params['type'])

            if type == 1:
                if 'erpwarehouseid' in request.query_params:
                    erp_warehouse_id = int(request.query_params['erpwarehouseid'])
                    # 临时计算uc_shopid
                    # cursor_dmstore.execute("select shop_id from erp_shop_related where erp_shop_id = {} and erp_shop_type = 1".format(erp_warehouse_id))
                    # (shop_id,) = cursor_dmstore.fetchone()
                    # cursor.execute("select id,mch_id from uc_shop where mch_shop_code = {}".format(shop_id))
                    # (uc_shopid, mch_id) = cursor.fetchone()
                    workflow = AllWorkFlowBatch.objects.create(
                        erp_warehouse_id = erp_warehouse_id,
                        uc_shopid=0,
                        batch_id=batch_id,
                        type=type,
                        select_goods_status = 0,
                        order_goods_status=1
                    )
                else:
                    # 兼容旧的接口
                    uc_shopid = int(request.query_params['ucshopid'])
                    workflow = AllWorkFlowBatch.objects.create(
                        uc_shopid=uc_shopid,
                        batch_id=batch_id,
                        type=type,
                        select_goods_status = 0,
                        order_goods_status=1
                    )

            elif type == 2:
                uc_shopid = int(request.query_params['ucshopid'])
                workflow = AllWorkFlowBatch.objects.create(
                    uc_shopid=uc_shopid,
                    batch_id=batch_id,
                    type=type,
                    select_goods_status = 0,
                    order_goods_status=1
                )
            else:
                return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error('BeginOrderGoods error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)
        finally:
            cursor.close()
            cursor_dmstore.close()

        return Response()

class OrderConfirm(APIView):
    def post(self, request):
        try:
            erp_warehouse_id = int(request.query_params['erpwarehouseid'])
            batch_id = request.query_params['batchid']
            logger.info(erp_warehouse_id)
            logger.info(batch_id)
            logger.info(request.data)
            logger.info(type(request.data))


            # TODO 调用计算方法

            return Response(erp_warehouse_id, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error('OrderConfirm error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)
