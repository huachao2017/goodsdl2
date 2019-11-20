import os
import cv2
import numpy as np
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.conf import settings

from goods.shelfdisplay import db_data
from goods.shelfdisplay import display_data
from goods.shelfdisplay import goods_arrange
from goods.shelfdisplay import shelf_arrange


def generate_displays(uc_shopid, tz_id):
    """
    :param uc_shopid:
    :param tz_id:
    :return: taizhang对象
    """

    # 初始化基础数据
    base_data = db_data.init_data(uc_shopid)

    # 初始化台账数据
    taizhang = display_data.init_data(uc_shopid, tz_id, base_data)

    # 第三步
    # FIXME 这版仅支持一个货架的台账
    candidate_category_list = shelf_arrange.shelf_arrange(taizhang.shelfs[0])
    taizhang.shelfs[0].candidate_category_list = candidate_category_list

    # 第四步
    is_ok = goods_arrange.goods_arrange(taizhang.shelfs[0])

    if is_ok:
        # 打印陈列图
        print(taizhang.to_json())
        image_relative_dir = os.path.join(settings.DETECT_DIR_NAME, 'taizhang',str(taizhang.tz_id))
        image_dir = os.path.join(settings.MEDIA_ROOT, image_relative_dir)
        from pathlib import Path
        if not Path(image_dir).exists():
            os.makedirs(image_dir)

        print(image_dir)
        print_taizhang(taizhang, image_dir)
    return taizhang


def print_taizhang(taizhang, image_dir):
    import urllib.request
    from django.conf import settings
    index = 0

    # import PIL.ImageFont as ImageFont
    #     fontText = ImageFont.truetype("font/simsun.ttc", 12, encoding="utf-8")

    picurl_to_goods_image = {}
    for shelf in taizhang.shelfs:
        index += 1
        image_path = os.path.join(image_dir, '{}.jpg'.format(index))
        image = np.ones((shelf.height, shelf.width, 3), dtype=np.int16)
        image = image * 255

        for level in shelf.best_candidate_shelf.levels:
            level_start_height = level.start_height
            for display_goods in level.display_goods_list:
                picurl = '{}{}'.format(settings.UC_PIC_HOST, display_goods.goods_data.tz_display_img)
                if picurl in picurl_to_goods_image:
                    goods_image = picurl_to_goods_image[picurl]
                else:
                    try:
                        goods_image_name = '{}.jpg'.format(display_goods.goods_data.mch_code)
                        goods_image_path = os.path.join(image_dir, goods_image_name)
                        urllib.request.urlretrieve(picurl, goods_image_path)
                        goods_image = cv2.imread(goods_image_path)
                        goods_image = cv2.resize(goods_image,
                                                 (display_goods.goods_data.width, display_goods.goods_data.height))
                    except Exception as e:
                        print('get goods pic error:{}'.format(e))
                        goods_image = None
                    picurl_to_goods_image[picurl] = goods_image

                for goods_display_info in display_goods.get_display_info(level):
                    point1 = (goods_display_info.left, shelf.height - (
                    goods_display_info.top + level_start_height))
                    point2 = (goods_display_info.left + display_goods.goods_data.width,
                              shelf.height - (goods_display_info.top + level_start_height) + display_goods.goods_data.height)
                    cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                    # if goods_image is None:
                    #     cv2.rectangle(image,point1,point2,(0,0,255),2)
                    # else:
                    #     h = goods_image.shape[0]
                    #     w = goods_image.shape[1]
                    #     image[point1[1]:point1[1]+h, point1[0]:point1[0]+w,:] = goods_image
                    txt_point = (goods_display_info.left, shelf.height - (
                    goods_display_info.top + level_start_height + int(display_goods.goods_data.height / 2)))
                    cv2.putText(image, '{}'.format(display_goods.goods_data.mch_code), txt_point,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.imwrite(image_path, image)


if __name__ == "__main__":
    # taizhang = generate_displays(806, 1187)
    taizhang = generate_displays(806, 1199)
