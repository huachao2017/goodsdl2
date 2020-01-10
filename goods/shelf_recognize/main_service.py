import argparse
import sys
import os
import logging
import urllib.request
import main.import_django_settings

from goods.models import ShelfImage,ShelfGoods
from dl import shelfdetection
from dl.util import caculate_level
from goods.shelfgoods.service import tz_good_compare
from goods.util import shelf_visualize
from django.conf import settings

logger = logging.getLogger("detect")

def parse_arguments(argv):
    # type,jpg_path,xml_path,classnames,online_batch_id
    parser = argparse.ArgumentParser()

    parser.add_argument('--imageid', type=int, help='imageid', default=0)
    return parser.parse_args(argv)

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
    print('notify_result request_param:{}'.format(request_param))
    if shelf_image.test_server:
        res = urllib.request.urlopen('http://alphataizhang.aicvs.cn/m/shelf/updateScore?' + request_param)
    else:
        res = urllib.request.urlopen('http://taizhang.aicvs.cn/m/shelf/updateScore?' + request_param)

    logger.info('notify_result response:{}'.format(res.read()))

if __name__ == "__main__":
    import json
    args = parse_arguments(sys.argv[1:])
    shelf_image = ShelfImage.objects.filter(pk=args.imageid)

    source_image_path = os.path.join(settings.MEDIA_ROOT, shelf_image.source.path)
    compare_ret = detect_compare(shelf_image, source_image_path, need_notify=True)
