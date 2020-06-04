import datetime
import json
import logging
import os
import shutil
import subprocess
import time
import urllib.request
from PIL import Image as PILImage
import datetime,pymysql

import numpy as np
from django.conf import settings
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
import goods.util
from goods.shelfgoods.service import tz_good_compare
from dl.util import caculate_level
import cv2
import math
from dl import shelfdetection
from goods.util import shelf_visualize
from .serializers import *
import tensorflow as tf
from goods.shelfgoods.imgsearch.aliyun.search import ImgSearch
from goods.shelfgoods.imgsearch.baidu_ai.search import ImgSearch_02


logger = logging.getLogger("detect")

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

def detect_recognize(shelf_image, source_image_path):
    # 检测框
    ret = []
    detector = shelfdetection.ShelfDetectorFactory.get_static_detector('shelf')
    step1_min_score_thresh = .5
    detect_ret = detector.detect(source_image_path, step1_min_score_thresh=step1_min_score_thresh)
    if len(detect_ret) > 0:
        caculate_level(detect_ret, shelf_image.tlevel)

    cvimg = cv2.imread(source_image_path)
    for one_box in detect_ret:
        # 识别商品
        upc, process_code = tz_good_compare.search_upc_from_api(
            one_box['xmin'],
            one_box['ymin'],
            one_box['xmax'],
            one_box['ymax'],
            cvimg
        )
        if upc is None:
            upc = ''
            result = 1
        else:
            result = 0
        shelf_goods = ShelfGoods2.objects.create(
            shelf_image_id=shelf_image.pk,
            xmin=one_box['xmin'],
            ymin=one_box['ymin'],
            xmax=one_box['xmax'],
            ymax=one_box['ymax'],
            level=one_box['level'],
            upc=upc,
            process_code=process_code,
        )
        ret.append({
            'id': shelf_goods.pk,
            'xmin': shelf_goods.xmin,
            'ymin': shelf_goods.ymin,
            'xmax': shelf_goods.xmax,
            'ymax': shelf_goods.ymax,
            'level': shelf_goods.level,
            'upc': shelf_goods.upc,
            'result': result,
        })
    if len(ret) > 0:
        #生成识别图
        result_image_name = shelf_visualize(ret, source_image_path)
        image_relative_dir = os.path.split(shelf_image.source)[0]
        shelf_image.resultsource = os.path.join(image_relative_dir, result_image_name)

        shelf_image.save()
    return ret

class CreateShelfImage(APIView):

    def get(self,request):


        logger.info('begin api/createshelfimage2')

        picurl = request.query_params['picurl']
        try:
            shopid = int(request.query_params['shopid'])
            shelfid = request.query_params['shelfid']
            tlevel = int(request.query_params['tlevel'])
        except Exception as e:
            logger.error('Shelf score error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl', charset="utf8",
                               port=3306, use_unicode=True)
        cursor = conn.cursor()
        search_sql = "select * from baidu_ai_goods_search where picture_url= '{}'".format(str(picurl))
        cursor.execute(search_sql)
        pic_data = cursor.fetchone()
        now = datetime.datetime.now()
        if pic_data is None:
            insert_sql = "insert into baidu_ai_goods_search(picture_url) value('{}')".format(str(picurl))
            cursor.execute(insert_sql)
            conn.commit()
        else:
            if not pic_data[1] is None:
                return Response(goods.util.wrap_ret(pic_data[1]), status=status.HTTP_200_OK)
            else:
                create_time = pic_data[-2]
                diff = now - create_time
                if diff.seconds < 300:
                    return Response(goods.util.wrap_ret("正在识别中"), status=status.HTTP_200_OK)


        logger.info('begin detect:{},{}'.format(shopid, shelfid))

        # 获取图片

        image_relative_dir = os.path.join(settings.DETECT_DIR_NAME, 'shelf', now.strftime('%Y%m'),now.strftime('%d%H'))
        image_dir = os.path.join(settings.MEDIA_ROOT, image_relative_dir)
        if not tf.gfile.Exists(image_dir):
            tf.gfile.MakeDirs(image_dir)
        source_image_name = '{}_{}_{}.jpg'.format(shopid,shelfid,now.strftime('%M%S'))
        source_image_path = os.path.join(image_dir, source_image_name)
        urllib.request.urlretrieve(picurl, source_image_path)

        shelf_image = ShelfImage2.objects.create(
            shopid = shopid,
            shelfid = shelfid,
            tlevel = tlevel,
            picurl = picurl,
            source=os.path.join(image_relative_dir, source_image_name),
        )

        ret = detect_recognize(shelf_image, source_image_path)

        update_sql = "update baidu_ai_goods_search set value={} where picture_url='{}'".format(str(ret),picurl)
        cursor.execute(update_sql)
        conn.commit()
        cursor.close()
        conn.close()

        logger.info('end detect:{},{}'.format(shopid, shelfid))
        return Response(goods.util.wrap_ret(ret), status=status.HTTP_200_OK)


