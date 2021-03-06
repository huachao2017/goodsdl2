import datetime
import json
import logging
import math
import os
import urllib.request
from PIL import Image
import subprocess
import base64
import cv2
import numpy as np
import traceback
import tensorflow as tf
from PIL import Image as PILImage
from django.conf import settings
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from dl import shelfdetection
from dl.util import caculate_level
from goods.shelfgoods.service import tz_good_compare
from goods.util import shelf_visualize
from .serializers import *
from goods.shelfgoods.imgsearch.aliyun.search import ImgSearch
from goods.shelfgoods.imgsearch.baidu_ai.search import ImgSearch_02

# from goods.freezer.keras_yolo3.yolo3 import yolo_shelf
logger = logging.getLogger("django")
# yolo_ins = yolo_shelf.YOLO()

class DefaultMixin:
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100


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

def detect_compare(shelf_image, image_path, need_detect = True, need_notify = False, label_goods = None):
    shelf_goods_map = {}
    if need_detect:
        # 删除旧的goods
        ShelfGoods.objects.filter(shelf_image_id=shelf_image.pk).delete()

        logger.info('begin detect:{}'.format(image_path))
        # 检测框
        detector = shelfdetection.ShelfDetectorFactory.get_static_detector('shelf')
        step1_min_score_thresh = .5
        detect_ret = detector.detect(image_path,step1_min_score_thresh=step1_min_score_thresh)
        if len(detect_ret) > 0:
            caculate_level(detect_ret, shelf_image.tlevel)

        for one_box in detect_ret:
            shelf_goods = ShelfGoods.objects.create(
                shelf_image_id=shelf_image.pk,
                xmin=one_box['xmin'],
                ymin=one_box['ymin'],
                xmax=one_box['xmax'],
                ymax=one_box['ymax'],
                level=one_box['level'],
            )
            shelf_goods_map[shelf_goods.pk] = shelf_goods
        logger.info('end detect:{}'.format(image_path))
    else:
        shelf_goods_list = shelf_image.shelf_image_goods.all()
        for shelf_goods in shelf_goods_list:
            shelf_goods_map[shelf_goods.pk] = shelf_goods

    # 比对获取结果
    logger.info('begin compare:{}'.format(image_path))
    if label_goods == None or label_goods.upc == '':
        compare_ret = tz_good_compare.compare(shelf_image.pk, shelf_image.displayid, shelf_image.shelfid)
    else:
        # TODO 需要优化成单个商品更新，提升效率
        compare_ret = tz_good_compare.compare(shelf_image.pk, shelf_image.displayid, shelf_image.shelfid, upcs=[label_goods.upc])
    logger.info('end compare:{}'.format(compare_ret))
    # 持久化
    if compare_ret is not None:
        # 生成识别图
        if len(compare_ret['detail']) > 0:
            result_image_name = shelf_visualize(compare_ret['detail'], image_path)
            image_relative_dir = os.path.split(shelf_image.source)[0]
            shelf_image.resultsource = os.path.join(image_relative_dir, result_image_name)

        shelf_image.score = compare_ret['score']
        shelf_image.equal_cnt = compare_ret['equal_cnt']
        shelf_image.different_cnt = compare_ret['different_cnt']
        shelf_image.unknown_cnt = compare_ret['unknown_cnt']
        shelf_image.save()
        for one in compare_ret['detail']:
            shelf_goods = shelf_goods_map[one['boxid']]
            # 以标注的商品为准
            if not shelf_goods.is_label:
                shelf_goods.result = one['result']
                shelf_goods.process_code = one['process_code']
                shelf_goods.row = one['row']
                shelf_goods.col = one['col']
                if shelf_goods.result == 0:
                    # TODO 如果前后两个upc不相同，有可能冲掉用户标注的数据
                    shelf_goods.upc = one['upc']
                else:
                    shelf_goods.upc = ''
                shelf_goods.save()
    if need_notify:
        notify_result(shelf_image)

    return compare_ret


def notify_result(shelf_image):
    # 测试环境：http: // alphataizhang.aicvs.cn / m / shelf / updateScore?picid = xxx & score = xxx & retpicurl = xxx & equal_cnt = 1 & different_cnt = 2 & unknown_cnt = 3
    # 产线环境：http: // taizhang.aicvs.cn / m / shelf / updateScore?picid = xxx & score = xxx & retpicurl = xxx & equal_cnt = 1 & different_cnt = 2 & unknown_cnt = 3

    request_param = 'picid={}&shopid={}&displayid={}&shelfid={}&score={}&retpicurl={}&equal_cnt={}&different_cnt={}&unknown_cnt={}'.format(
        shelf_image.picid,
        shelf_image.shopid,
        shelf_image.displayid,
        shelf_image.shelfid,
        shelf_image.score,
        os.path.join(settings.MEDIA_URL, shelf_image.resultsource),
        shelf_image.equal_cnt,
        shelf_image.different_cnt,
        shelf_image.unknown_cnt
    )
    logger.info('notify_result request_param:{}'.format(request_param))
    if shelf_image.test_server:
        res = urllib.request.urlopen('http://alphataizhang.aicvs.cn/m/shelf/updateScore?' + request_param)
    else:
        res = urllib.request.urlopen('http://taizhang.aicvs.cn/m/shelf/updateScore?' + request_param)

    logger.info('notify_result response:{}'.format(res.read()))

