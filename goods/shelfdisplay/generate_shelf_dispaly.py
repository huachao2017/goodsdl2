import os
import cv2
import numpy as np
import json
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections

from goods.shelfdisplay import db_data
from goods.shelfdisplay import display_data
from goods.shelfdisplay import shelf_arrange
from goods.shelfdisplay import goods_arrange

def generate_displays(uc_shopid, tz_id):
    """
    :param uc_shopid:
    :param tz_id:
    :return: taizhang对象
    """

    # 初始化基础数据
    base_data = db_data.init_data()

    # 初始化台账数据
    taizhang = display_data.init_data(tz_id, base_data.goods_data_list)

    # 第三步
    # FIXME 这版仅支持一个货架的台账
    candidate_category_list = shelf_arrange.shelf_arrange(taizhang.shelfs[0],
                                                          base_data.category3_intimate_weight,
                                                          base_data.category3_level_value)
    # 第四步
    goods_arrange.goods_arrange(taizhang.shelfs[0],
                                candidate_category_list,
                                taizhang.candidate_goods_data_list,
                                base_data.category_area_ratio,
                                base_data.goods_arrange_weight)


    return taizhang


if __name__ == "__main__":
    taizhang = generate_displays(806,1142)
