import json
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections


def get_shop_shelfs(shopid):
    """
    获取商店的所有货架，及每个货架的每个层的参数信息
    :param shopid: fx系统的商店id
    :return:返回一个Shop对象
    """
    return DataShop(0)

def get_goods_info(upcs):
    """
    根据upc列表获取每个upc的类别、长宽高
    :param upcs:
    :return:返回一个map，类似{upc1:goods1,upc2:goods2}，goods1和goods2都是一个goods对象
    """
    ret = {}
    for upc in upcs:
        ret[upc] = DataGoods(upc, '',0,0,0)
    return ret

class DataShop():
    def __init__(self, shopid):
        self.shopid = shopid
        self.data_shelfs = []

    def add_data_shelf(self, data_shelf):
        self.data_shelfs.append(data_shelf)

class DataShelf():
    def __init__(self, type, width, height, deepth):
        self.type = type
        self.width = width
        self.deepth = height
        self.deep = deepth
        self.data_levels = []

    def add_data_level(self,data_level):
        self.data_levels.append(data_level)

class DataLevel():
    def __init__(self, type, width, height, deepth):
        self.type = type
        self.width = width
        self.height = height
        self.deepth = deepth

class DataGoods():
    def __init__(self,upc, code, width, height, deepth):
        self.upc = upc
        self.code = code
        self.width = width
        self.height = height
        self.deepth = deepth