class ShelfScore(APIView):
    def get(self, request):
        picurl = request.query_params['picurl']
        try:
            picid = int(request.query_params['picid'])
            shopid = int(request.query_params['shopid'])
            shelfid = request.query_params['shelfid']
            displayid = int(request.query_params['displayid'])
            tlevel = int(request.query_params['tlevel'])
            if 'debug' in request.query_params and request.query_params['debug'] == '0':
                test_server = False
            else:
                test_server = True
        except Exception as e:
            logger.error('Shelf score error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        # 获取图片
        now = datetime.datetime.now()
        image_relative_dir = os.path.join(settings.DETECT_DIR_NAME, 'shelf', now.strftime('%Y%m'),now.strftime('%d%H'))
        image_dir = os.path.join(settings.MEDIA_ROOT, image_relative_dir)
        if not tf.gfile.Exists(image_dir):
            tf.gfile.MakeDirs(image_dir)
        source_image_name = '{}_{}_{}.jpg'.format(shopid,shelfid,now.strftime('%M%S'))
        source_image_path = os.path.join(image_dir, source_image_name)
        urllib.request.urlretrieve(picurl, source_image_path)

        shelf_image = ShelfImage.objects.create(
            picid=picid,
            shopid=shopid,
            shelfid=shelfid,
            displayid=displayid,
            tlevel=tlevel,
            picurl=picurl,
            source=os.path.join(image_relative_dir,source_image_name),
            test_server=test_server
        )
        # command = "nohup python3 {}/goods/shelf_recoginze/main_service.py --imageid={} > {}/logs/shelf_recognize.out 2>&1 &".format(
        #     settings.BASE_DIR,
        #     shelf_image.pk,
        #     settings.BASE_DIR
        # )
        #
        # # 启动训练进程
        # logger.info(command)
        # subprocess.call(command, shell=True)
        # ret = ''
        compare_ret = detect_compare(shelf_image, source_image_path)

        retpicurl = ''
        if shelf_image.resultsource != '':
            retpicurl = os.path.join(settings.MEDIA_URL, shelf_image.resultsource)
        ret = {
            'score':shelf_image.score,
            "equal_cnt":shelf_image.equal_cnt,
            "different_cnt":shelf_image.different_cnt,
            "unknown_cnt":shelf_image.unknown_cnt,
            'retpicurl':retpicurl

        }
        return Response(ret, status=status.HTTP_200_OK)


class RectifyAndDetect(APIView):
    def get(self, request):
        try:
            x1 = int(request.query_params['x1'])
            y1 = int(request.query_params['y1'])
            x2 = int(request.query_params['x2'])
            y2 = int(request.query_params['y2'])
            x3 = int(request.query_params['x3'])
            y3 = int(request.query_params['y3'])
            x4 = int(request.query_params['x4'])
            y4 = int(request.query_params['y4'])
            picid = int(request.query_params['picid'])
            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('Rectify and detect error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        if x1>x2:
            xt = x1
            yt = y1
            x1 = x2
            y1 = y2
            x2 = xt
            y2 = yt
        if x3>x4:
            xt = x3
            yt = y3
            x3 = x4
            y3 = y4
            x4 = xt
            y4 = yt

        height = abs(y1-y3) # 800
        width = int(height * math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) / math.sqrt((x1-x3)*(x1-x3)+(y1-y3)*(y1-y3)))


        now = datetime.datetime.now()
        # 通过数据库获取图片
        image_relative_dir = os.path.split(shelf_image.source)[0]
        source_image_name = os.path.split(shelf_image.source)[1]
        image_dir = os.path.join(settings.MEDIA_ROOT, image_relative_dir)
        source_image_path = os.path.join(settings.MEDIA_ROOT,shelf_image.source)

        rectify_image_name = 'rectify_{}'.format(source_image_name)
        rectify_image_path = os.path.join(image_dir, rectify_image_name)
        img = cv2.imread(source_image_path)
        # rows, cols = img.shape[:2]
        # 原图中书本的四个角点
        pts1 = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        # 变换后分别在左上、右上、左下、右下四个点
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        # 生成透视变换矩阵
        M = cv2.getPerspectiveTransform(pts1, pts2)
        # 进行透视变换
        dst = cv2.warpPerspective(img, M, (width, height))
        cv2.imwrite(rectify_image_path,dst)

        shelf_image.rectjson = json.dumps({
            "x1":x1,
            "y1":y1,
            "x2":x2,
            "y2":y2,
            "x3":x3,
            "y3":y3,
            "x4":x4,
            "y4":y4})
        shelf_image.rectsource = os.path.join(image_relative_dir, rectify_image_name)
        shelf_image.save()

        compare_ret = detect_compare(shelf_image, rectify_image_path, need_notify=True)

        return Response(compare_ret, status=status.HTTP_200_OK)


class GetShelfImage(APIView):
    def get(self, request):
        try:
            picid = int(request.query_params['picid'])
            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('GetShelfImage error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.source)
        image = PILImage.open(image_path)
        (im_width, im_height) = image.size
        ret = {
            "url": os.path.join(settings.MEDIA_URL, shelf_image.source),
            "width": im_width,
            "height": im_height,
        }
        if shelf_image.rectjson != '':
            rect = json.loads(shelf_image.rectjson)
            ret.update(rect)
        return Response(ret, status=status.HTTP_200_OK)


class GetShelfImageDetail(APIView):
    def get(self, request):
        try:
            picid = int(request.query_params['picid'])
            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('GetShelfImageDetail error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        detail = []
        shelf_goods_list = shelf_image.shelf_image_goods.all()
        for shelf_goods in shelf_goods_list:
            detail.append({
                'level': shelf_goods.level,
                'xmin': shelf_goods.xmin,
                'ymin': shelf_goods.ymin,
                'xmax': shelf_goods.xmax,
                'ymax': shelf_goods.ymax,
                'result': shelf_goods.result,
                'boxid': shelf_goods.pk,
                'upc': shelf_goods.upc
            })

        image_relative_path = shelf_image.rectsource
        if image_relative_path == '':
            image_relative_path = shelf_image.source
        image_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)
        image = PILImage.open(image_path)
        (im_width, im_height) = image.size
        ret = {
            "recturl":os.path.join(settings.MEDIA_URL,image_relative_path),
            "rectwidth": im_width,
            "rectheight": im_height,
            "score":shelf_image.score,
            "equal_cnt":shelf_image.equal_cnt,
            "different_cnt":shelf_image.different_cnt,
            "unknown_cnt":shelf_image.unknown_cnt,
            "displayurl":get_display_url(shelf_image.displayid,shelf_image.shelfid),
            "detail":detail
        }
        return Response(ret, status=status.HTTP_200_OK)

def get_display_url(displayid, shelfid):
    try:
        url = ''
        from django.db import connections
        # TODO 需要切换正式和测试服务器
        cursor = connections['ucenter'].cursor()
        cursor.execute("select tmp_display_img_list from sf_taizhang_display where id = {}".format(displayid))
        raw = cursor.fetchone()
        if len(raw) == 1:
            url = 'http://lximages.xianlife.com/'
            shelfid_to_url = json.loads(raw[0])
            url += shelfid_to_url[shelfid]
        return url
    except Exception as e:
        logger.error('caculate level error:{}'.format(e))
        traceback.print_exc()
    return ''


class DetectShelfImage(APIView):
    def get(self, request):
        try:
            picid = int(request.query_params['picid'])
            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('Rectify and detect error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        if shelf_image.rectsource != '':
            image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.rectsource)
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.source)
        compare_ret = detect_compare(shelf_image, image_path, need_detect = False, need_notify=True)
        return Response(compare_ret, status=status.HTTP_200_OK)


class ShelfImageViewSet(DefaultMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = ShelfImage.objects.order_by('-id')
    serializer_class = ShelfImageSerializer


class ShelfGoodsViewSet(DefaultMixin, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = ShelfGoods.objects.order_by('-id')
    serializer_class = ShelfGoodsSerializer

    def create(self, request, *args, **kwargs):
        try:
            picid = int(request.data['picid'])
            xmin = int(request.data['xmin'])
            ymin = int(request.data['ymin'])
            xmax = int(request.data['xmax'])
            ymax = int(request.data['ymax'])
            if xmin > xmax or ymin > ymax:
                raise ValueError("position error")

            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('Rectify and detect error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        # 需要计算层数
        boxes = []
        # 新增的添加在第一条
        boxes.append({
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
            'level': -1,
        })
        shelf_goods_list = shelf_image.shelf_image_goods.all()
        for shelf_goods in shelf_goods_list:
            boxes.append({
                'level': shelf_goods.level,
                'xmin': shelf_goods.xmin,
                'ymin': shelf_goods.ymin,
                'xmax': shelf_goods.xmax,
                'ymax': shelf_goods.ymax,
            })
        caculate_level(boxes, shelf_image.tlevel)
        shelf_goods = ShelfGoods.objects.create(
            shelf_image_id=shelf_image.pk,
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
            level=boxes[0]['level'],
        )

        return Response({'boxid':shelf_goods.pk}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_result = instance.result
        old_upc = instance.upc

        if 'xmin' in request.data and 'xmax' in request.data and 'ymin' in request.data and 'ymax' in request.data:
            if int(request.data['xmin']) > int(request.data['xmax']) or int(request.data['ymin']) > int(request.data['ymax']):
                raise ValueError("position error")
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)


        result = serializer.instance.result
        logger.info(serializer.instance)
        if result == 1:
            if old_result == 0 and old_upc != '':
                sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
                if not tf.gfile.Exists(sample_dir):
                    tf.gfile.MakeDirs(sample_dir)
                old_sample_path = os.path.join(sample_dir, old_upc, '{}.jpg'.format(serializer.instance.pk))
                if os.path.isfile(old_sample_path):
                    # 删除原来的样本
                    os.remove(old_sample_path)
                serializer.instance.is_label = True
                # serializer.instance.upc = ''
                serializer.instance.save()
                img_search = ImgSearch()
                img_search.delete_img(old_upc,str(serializer.instance.pk))

                if serializer.instance.baidu_code != '':
                    imgsearch_02 = ImgSearch_02()
                    imgsearch_02.delete_img(serializer.instance.baidu_code)


        elif result == 0:
            # 计算upc
            upc = tz_good_compare.get_upc(
                serializer.instance.shelf_image.displayid,
                serializer.instance.shelf_image.shelfid,
                serializer.instance.shelf_image.pk,
                serializer.instance.pk)

            if upc is not None and upc != '':
                # 添加新样本
                sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
                if serializer.instance.shelf_image.rectsource != '':
                    image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.rectsource)
                else:
                    image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.source)
                upc_sample_dir = os.path.join(sample_dir,upc)
                if not tf.gfile.Exists(upc_sample_dir):
                    tf.gfile.MakeDirs(upc_sample_dir)

                image = PILImage.open(image_path)
                sample_image = image.crop((serializer.instance.xmin, serializer.instance.ymin, serializer.instance.xmax, serializer.instance.ymax))
                sample_image_path = os.path.join(upc_sample_dir, '{}.jpg'.format(serializer.instance.pk))
                logger.info("add upc image ,filepath="+str(sample_image_path))
                sample_image.save(sample_image_path, 'JPEG')
                serializer.instance.upc = upc
                serializer.instance.is_label = True
                serializer.instance.save()
                img_search = ImgSearch()
                img_search.add_img(upc,str(serializer.instance.pk),sample_image_path)

                imgsearch_02 = ImgSearch_02()
                baidu_code = imgsearch_02.add_img(upc, str(serializer.instance.pk),sample_image_path)
                if baidu_code is not None:
                    serializer.instance.baidu_code = baidu_code
                    serializer.instance.save()
            else:
                logger.error('get_upc is None')

        # compare_ret = tz_good_compare.level_compare(
        #     serializer.instance.shelf_image.displayid,
        #     serializer.instance.shelf_image.shelfid,
        #     serializer.instance.shelf_image.pk,
        #     serializer.instance.pk)

        if serializer.instance.shelf_image.rectsource != '':
            image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.rectsource)
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.source)
        compare_ret = detect_compare(serializer.instance.shelf_image, image_path, need_detect=False, need_notify=True, label_goods=serializer.instance)
        if result == 1:
            serializer.instance.upc = ''
            serializer.instance.save()

        return Response(compare_ret)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
        # 删除原来的样本
        old_sample_path = os.path.join(sample_dir, instance.upc, '{}.jpg'.format(instance.pk))
        if os.path.isfile(old_sample_path):
            os.remove(old_sample_path)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

#
#
# class ShelfAndNullBoxDetect(APIView):
#     def get(self, request):
#         ret = {}
#         try:
#             traceId = int(request.query_params['traceId'])
#             img_base64 = int(request.query_params['img_base64'])
#             imgBuf = base64.b64decode(img_base64)
#             img = cv2.imdecode(np.frombuffer((imgBuf), dtype=np.uint8),
#                                cv2.IMREAD_COLOR)
#             img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#             classes,scores,locations = yolo_ins.predict_img(img)
#             ret = {
#                 'classes':classes,
#                 'scores':scores,
#                 'locations':locations
#             }
#             logger.info("ShelfAndNullBoxDetect traceId={},ret={}".format(traceId,ret))
#         except Exception as e:
#             logger.error('ShelfAndNullBoxDetect error:{}'.format(e))
#             return Response(-1, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response(ret, status=status.HTTP_200_OK)
