
import json
import django
import os
import time
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
import math
from django.db import connections
import traceback
from goods import utils

def get_shop_order_goods(shopid, erp_shop_type=0,batch_id=None):
    """
    获取商店的所有货架及货架上的商品信息，该方法在订货V3时用
    :param shopid: fx系统的商店id
    :param erp_shop_type: erp系统里面的类型
    :return:返回一个DataRawGoods对象的map,key为mch_code
    """
    ret = {}
    next_day = str(time.strftime('%Y-%m-%d', time.localtime()))
    cursor = connections['ucenter'].cursor()
    cursor_dmstore = connections['dmstore'].cursor()
    cursor_erp = connections['erp'].cursor()
    cursor_ai = connections['default'].cursor()

    # 获取台账系统的uc_shopid
    cursor.execute('select id, shop_name , mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    (uc_shopid, shop_name,mch_id) = cursor.fetchone()
    erp_shop_id = None
    erp_supply_id = None
    authorized_shop_id = None
    # 获取erp系统的erp_shopid
    try:
        cursor_dmstore.execute("select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 0".format(shopid))
        (erp_shop_id,) = cursor_dmstore.fetchone()
        cursor_dmstore.execute(
            "select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 1".format(shopid))
        (erp_supply_id,) = cursor_dmstore.fetchone()
        if erp_shop_type == 0:
            cursor_erp.execute("select authorized_shop_id from ms_relation WHERE is_authorized_shop_id={} and status=1".format(erp_shop_id))
            (authorized_shop_id,) = cursor_erp.fetchone()
        else:
            cursor_erp.execute("select authorized_shop_id from ms_relation WHERE is_authorized_shop_id={} and status=1".format(erp_supply_id))
            (authorized_shop_id,) = cursor_erp.fetchone()


    except:
        print('找不到供应商:{}！'.format(shopid))
        traceback.print_exc()
        authorized_shop_id = None

    # 获取台账 TODO 只能获取店相关的台账，不能获取商家相关的台账
    cursor.execute("select t.id, t.shelf_id, td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status in (1,2) and td.approval_status=1 and st.shop_id = {}".format(uc_shopid))
    taizhangs = cursor.fetchall()
    shelf_inss = []
    for taizhang in taizhangs:
        taizhang_id = taizhang[0]
        shelf_id = taizhang[1]
        shelf_type = ''
        shelf_type_id = None
        try:
            cursor.execute("select id,shelf_type_id from sf_shelf where id = {}".format(shelf_id))
            (id,shelf_type_id) = cursor.fetchone()
        except:
            print ("台账找不到货架 ， shelf_id="+str(shelf_id))
            traceback.print_exc()

        try:
            cursor.execute("select id,type_name from sf_shelf_type where id = {} ".format(shelf_type_id))
            (id, type_name) = cursor.fetchone()
            shelf_type = type_name
        except:
            print("台账找不到货架类型名称 ， shelf_type_id=" + str(shelf_type_id))
            traceback.print_exc()
        display_shelf_info = taizhang[2]
        display_goods_info = taizhang[3]
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
            for i in range(len(level_array)):
                level = level_array[i]
                goods_level_array = goods_array[i]
                level_depth = round(float(level['depth']))
                for goods in goods_level_array:
                    mch_code = goods['mch_goods_code']
                    if mch_code in ret:
                        for shelf_ins in ret[mch_code].shelf_inss:
                            if shelf_id == shelf_ins.shelf_id:
                                shelf_ins.face_num += 1
                    else:
                        shelf_ins = Shelf()
                        shelf_ins.taizhang_id = taizhang_id
                        shelf_ins.shelf_id = shelf_id
                        shelf_ins.shelf_type = shelf_type
                        shelf_ins.mch_code = mch_code
                        shelf_ins.goods_level_id = i
                        shelf_ins.level_depth = level_depth
                        shelf_ins.face_num = 1
                        shelf_inss.append(shelf_ins)
                        # 获取商品属性
                        try:
                            cursor.execute(
                                "select id, goods_name,upc, tz_display_img, spec, volume, width,height,depth,is_superimpose,is_suspension,delivery_type,category1_id,category2_id,category_id,storage_day,package_type from uc_merchant_goods where mch_id = {} and mch_goods_code = {}".format(
                                    mch_id, mch_code))
                            # FIXME width,height暂时翻转
                            # (goods_id, goods_name, upc, tz_display_img, spec, volume, width, height, depth,is_superimpose,is_suspension) = cursor.fetchone()
                            (goods_id, goods_name, upc, tz_display_img, spec, volume, height, width, depth, is_superimpose,
                             is_suspension,delivery_type,category1_id,category2_id,category_id,storage_day,package_type) = cursor.fetchone()
                        except:
                            print('台账找不到商品，只能把这个删除剔除:{}！'.format(mch_code))
                            continue
                        scale = None
                        # 获取最大陈列系数
                        try:
                            cursor.execute(
                                "select cat2_id,cat3_id,scale from sf_goods_categorymaxdisplayscale where mch_id = {} and cat3_id = '{}' ".format(
                                    mch_id,category_id))
                            (cat3_id, scale) = cursor.fetchone()
                            if cat3_id is None:
                                max_scale = 1
                            else:
                                max_scale = float(scale)
                        except:
                            print('台账找不到商品的最大陈列系数:{}！'.format(mch_code))
                            scale = None

                        try:
                            if scale is None:
                                cursor.execute(
                                    "select cat2_id,cat3_id,scale from sf_goods_categorymaxdisplayscale where mch_id = {} and cat2_id = '{}' ".format(
                                        mch_id, category2_id))
                                (cat2_id, scale) = cursor.fetchone()
                                if cat2_id is None:
                                    max_scale = 1
                                else:
                                    max_scale = float(scale)
                        except:
                            print('台账找不到商品的最大陈列系数:{}！'.format(mch_code))
                            scale = None
                        if scale is None :
                            max_scale = 1
                        # 获取分类码
                        try:
                            cursor_dmstore.execute(
                                "select corp_classify_code from goods where upc = '{}' and corp_goods_id={}".format(upc,
                                                                                                                    mch_code))
                            (corp_classify_code, ) = cursor_dmstore.fetchone()
                        except:
                            print('dmstore找不到商品:{}-{}！'.format(upc, mch_code))
                            corp_classify_code = None

                        try:
                            cursor_dmstore.execute(
                                "select id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (id, upc_price, purchase_price, stock) = cursor_dmstore.fetchone()
                        except:
                            stock = 0
                            purchase_price = 1
                            upc_price = 1
                            print("%s delivery_type is error , goods_name=%s,upc=%s" % (
                                str(delivery_type), str(goods_name),
                                str(upc)))
                        sales_nums = 0
                        #  获取最近一周的平均销量
                        try:
                            cursor_dmstore.execute(
                                "select id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (id,upc_price,purchase_price,stock) = cursor_dmstore.fetchone()
                            # 销量
                            sales_sql = "SELECT sum(number) as nums FROM payment_detail " \
                                        "WHERE shop_id = {} and shop_goods_id = {} and number > 0 and create_time >= '{} 00:00:00' AND create_time < '{} 00:00:00' AND payment_id IN ( " \
                                        "SELECT DISTINCT(payment.id) FROM payment WHERE payment.type != 50 AND create_time >= '{} 00:00:00' AND create_time < '{} 00:00:00' )"
                            if delivery_type == 2:  # 非日配
                                end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
                                start_date = str(
                                    (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                                        days=-7)).strftime("%Y-%m-%d"))
                                cursor_dmstore.execute(
                                    sales_sql.format(shopid, id, start_date, end_date, start_date, end_date))
                                # print ([str(shopid), str(id), str(start_date), str(end_date), str(start_date), str(end_date)])
                                (sales_nums,) = cursor_dmstore.fetchone()

                            elif  delivery_type == 1: # 日配
                                end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
                                start_date = str(
                                    (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                                        days=-7)).strftime("%Y-%m-%d"))
                                cursor_dmstore.execute(
                                    sales_sql.format(shopid, id, start_date, end_date, start_date, end_date))
                                (sales_nums,) = cursor_dmstore.fetchone()
                            else:
                                print("%s delivery_type is error , goods_name=%s,upc=%s" % (
                                str(delivery_type), str(goods_name),
                                str(upc)))
                                sales_nums = 0
                        except:
                            print('dmstore找不到计算销量商店商品:{}-{}-{}！'.format(shopid, upc,goods_name))
                            sales_nums = 0


                        if authorized_shop_id is not None:
                            try:
                                # 获取起订量
                                # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                                cursor_erp.execute(
                                    "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}'".format(
                                        authorized_shop_id, upc))
                                (sku_id,) = cursor_erp.fetchone()
                                cursor_erp.execute(
                                    "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(
                                        sku_id))
                                (start_sum, multiple) = cursor_erp.fetchone()
                            except:
                                print('Erp找不到商品:{}-{}！'.format(upc, authorized_shop_id))
                                start_sum = 0
                                multiple = 0
                        else:
                            start_sum = 0
                            multiple = 0
                        try:
                            # 获取小仓库库存
                            # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                            cursor_erp.execute(
                                "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}'".format(
                                    erp_supply_id, upc))
                            (sku_id,) = cursor_erp.fetchone()
                            cursor_erp.execute(
                                "select stock from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(
                                    sku_id))
                            (supply_stock, ) = cursor_erp.fetchone()
                        except:
                            print('ErpSupply找不到商品:{}-{}！'.format(upc, erp_supply_id))
                            supply_stock = 0
                        # 获取在途订单数
                        try:
                            # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                            cursor_erp.execute(
                                "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}'".format(
                                    authorized_shop_id, upc))
                            (sku_id,) = cursor_erp.fetchone()
                            cursor_erp.execute(
                                "select sum(item.sub_item_count) as sub_count from ls_sub_item item LEFT JOIN ls_sub sub ON  item.sub_number=sub.sub_number where sub.buyer_shop_id= {} AND sub.status=50 and sku_id = {}".format(
                                    erp_supply_id,sku_id))
                            (sub_count,) = cursor_erp.fetchone()
                            print("找到在途库存 ："+str(erp_supply_id) + "," + str(upc) + "," + str(sku_id))
                        except:
                            print('ErpSupply 获取在途订单数 找不到商品:{}-{}！'.format(upc, erp_supply_id))
                            sub_count = 0
                        # 获取昨日预测销量
                        try:
                            cursor_ai.execute(
                                "select nextday_predict_sales from goods_ai_sales_goods where shopid={} and upc='{}' and next_day='{}'".format(shopid, upc, next_day))
                            (sales,) = cursor_ai.fetchone()
                        except:
                            print('ai找不到销量预测:{}-{}-{}！'.format(shopid,upc,next_day))
                            sales = 0
                        # 获取商品的上架时间
                        try:
                            cursor_ai.execute(
                                "select up_shelf_date,is_new_goods from goods_up_shelf_datetime where shopid={} and upc='{}'".format(
                                    uc_shopid, upc))
                            (up_shelf_date,up_status) = cursor_ai.fetchone()
                            print('ai找到商品上架时间 :{}-{}！'.format(uc_shopid, upc))
                        except:
                            # print('ai找不到销量预测:{}-{}-{}！'.format(shopid,upc,next_day))
                            up_shelf_date = str(time.strftime('%Y-%m-%d', time.localtime()))

                        # TODO 获取bi 数据库 ， 品的psd金额   mch_id  dmstore_shopid  goods_code
                        try:
                            end_date = str(time.strftime('%Y%m%d', time.localtime()))
                            start_date_1 = str(
                                (datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(
                                    days=-7)).strftime("%Y%m%d"))
                            start_date_4 = str(
                                (datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(
                                    days=-28)).strftime("%Y%m%d"))
                            sql1 = ""
                            upc_psd_amount_avg_4 = 0
                            upc_psd_amount_avg_1 = 0
                        except:
                            # print('ai找不到销量预测:{}-{}-{}！'.format(shopid,upc,next_day))
                            upc_psd_amount_avg_4 = 0
                            upc_psd_amount_avg_1 = 0
                        psd_nums_4, psd_amount_4 = 0,0
                        try:
                            psd_nums_4, psd_amount_4 = utils.select_psd_data(upc, shopid, 28)
                        except:
                            print("select_psd_data is error ,upc=" + str(upc))
                            psd_nums_4 = 0
                            psd_amount_4 = 0

                        ret[mch_code] = DataRawGoods(mch_code, goods_name, upc, tz_display_img,corp_classify_code, spec, volume, width, height, depth,
                                                      start_sum,multiple,
                                                     stock = stock,
                                                     predict_sales = sales,
                                                     supply_stock=supply_stock,old_sales = sales_nums,delivery_type=delivery_type,category1_id=category1_id,
                                                     category2_id=category2_id,category_id=category_id,storage_day=storage_day,shelf_inss=shelf_inss,
                                                     shop_name=shop_name,uc_shopid=uc_shopid,package_type=package_type,dmstore_shopid=shopid,
                                                     up_shelf_date = up_shelf_date,up_status = up_status,sub_count = sub_count,upc_price=upc_price,
                                                     upc_psd_amount_avg_4=upc_psd_amount_avg_4,purchase_price = purchase_price,upc_psd_amount_avg_1=upc_psd_amount_avg_1,
                                                     psd_nums_4=psd_nums_4,psd_amount_4=psd_amount_4,max_scale=max_scale)
    cursor.close()
    cursor_dmstore.close()
    cursor_erp.close()
    cursor_ai.close()
    return ret

