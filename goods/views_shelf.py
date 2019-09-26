import datetime
import json
import logging
import os
import urllib.request
from PIL import Image as PILImage

import numpy as np
from django.conf import settings
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
import cv2
import math

from dl import shelfdetection
from goods.shelfgoods.service import tz_good_compare
from .serializers import *
import tensorflow as tf
from dl.util import caculate_level
from dl.util import visualize_boxes_and_labels_on_image_array_for_shelf

logger = logging.getLogger("django")

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

def detect_compare(shelf_image, image_path, need_detect = True):
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
    compare_ret = tz_good_compare.compare(shelf_image.pk, shelf_image.displayid, shelf_image.shelfid)
    logger.info('end compare:{}'.format(compare_ret))
    # 持久化
    if compare_ret is not None:
        # 生成识别图
        if len(compare_ret['detail']) > 0:
            image = PILImage.open(image_path)
            text_infos = []
            color_infos = []
            for one in compare_ret['detail']:
                text_infos.append('{}-{}'.format(one['level'], one['upc']))
                color = 'black'
                if one['result'] == 0:
                    color = 'blue'
                elif one['result'] == 1 or one['result'] == 2:
                    color = 'red'
                color_infos.append(color)
            visualize_boxes_and_labels_on_image_array_for_shelf(
                np.array(image),
                compare_ret['detail'],
                text_infos,
                color_infos
            )
            image_relative_dir = os.path.split(shelf_image.source)[0]
            image_dir = os.path.dirname(image_path)
            result_image_name = 'visual_' + os.path.split(image_path)[-1]
            result_image_path = os.path.join(image_dir, result_image_name)
            (im_width, im_height) = image.size
            image.thumbnail((int(im_width), int(im_height)), PILImage.ANTIALIAS)
            image.save(result_image_path)
            shelf_image.resultsource = os.path.join(image_relative_dir, result_image_name)

        shelf_image.score = compare_ret['score']
        shelf_image.equal_cnt = compare_ret['equal_cnt']
        shelf_image.different_cnt = compare_ret['different_cnt']
        shelf_image.unknown_cnt = compare_ret['unknown_cnt']
        shelf_image.save()
        for one in compare_ret['detail']:
            shelf_goods = shelf_goods_map[one['boxid']]
            shelf_goods.result = one['result']
            if shelf_goods.result == 0:
                # TODO 如果前后两个upc不相同，有可能冲掉用户标注的数据
                shelf_goods.upc = one['upc']
            else:
                shelf_goods.upc = ''
            shelf_goods.save()

    return compare_ret


class ShelfScore(APIView):
    def get(self, request):
        logger.info(request.META['HTTP_REFERER'])
        picurl = request.query_params['picurl']
        try:
            picid = int(request.query_params['picid'])
            shopid = int(request.query_params['shopid'])
            shelfid = request.query_params['shelfid']
            displayid = int(request.query_params['displayid'])
            tlevel = int(request.query_params['tlevel'])
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
            source=os.path.join(image_relative_dir,source_image_name)
        )

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
            x1:x1,
            y1:y1,
            x2:x2,
            y2:y2,
            x3:x3,
            y3:y3,
            x4:x4,
            y4:y4})
        shelf_image.rectsource = os.path.join(image_relative_dir, rectify_image_name)
        shelf_image.save()

        compare_ret = detect_compare(shelf_image, rectify_image_path)

        return Response(compare_ret, status=status.HTTP_200_OK)


class GetShelfImage(APIView):
    def get(self, request):
        logger.info('GetShelfImage test')
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
        return Response(ret, status=status.HTTP_200_OK)


class GetShelfImageDetail(APIView):
    def get(self, request):
        logger.info('GetShelfImageDetail test')
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

        image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.rectsource)
        image = PILImage.open(image_path)
        (im_width, im_height) = image.size
        ret = {
            "recturl":os.path.join(settings.MEDIA_URL,shelf_image.rectsource),
            "rectwidth": im_width,
            "rectheight": im_height,
            "score":shelf_image.score,
            "equal_cnt":shelf_image.equal_cnt,
            "different_cnt":shelf_image.different_cnt,
            "unknown_cnt":shelf_image.unknown_cnt,
            "detail":detail
        }
        return Response(ret, status=status.HTTP_200_OK)


class DetectShelfImage(APIView):
    def get(self, request):
        try:
            picid = int(request.query_params['picid'])
            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('Rectify and detect error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        rectify_image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.rectsource)
        compare_ret = detect_compare(shelf_image, rectify_image_path, need_detect = False)

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

            shelf_image = ShelfImage.objects.filter(picid=picid).order_by('-pk')[0]
        except Exception as e:
            logger.error('Rectify and detect error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        # 需要计算层数
        boxes = []
        shelf_goods_list = shelf_image.shelf_image_goods.all()
        for shelf_goods in shelf_goods_list:
            # 新增的添加在第一条
            boxes.append({
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'level': -1,
            })
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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        result = serializer.instance.result
        if result == 1:
            if old_result == 0 and old_upc != '':
                sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
                if not tf.gfile.Exists(sample_dir):
                    tf.gfile.MakeDirs(sample_dir)
                old_sample_path = os.path.join(sample_dir, old_upc, '{}.jpg'.format(serializer.instance.pk))
                if os.path.isfile(old_sample_path):
                    # 删除原来的样本
                    os.remove(old_sample_path)
                serializer.instance.upc = ''
                serializer.instance.save()

        elif result == 0:
            # 计算upc
            upc = tz_good_compare.get_upc(
                serializer.instance.shelf_image.displayid,
                serializer.instance.shelf_image.shelfid,
                serializer.instance.shelf_image.pk,
                serializer.instance.pk)

            # 添加新样本
            sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
            if serializer.instance.shelf_image.rectsource != '':
                image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.rectsource)
            else:
                image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.source)
            image = PILImage.open(image_path)
            sample_image = image.crop((serializer.instance.xmin, serializer.instance.ymin, serializer.instance.xmax, serializer.instance.ymax))
            sample_image_path = os.path.join(sample_dir, upc, '{}.jpg'.format(serializer.instance.pk))
            sample_image.save(sample_image_path, 'JPEG')
            serializer.instance.upc = upc
            serializer.instance.save()

        # compare_ret = tz_good_compare.level_compare(
        #     serializer.instance.shelf_image.displayid,
        #     serializer.instance.shelf_image.shelfid,
        #     serializer.instance.shelf_image.pk,
        #     serializer.instance.pk)

        if serializer.instance.shelf_image.rectsource != '':
            image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.rectsource)
        else:
            image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.source)
        # TODO 需要优化成单层更新，提升效率
        compare_ret = detect_compare(serializer.instance.shelf_image, image_path, need_detect=False)
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
