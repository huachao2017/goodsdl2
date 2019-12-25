import json

from django.db import connections

from goods.shelfdisplay.db_data import Category3
from goods.shelfdisplay.replacedisplay.display_taizhang import TaizhangDisplay, Shelf, Level, DisplayGoods


def init_display_data(uc_shopid, tz_id, old_display_id, base_data):
    """
    初始化陈列相关的台账、货架、指定分类数据，最终生成初始化好的taizhang_display对象
    :param uc_shopid: ucentor系统shopid
    :param tz_id:
    :param old_display_id:
    :param base_data:
    :return: taizhang_display对象
    """
    taizhang_display = TaizhangDisplay(tz_id)
    cursor = connections['ucenter'].cursor()

    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账信息
    try:
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count from sf_taizhang t where t.id = {}".format(tz_id))
        (taizhang_id, shelf_id, count, third_cate_ids) = cursor.fetchone()
    except:
        print('获取台账失败：{},{}！'.format(uc_shopid, tz_id))
        cursor.close()
        raise ValueError('taizhang_display error:{},{}'.format(uc_shopid, tz_id))

    # 获取陈列信息
    cursor.execute("select display_goods_info, display_shelf_info from sf_taizhang_display where id = {} and taizhang_id = {}".format(old_display_id, tz_id))
    (display_goods_info, display_shelf_info) = cursor.fetchone()
    cursor.execute(
        "select t.shelf_no,s.length,s.height,s.depth from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(
            shelf_id))
    (shelf_no, length, height, depth) = cursor.fetchone()
    display_shelf_info = json.loads(display_shelf_info)
    display_goods_info = json.loads(display_goods_info)
    cursor.close()


    # TODO 需要支持多个货架
    shelfs = display_shelf_info['shelf']
    shelf_dict = {}
    goods_array_dict = {}
    for shelf in shelfs:
        shelf_dict[shelf['shelfId']] = shelf['layer']
    for goods_info in display_goods_info:
        goods_array_dict[goods_info['shelfId']] = goods_info['layerArray']

    category3_list = []
    for shelfId in shelf_dict.keys():
        shelf_array = shelf_dict[shelfId]
        goods_array = goods_array_dict[shelfId]
        shelf = Shelf(shelf_id, height, length, depth)
        for i in range(len(shelf_array)):
            level = shelf_array[i]
            goods_level_array = goods_array[i]
            # floor_type 1：普通陈列 2：挂层
            level = Level(shelf, i, round(float(level['height'])), round(float(level['depth'])))
            shelf.add_level(level)
            last_display_goods = None
            for goods_info in goods_level_array:
                goods_data = find_goods(goods_info['mch_goods_code'], base_data.goods_data_list)
                if last_display_goods is not None and goods_data.equal(last_display_goods.goods_data):
                    # TODO 需要把扩面和叠放反算出来
                    pass
                else:
                    last_display_goods = level.add_display_goods(goods_data)
                    if goods_data.category3 not in category3_list:
                        category3_list.append(goods_data.category3)
                    level.add_display_goods(last_display_goods)

        # FIXME 目前只支持一个货架
        choose_goods_list = filter_goods_data(category3_list, base_data.goods_data_list)
        taizhang_display.init_data(shelf, category3_list, choose_goods_list)

    return taizhang_display

def find_goods(mch_goods_code, goods_data_list):
    for goods_data in goods_data_list:
        if goods_data.mch_code == mch_goods_code:
            return goods_data
    return None

def filter_goods_data(category3_list, goods_data_list):
    ret = []
    for goods_data in goods_data_list:
        if goods_data.category3 in category3_list:
            ret.append(goods_data)

    return ret