import os
import django

from goods.shelfdisplay import db_data
from goods.shelfdisplay import display_data


def generate_displays(uc_shopid, tz_id):
    """
    :param uc_shopid:
    :param tz_id:
    :return: taizhang对象
    """

    print("begin generate_displays:{},{}".format(uc_shopid,tz_id))

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

