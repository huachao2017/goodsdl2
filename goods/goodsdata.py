import json
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings_public")
django.setup()
from django.db import connections


def get_shop_shelfs(shopid, need_goods=False):
    """
    获取商店的所有货架，及每个货架的每个层的参数信息，如果need_goods则需连带商品数据信息，否则不带商品数据信息
    :param shopid: fx系统的商店id
    :param need_goods: 是否需要返回商品相关信息
    :return:返回一个Shop对象
    """

    data_shop = DataShop(shopid)
    cursor = connections['ucenter'].cursor()
    # 获取台账系统的uc_shopid
    cursor.execute('select id, mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    (uc_shopid, mch_id) = cursor.fetchone()

    # 获取台账
    # TODO 需要获取商店台账可放的品类
    cursor.execute('select t.id, t.shelf_id from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {}'.format(uc_shopid))
    taizhangs = cursor.fetchall()
    for taizhang in taizhangs:
        taizhang_id = taizhang[0]
        shelf_id = taizhang[1]
        cursor.execute('select t.shelf_no,s.length,s.height,s.depth from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}'.format(shelf_id))
        (shelf_no, length, height, depth) = cursor.fetchone()
        data_shelf = DataShelf(shelf_no,length,height,depth)
        data_shop.add_data_shelf(data_shelf)

    cursor.close()

    return data_shop

def get_raw_goods_info(upcs):
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
    def __init__(self, type, length, height, depth):
        self.type = type
        self.length = length
        self.height = height
        self.depth = depth
        self.data_levels = []


class DataGoods():
    def __init__(self,upc, code, width, height, depth):
        self.upc = upc
        self.code = code
        self.width = width
        self.height = height
        self.depth = depth
