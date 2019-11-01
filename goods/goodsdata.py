"""
这是选品、陈列、订货所需要的数据接口程序
接口包括：
1、get_shop_shelfs：陈列设计前获取货架信息
2、get_raw_goods_info：陈列设计前获取商品信息
3、get_shop_shelf_goods：订货前获取陈列信息
"""
import json
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings_public")
django.setup()
from django.db import connections


def get_raw_shop_shelfs(uc_shopid, tz_id = None):
    """
    获取商店的所有货架及货架的相关信息，该方法在陈列时用
    :param uc_shopid: 台账系统的商店id
    :param tz_id: 台账系统的台账id
    :return:返回一个DataRawShelf对象列表
    """

    ret = []
    cursor = connections['ucenter'].cursor()
    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账
    if tz_id is None:
        cursor.execute("select t.id, t.shelf_id, t.shelf_count from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {}".format(uc_shopid))
    else:
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.id = {}".format(
                uc_shopid, tz_id))
    taizhangs = cursor.fetchall()
    for taizhang in taizhangs:
        taizhang_id = taizhang[0]
        shelf_id = taizhang[1]
        count = taizhang[2]
        # 获取商店台账可放的品类
        try:
            cursor.execute("select associated_catids from sf_taizhang_display where taizhang_id = {} and status in (0,1) and approval_status = 0".format(taizhang_id))
            (associated_catids,) = cursor.fetchone()
        except:
            print('获取台账陈列失败：{}！'.format(taizhang_id))
            associated_catids = None
        cursor.execute("select t.shelf_no,s.length,s.height,s.depth from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(shelf_id))
        (shelf_no, length, height, depth) = cursor.fetchone()
        data_raw_shelf = DataRawShelf(taizhang_id, shelf_id, shelf_no,count, length,height,depth,associated_catids)
        ret.append(data_raw_shelf)

    cursor.close()

    return ret

def get_raw_goods_info(uc_shopid, mch_codes):
    """
    根据upc列表获取每个upc的类别、长宽高，该方法在陈列时用
    :param uc_shopid: 台账系统的商店id
    :param mch_id: 台账系统的商家id
    :param mch_codes:
    :return:返回一个DataRawGoods对象的map,key为mch_code
    """
    ret = {}
    cursor = connections['ucenter'].cursor()
    cursor_dmstore = connections['dmstore'].cursor()
    cursor_erp = connections['erp'].cursor()

    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取erp系统的erp_shopid
    try:
        cursor_dmstore.execute("select erp_shop_id from erp_shop_related where erp_shop_type = 0 and shop_id = {}".format(shopid))
        (erp_shop_id,) = cursor_dmstore.fetchone()

        # 获取erp系统的供应商id TODO 需要处理多个供应商
        cursor_erp.execute("select authorized_shop_id from ms_relation WHERE is_authorized_shop_id={} and status=1".format(erp_shop_id))
        (authorized_shop_id,) = cursor_erp.fetchone()
    except:
        print('找不到供应商:{}！'.format(shopid))
        authorized_shop_id = None

    for mch_code in mch_codes:
        # 获取商品属性
        cursor.execute("select id, goods_name,upc, tz_display_img, spec, volume, width,height,depth,is_superimpose,is_suspension from uc_merchant_goods where mch_id = {} and mch_goods_code = {}".format(mch_id, mch_code))
        (goods_id, goods_name, upc, tz_display_img, spec, volume, width, height, depth,is_superimpose,is_suspension) = cursor.fetchone()

        # 获取分类码
        try:
            cursor_dmstore.execute("select corp_classify_code from goods where upc = '{}' and corp_goods_id={}".format(upc, mch_code))
            (corp_classify_code,) = cursor_dmstore.fetchone()
        except:
            print('dmstore找不到商品:{}-{}！'.format(upc, mch_code))
            corp_classify_code = None

        if authorized_shop_id is not None:
            try:
                # 获取起订量
                # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                cursor_erp.execute("select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}'".format(authorized_shop_id, upc))
                (sku_id,) = cursor_erp.fetchone()
                cursor_erp.execute("select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(sku_id))
                (start_sum,multiple) = cursor_erp.fetchone()
            except:
                print('Erp找不到商品:{}！'.format(upc))
                start_sum = 0
                multiple = 0
        else:
            start_sum = 0
            multiple = 0

        ret[mch_code] = DataRawGoods(mch_code, goods_name, upc, tz_display_img,corp_classify_code, spec, volume, width, height, depth,is_superimpose,is_suspension, start_sum,multiple)

    cursor.close()
    cursor_dmstore.close()
    cursor_erp.close()
    return ret

def get_shop_shelf_goods(shopid):
    """
    获取商店的所有货架及货架上的商品信息，该方法在订货时用
    :param shopid: fx系统的商店id
    :return:返回DataShelf列表
    """

    ret = []
    cursor = connections['ucenter'].cursor()
    # 获取台账系统的uc_shopid
    cursor.execute('select id, mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    (uc_shopid, mch_id) = cursor.fetchone()

    # 获取台账 TODO 只能获取店相关的台账，不能获取商家相关的台账
    cursor.execute("select t.id, t.shelf_id, td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status in (1,2) and td.approval_status=1 and st.shop_id = {}".format(uc_shopid))
    taizhangs = cursor.fetchall()
    for taizhang in taizhangs:
        taizhang_id = taizhang[0]
        shelf_id = taizhang[1]
        display_shelf_info = taizhang[2]
        display_goods_info = taizhang[3]
        cursor.execute("select t.shelf_no,s.length,s.height,s.depth from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(shelf_id))
        (shelf_no, length, height, depth) = cursor.fetchone()
        display_shelf_info = json.loads(display_shelf_info)
        display_goods_info = json.loads(display_goods_info)
        shelfs = display_shelf_info['shelf']
        shelf_dict = {}
        goods_array_dict = {}
        for shelf in shelfs:
            shelf_dict[shelf['shelfId']] = shelf['layer']
        for goods_info in display_goods_info:
            goods_array_dict[goods_info['shelfId']] = goods_info['layerArray']

        for shelfId in shelf_dict.keys():
            level_array = shelf_dict[shelfId]
            goods_array = goods_array_dict[shelfId]
            data_shelf = DataShelf(taizhang_id, shelf_id, shelf_no, length, height, depth)
            ret.append(data_shelf)
            for i in range(len(level_array)):
                level = level_array[i]
                goods_level_array = goods_array[i]
                #floor_type 1：普通陈列 2：挂层
                data_level = DataLevel(level['floor_type'],round(float(level['height'])),round(float(level['depth'])))
                data_shelf.add_data_level(data_level)
                for goods in goods_level_array:
                    cursor.execute(
                        "select id, upc, spec, volume, width,height,depth from uc_merchant_goods where mch_id = {} and mch_goods_code = {}".format(
                            mch_id, goods['mch_goods_code']))
                    (goods_id, upc, spec, volume, width, height, depth) = cursor.fetchone()
                    data_goods = DataGoods(goods['mch_goods_code'], upc, width, height, depth)
                    data_level.add_data_goods(data_goods)

    cursor.close()

    return ret


class DataRawShelf():
    def __init__(self, taizhang_id, shelf_id, type, count, length, height, depth, associated_catids):
        self.taizhang_id = taizhang_id
        self.shelf_id = shelf_id
        self.type = type
        self.count = count
        self.length = length
        self.height = height
        self.depth = depth
        if associated_catids is None or associated_catids == '':
            self.associated_catids = []
        else:
            self.associated_catids = associated_catids.split(',')

    def __str__(self):
        ret = '{},{},{},{},{},{},{},{}'.format(self.taizhang_id, self.shelf_id, self.type, self.count, self.length, self.height, self.depth, self.associated_catids)
        return ret

class DataShelf():
    def __init__(self, taizhang_id, shelf_id, type, length, height, depth):
        self.taizhang_id = taizhang_id
        self.shelf_id = shelf_id
        self.type = type
        self.length = length
        self.height = height
        self.depth = depth
        self.data_levels = []

    def add_data_level(self, data_level):
        self.data_levels.append(data_level)

    def __str__(self):
        ret = '{},{},{},{},{},{}'.format(self.taizhang_id, self.shelf_id, self.type, self.length, self.height, self.depth)
        if len(self.data_levels)>0:
            ret += ':[\n'
            for data_level in self.data_levels:
                ret += str(data_level)
                ret += '\n'
            ret += ']'
        return ret

class DataLevel():
    def __init__(self, type, height, depth):
        self.type = type
        self.height = height
        self.depth = depth
        self.data_goods_array = []

    def add_data_goods(self, data_goods):
        self.data_goods_array.append(data_goods)

    def __str__(self):
        ret = '\t{},{},{}'.format(self.type, self.height, self.depth)
        if len(self.data_goods_array)>0:
            ret += ':[\n'
            for data_goods in self.data_goods_array:
                ret += str(data_goods)
                ret += '\n'
            ret += '\t]'
        return ret

class DataGoods():
    def __init__(self, mch_code, upc, width, height, depth):
        self.mch_code = mch_code
        self.upc = upc
        self.width = width
        self.height = height
        self.depth = depth

    def __str__(self):
        return '\t\t{},{},{},{},{}'.format(self.mch_code,self.upc,self.width,self.height,self.depth)

class DataRawGoods():
    def __init__(self, mch_code, goods_name, upc, tz_display_img,corp_classify_code, spec, volume, width, height, depth, is_superimpose,is_suspension, start_sum, multiple):
        self.mch_code = mch_code
        self.goods_name = goods_name
        self.upc = upc
        self.tz_display_img = tz_display_img
        self.corp_classify_code = corp_classify_code
        self.display_code = corp_classify_code # FIXME 需要修订为真实陈列分类
        self.spec = spec
        self.volume = volume
        self.width = width
        self.height = height
        self.depth = depth
        if is_superimpose is None or is_superimpose == 2:
            self.is_superimpose = False # 1可叠放，2不可叠放
        else:
            self.is_superimpose = True
        if is_suspension is None or is_suspension == 2:
            self.is_suspension = False # 1可挂放，2不可挂放
        else:
            self.is_suspension = True
        self.start_sum = start_sum
        self.multiple = multiple

    def __str__(self):
        return '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(self.mch_code,self.goods_name,self.upc,self.tz_display_img,self.corp_classify_code,self.display_code,self.spec,self.volume,self.width,self.height,self.depth,self.is_superimpose,self.is_suspension,self.start_sum,self.multiple)

if __name__ == "__main__":
    ret = get_raw_shop_shelfs(806)
    for data_raw_shelf in ret:
        print(str(data_raw_shelf))
        print('\n')

    ret = get_raw_goods_info(806,[2036329,2036330])
    print("\n".join('{}:{}'.format(str(i),str(ret[i])) for i in ret.keys()))

    # ret = get_shop_shelf_goods(1284)
    # for data_shelf in ret:
    #     print(str(data_shelf))
    #     print('\n')