class DataRawGoods():
    def __init__(self, mch_code, goods_name, upc, tz_display_img, corp_classify_code, spec, volume, width, height, depth,  start_sum, multiple,
                 stock=0, predict_sales=0,supply_stock=0,old_sales=0,delivery_type=None,category1_id=None,category2_id=None,category_id=None,
                 storage_day=None,shelf_inss=None,shop_name=None,uc_shopid =None,package_type=None,dmstore_shopid = None,up_shelf_date = None,
                 up_status=None,sub_count = None,upc_price = None,upc_psd_amount_avg_4 = None,purchase_price = None,upc_psd_amount_avg_1=None,
                 psd_nums_4=None, psd_amount_4=None,max_scale=None):
        self.mch_code = mch_code
        self.goods_name = goods_name
        self.upc = upc
        self.shop_name = shop_name
        self.ucshop_id = uc_shopid
        self.dmstoreshop_id = dmstore_shopid
        self.tz_display_img = tz_display_img
        self.corp_classify_code = corp_classify_code
        self.display_code = corp_classify_code # FIXME 需要修订为真实陈列分类
        self.spec = spec
        self.volume = volume
        self.width = width
        self.height = height
        if up_shelf_date is None:
            self.up_shelf_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        else:
            self.up_shelf_date = up_shelf_date
        if up_status is None :
            self.up_status = 1
        else:
            self.up_status = up_status
        if sub_count is None :
            self.sub_count = 0
        else:
            self.sub_count = float(sub_count)
        if upc_psd_amount_avg_4 is None:
            self.upc_psd_amount_avg_4 = 0
        else:
            self.upc_psd_amount_avg_4 = upc_psd_amount_avg_4
        if upc_psd_amount_avg_1 is None:
            self.upc_psd_amount_avg_1 = 0
        else:
            self.upc_psd_amount_avg_1= upc_psd_amount_avg_1
        if purchase_price is None:
            self.purchase_price = 1
        else:
            self.purchase_price = purchase_price
        if upc_price is None or int(upc_price) == 0:
            self.upc_price = 1
        else:
            self.upc_price = upc_price
        if psd_nums_4 is None:
            self.psd_nums_4 = 0
        else:
            self.psd_nums_4 = psd_nums_4
        if psd_amount_4 is None:
            self.psd_amount_4 = 0
        else:
            self.psd_amount_4 = psd_amount_4


        if package_type is None:
            self.package_type = 0
        else:
            self.package_type = package_type
        if depth is None or depth == 0 :
            self.depth = 0.001
        else:
            self.depth = depth
        if start_sum is None :
            self.start_sum = 0
        else:
            self.start_sum = start_sum
        self.multiple = multiple
        if stock is None:
            self.stock = 0
        else:
            self.stock = float(stock)   # 门店库存
        if predict_sales is None:
            self.predict_sales = 0
        else:
            self.predict_sales = predict_sales
        if old_sales is None :
            self.old_sales = 0
        else:
            self.old_sales = float(old_sales)
        if supply_stock is None:
            self.supply_stock = 0
        else:
            self.supply_stock = float(supply_stock)  #小仓库库存
        self.delivery_type = delivery_type
        self.category1_id = category1_id  # 台账分类
        self.category2_id = category2_id
        if delivery_type is None:
            self.delivery_type = 2
        if category_id is None:
            self.category_id = 0
        else:
            self.category_id = category_id
        if storage_day is None:
            self.storage_day = 0
        else:
            self.storage_day = storage_day
        if max_scale is None:
            max_scale = 1
        else:
            self.max_scale = max_scale
        new_shelf_inss = []
        max_disnums = 0
        min_disnums = 0
        for shelf_ins in shelf_inss:
            if shelf_ins.mch_code == mch_code:
                min_disnums += shelf_ins.face_num
                max_disnums = int(shelf_ins.face_num * math.floor(shelf_ins.level_depth / self.depth))
                new_shelf_inss.append(shelf_ins)
        self.shelf_inss = new_shelf_inss
        self.max_disnums = max_disnums * max_scale
        self.min_disnums = min_disnums
        self.safe_day_nums = 7
        self.isnew_goods = False
        try:
            if self.storage_day != None and int(storage_day) > 0:
                if  int(storage_day) >=30:
                    self.safe_day_nums = 7
                else:
                    self.safe_day_nums = 2
        except:
            print("商品的保质期error,mch_code=" + str(self.mch_code)+",goods_name="+str(self.goods_name))
            self.storage_day = 0
            self.safe_day_nums = 2
            pass

class Shelf:
    taizhang_id = None
    shelf_id = None
    shelf_type = None
    mch_code = None
    goods_level_id = None
    level_depth = 0
    face_num = 0
