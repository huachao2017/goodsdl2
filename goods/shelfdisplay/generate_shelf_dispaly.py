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

    success =  taizhang.display()
    if success:
        print('Success')
    else:
        print('Fail')

    return taizhang



if __name__ == "__main__":
    # taizhang = generate_displays(806, 1187)
    taizhang = generate_displays(806, 1199)