class RectifyShelfImage(APIView):
    def get(self, request):

        picurl = request.query_params['picurl']
        x1 = int(request.query_params['x1'])
        y1 = int(request.query_params['y1'])
        x2 = int(request.query_params['x2'])
        y2 = int(request.query_params['y2'])
        if x1>x2:
            xt = x1
            yt = y1
            x1 = x2
            y1 = y2
            x2 = xt
            y2 = yt

        x3 = int(request.query_params['x3'])
        y3 = int(request.query_params['y3'])
        x4 = int(request.query_params['x4'])
        y4 = int(request.query_params['y4'])
        if x3>x4:
            xt = x3
            yt = y3
            x3 = x4
            y3 = y4
            x4 = xt
            y4 = yt

        # width = int(request.query_params['width'])
        # height = int(width * (math.sqrt((x1-x3)*(x1-x3)+(y1-y3)*(y1-y3))) / math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)))
        # TODO test for big pic
        height = abs(y1-y3) # 800
        width = int(height * math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) / math.sqrt((x1-x3)*(x1-x3)+(y1-y3)*(y1-y3)))


        now = datetime.datetime.now()
        source_image_name = '{}.jpg'.format(now.strftime('%Y%m%d_%H%M%S'))
        media_dir = settings.MEDIA_ROOT
        # 通过 picurl 获取图片
        image_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf', 'rectify')
        if not tf.gfile.Exists(image_dir):
            tf.gfile.MakeDirs(image_dir)
        source_image_path = os.path.join(image_dir, source_image_name)
        urllib.request.urlretrieve(picurl, source_image_path)

        dest_image_name = 'rectify_{}.jpg'.format(now.strftime('%Y%m%d_%H%M%S'))
        dest_image_path = os.path.join(image_dir, dest_image_name)
        img = cv2.imread(source_image_path)
        rows, cols = img.shape[:2]
        # 原图中书本的四个角点
        pts1 = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        # 变换后分别在左上、右上、左下、右下四个点
        pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        # 生成透视变换矩阵
        M = cv2.getPerspectiveTransform(pts1, pts2)
        # 进行透视变换
        dst = cv2.warpPerspective(img, M, (width, height))
        cv2.imwrite(dest_image_path,dst)
        ret = {'returl':os.path.join(settings.MEDIA_URL, settings.DETECT_DIR_NAME, 'shelf', 'rectify',dest_image_name)}

        return Response(goods.util.wrap_ret(ret), status=status.HTTP_200_OK)

class ShelfImageViewSet(DefaultMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = ShelfImage2.objects.order_by('-id')
    serializer_class = ShelfImage2Serializer


class ShelfGoodsViewSet(DefaultMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = ShelfGoods2.objects.order_by('-id')
    serializer_class = ShelfGoods2Serializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        old_upc = instance.upc

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        logger.info(serializer.instance)
        upc = serializer.instance.upc
        if upc != '':
            sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
            upc_sample_dir = os.path.join(sample_dir, upc)
            if not tf.gfile.Exists(upc_sample_dir):
                tf.gfile.MakeDirs(upc_sample_dir)
            old_sample_path = os.path.join(sample_dir, old_upc, '2_{}.jpg'.format(serializer.instance.pk))

            if os.path.isfile(old_sample_path):
                # 删除原来的样本
                os.remove(old_sample_path)
            img_search = ImgSearch()
            img_search.delete_img(old_upc, '2_{}'.format(serializer.instance.pk))

            if serializer.instance.baidu_code != '':
                imgsearch_02 = ImgSearch_02()
                imgsearch_02.delete_img(serializer.instance.baidu_code)

            # 添加新样本
            image_path = os.path.join(settings.MEDIA_ROOT, serializer.instance.shelf_image.source)
            image = PILImage.open(image_path)
            sample_image = image.crop((serializer.instance.xmin, serializer.instance.ymin, serializer.instance.xmax, serializer.instance.ymax))
            sample_image_path = os.path.join(upc_sample_dir, '2_{}.jpg'.format(serializer.instance.pk))
            sample_image.save(sample_image_path, 'JPEG')
            img_search = ImgSearch()
            img_search.add_img(upc, '2_{}'.format(serializer.instance.pk), sample_image_path)

            imgsearch_02 = ImgSearch_02()
            baidu_code = imgsearch_02.add_img(upc, '2_{}'.format(serializer.instance.pk), sample_image_path)
            if baidu_code is not None:
                serializer.instance.baidu_code = baidu_code
                serializer.instance.save()

        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        sample_dir = os.path.join(settings.MEDIA_ROOT, settings.DETECT_DIR_NAME, 'shelf_sample')
        # 删除原来的样本
        old_sample_path = os.path.join(sample_dir, instance.upc, '2_{}.jpg'.format(instance.pk))
        if os.path.isfile(old_sample_path):
            os.remove(old_sample_path)
        img_search = ImgSearch()
        img_search.delete_img(instance.upc, '2_{}'.format(instance.pk))

        if instance.baidu_code != '':
            imgsearch_02 = ImgSearch_02()
            imgsearch_02.delete_img(instance.baidu_code)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

if __name__ == '__main__':
    a = ShelfImage()
    a.get(1)
