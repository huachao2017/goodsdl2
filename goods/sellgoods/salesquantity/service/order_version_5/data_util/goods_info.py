
import json
import time
import datetime
import main.import_django_settings
import math
from django.db import connections
import traceback
from goods import utils
from set_config import config

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
    try:
        cursor_bi = connections['bi'].cursor()
    except:
        cursor_bi = None
    # 获取台账系统的uc_shopid
    cursor.execute('select id, shop_name , mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    (uc_shopid, shop_name,mch_id) = cursor.fetchone()
    # 获取erp系统的erp_shopid
    cursor_dmstore.execute("select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 0".format(shopid))
    (erp_shop_id,) = cursor_dmstore.fetchone() # 门店id
    cursor_dmstore.execute(
        "select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 1".format(shopid))
    (erp_supply_id,) = cursor_dmstore.fetchone() # 仓库id

    cursor_dmstore.execute(
        "select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 2".format(shopid))
    (erp_resupply_id,) = cursor_dmstore.fetchone()  # 供货商id

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
            cursor.execute("select id,shelf_type_id,length,height,depth from sf_shelf where id = {}".format(shelf_id))
            (id,shelf_type_id,shelf_length,shelf_height,shelf_depth) = cursor.fetchone()
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
        print(shelf_id)
        for shelfId in shelf_dict.keys():
            level_array = shelf_dict[shelfId]
            goods_array = goods_array_dict[shelfId]
            for i in range(len(level_array)):
                level = level_array[i]
                goods_level_array = goods_array[i]
                level_depth = round(float(level['depth']))
                for goods in goods_level_array:
                    mch_code = goods['mch_goods_code']
                    height = goods['p_height']
                    width = goods['p_width']
                    depth = goods['p_depth']
                    shelf_ins = Shelf()
                    shelf_ins.shelf_length = shelf_length
                    shelf_ins.shelf_height = shelf_height
                    shelf_ins.shelf_depth = shelf_depth
                    shelf_ins.taizhang_id = taizhang_id
                    shelf_ins.shelf_id = shelf_id
                    shelf_ins.shelf_type = shelf_type
                    shelf_ins.mch_code = mch_code
                    shelf_ins.goods_level_id = i
                    shelf_ins.level_depth = level_depth
                    shelf_ins.face_num = 1
                    shelf_inss.append(shelf_ins)
                    if mch_code in ret:
                        print ("该商品已加入,更新和face相关的参数")
                        drg_ins = ret[mch_code]
                        new_shelf_inss = []
                        max_disnums = 0
                        min_disnums = 0
                        face_num = 0
                        for shelf_ins in shelf_inss:
                            if shelf_ins.mch_code == mch_code:
                                face_num += shelf_ins.face_num
                                min_disnums += shelf_ins.face_num
                                max_disnums += int(shelf_ins.face_num * math.floor(shelf_ins.level_depth / drg_ins.depth))
                                new_shelf_inss.append(shelf_ins)
                        drg_ins.face_num = face_num
                        drg_ins.max_disnums = max_disnums
                        drg_ins.shelf_inss = new_shelf_inss
                        drg_ins.min_disnums = min_disnums
                    else:
                        # 获取商品属性
                        try:
                            cursor.execute(
                                "select id, goods_name,upc, tz_display_img, spec, volume,is_superimpose,is_suspension,delivery_type,category1_id,category2_id,category_id,storage_day,package_type from uc_merchant_goods where mch_id = {} and mch_goods_code = {}".format(
                                    mch_id, mch_code))
                            # FIXME width,height暂时翻转
                            # (goods_id, goods_name, upc, tz_display_img, spec, volume, width, height, depth,is_superimpose,is_suspension) = cursor.fetchone()
                            (goods_id, goods_name, upc, tz_display_img, spec, volume, is_superimpose,
                             is_suspension,delivery_type,category1_id,category2_id,category_id,storage_day,package_type) = cursor.fetchone()
                        except:
                            print('台账找不到商品，只能把这个删除剔除:{}！'.format(mch_code))
                            continue
                        scale = None
                        max_scale = 1
                        # 获取最大陈列系数
                        try:
                            cursor.execute(
                                "select cat3_id,scale from sf_goods_categorymaxdisplayscale where mch_id = {} and cat3_id = '{}' ".format(
                                    mch_id,category_id))
                            (cat3_id, scale) = cursor.fetchone()
                            if scale is None:
                                max_scale = 1
                            else:
                                max_scale = float(scale)
                        except:
                            print('台账找不到商品的最大陈列系数:{}！'.format(mch_code))
                            scale = None
                        try:
                            if scale is None:
                                cursor.execute(
                                    "select cat2_id,,scale from sf_goods_categorymaxdisplayscale where mch_id = {} and cat2_id = '{}' ".format(
                                        mch_id, category2_id))
                                (cat2_id, scale) = cursor.fetchone()
                                if scale is None:
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
                                        "SELECT DISTINCT(payment.id) FROM payment WHERE payment.status = 10 AND create_time >= '{} 00:00:00' AND create_time < '{} 00:00:00' )"
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

                        #  废弃率 ，废弃后毛利率 计算
                        loss_avg=0  # 7天平均废弃率
                        loss_avg_nums = 0 # 7天的平均废弃量
                        loss_avg_profit_amount = 0 # 7天平均废弃后毛利率
                        loss_avg_amount = 0 # 7天平均废弃额
                        try:
                            cursor_dmstore.execute(
                                "select id,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (shop_goods_id,upc_stock) = cursor_dmstore.fetchone()

                            sql_loss = "select  T.nums,T.amounts,T.create_date,T2.handle_amount,T2.handle_number,T2.price,T2.purchase_price from (SELECT shop_goods_id as t1_shop_goods_id,T1.handle_amount,T1.handle_number,T1.price,T1.purchase_price,DATE_FORMAT(T1.create_time,'%Y-%m-%d') as t1_create_date  FROM shop_goods_loss_record T1 where shop_id = {} AND shop_goods_id = {} and create_time >= '{} 00:00:00'  and create_time < '{} 00:00:00') T2 LEFT JOIN ( "\
                                            "SELECT shop_goods_id ,sum(number) AS nums,sum(amount) as amounts,DATE_FORMAT(create_time,'%Y-%m-%d') as create_date FROM payment_detail "\
	                                            "WHERE shop_id = {} AND shop_goods_id = {} AND number > 0 AND create_time >= '{} 00:00:00' AND create_time < '{} 00:00:00' AND payment_id IN ( "\
			                                        "SELECT DISTINCT(payment.id) FROM payment WHERE payment.status = 10 AND create_time >= '{} 00:00:00' AND create_time < '{} 00:00:00' "\
		                                            " )" \
                                            "GROUP BY DATE_FORMAT(create_time,'%Y-%m-%d') "\
                                            ") T  on T.shop_goods_id = T2.t1_shop_goods_id and T.create_date = T2.t1_create_date "
                            end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
                            start_date = str(
                                (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                                    days=-7)).strftime("%Y-%m-%d"))
                            sql_loss = sql_loss.format(shopid,shop_goods_id,start_date,end_date,shopid,shop_goods_id,start_date,end_date,start_date,end_date)
                            cursor_dmstore.execute(sql_loss)
                            loss_results = cursor_dmstore.fetchall()
                            if loss_results is not None and len(loss_results) > 0:
                                for loss_result in loss_results:
                                    loss_avg_one_day = 0
                                    upc_sale_nums = loss_result[0]
                                    upc_sale_amounts = loss_result[1]
                                    upc_sale_create_date = loss_result[2]
                                    upc_handle_amounts = loss_result[3]
                                    upc_handle_nums = loss_result[4]
                                    upc_loss_price = loss_result[5]
                                    upc_loss_purchase_price = loss_result[6]
                                    if upc_handle_nums is not None:
                                        loss_avg_nums+=upc_handle_nums
                                    if upc_handle_amounts is not None and upc_sale_nums is not None:
                                        loss_avg_one_day = float(upc_handle_amounts / (upc_handle_amounts+upc_sale_nums))
                                    elif upc_handle_amounts is not None and upc_sale_nums is None:
                                        loss_avg_one_day =  float(upc_handle_amounts / (upc_handle_amounts))
                                    loss_avg += loss_avg_one_day
                                    # 计算废弃后毛利率
                                    if upc_sale_amounts is not None and upc_sale_amounts != 0 :
                                        if upc_loss_purchase_price is not None and upc_sale_amounts is not None and upc_sale_nums is not None and upc_handle_nums is not None:
                                            loss_avg_profit_amount += (upc_sale_amounts - upc_handle_amounts - upc_handle_nums * upc_loss_purchase_price) / upc_sale_amounts
                                    else:
                                        loss_avg_amount += 0-upc_handle_amounts
                                loss_avg = float(loss_avg / 7)
                                loss_avg_amount = float(loss_avg_amount /7)
                                loss_avg_profit_amount = float(loss_avg_profit_amount /7)
                                loss_avg_nums = float(loss_avg_nums /7)
                        except Exception as e :
                            print ("dmstore 废弃率 计算失败 {}-{}-{}".format(shopid, upc,goods_name))
                            traceback.print_exc()
                            loss_avg = 0
                            loss_avg_profit_amount = 0
                            loss_avg_amount = 0
                            loss_avg_nums = 0

                        if erp_resupply_id is not None:
                            try:
                                # 获取起订量
                                # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                                cursor_erp.execute(
                                    "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}' and s.party_code = '{}'".format(
                                        erp_resupply_id, upc,mch_code))
                                (sku_id,) = cursor_erp.fetchone()
                                cursor_erp.execute(
                                    "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(
                                        sku_id))
                                (start_sum, multiple) = cursor_erp.fetchone()
                            except:
                                print('Erp找不到商品:{}-{}！'.format(upc, erp_resupply_id))
                                start_sum = 0
                                multiple = 0
                        else:
                            start_sum = 0
                            multiple = 0
                        try:
                            # 获取小仓库库存
                            cursor_erp.execute(
                                "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}' and s.party_code = '{}' ".format(
                                    erp_supply_id, upc,mch_code))
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
                            cursor_erp.execute(
                                "SELECT sum(sub_item_count) as sub_count from ls_sub_item where  sub_number in  (SELECT sub_number from ls_sub where  seller_shop_id={} AND status=50) AND sku_id =(SELECT sku_id FROM ls_sku sku, ls_prod  prod where prod.prod_id= sku.prod_id AND prod.shop_id={}  and sku.model_id='{}' )".format(
                                    erp_resupply_id,erp_resupply_id,upc))
                            (sub_count,) = cursor_erp.fetchone()
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
                                "select DATE_FORMAT(up_shelf_date,'%Y-%m-%d') as upshelf_date,is_new_goods from goods_up_shelf_datetime where shopid={} and upc='{}'".format(
                                    uc_shopid, upc))
                            (up_shelf_date,up_status) = cursor_ai.fetchone()
                            up_shelf_date = str(up_shelf_date)
                            print('ai找到商品上架时间 :{}-{}-{}！'.format(uc_shopid, upc,up_shelf_date))
                        except:
                            # print('ai找不到销量预测:{}-{}-{}！'.format(shopid,upc,next_day))
                            up_shelf_date = str(time.strftime('%Y-%m-%d', time.localtime()))
                            up_status = 1

                        # TODO 获取bi 数据库 ， 品的psd金额   mch_id  dmstore_shopid  goods_code
                        upc_psd_amount_avg_1 = 0
                        upc_psd_amount_avg_1_5 = 0
                        upc_psd_amount_avg_6_7 = 0
                        try:
                            cursor_dmstore.execute(
                                "select goods_id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (goods_id, upc_price, purchase_price, stock) = cursor_dmstore.fetchone()
                            end_date = str(time.strftime('%Y%m%d', time.localtime()))
                            start_date_1 = str((datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(days=-7)).strftime("%Y%m%d"))
                            print ("获取bi 真实psd {} ,{},{},{},{}".format(shopid,goods_id,mch_id,upc,goods_name))
                            sql_1 = "select psd,date from tj_goods_day_psd where mch_id = {} and shop_id = {} and goods_code = {} and date >= {} and date < {}".format(mch_id,shopid,goods_id,int(start_date_1),int(end_date))
                            cursor_bi.execute(sql_1)
                            res1 = cursor_bi.fetchall()

                            if res1 is None or len(res1) < 1:
                                upc_psd_amount_avg_1 = 0
                            else:
                                res_len1 = 0
                                psd_amount = 0
                                psd_amount_1_5 = 0
                                psd_amount_6_7 = 0
                                for re in res1:
                                    psd_amount += re[0]
                                    day_date = re[1]
                                    weekday_i = datetime.datetime.strptime(str(day_date), "%Y%m%d").weekday() + 1
                                    if weekday_i >= 1 and  weekday_i<=5:
                                        psd_amount_1_5 += re[0]
                                    else:
                                        psd_amount_6_7 += re[0]
                                    res_len1+=1
                                upc_psd_amount_avg_1 = float(psd_amount / 7)
                                upc_psd_amount_avg_1_5 = float(psd_amount_1_5 / 5)
                                upc_psd_amount_avg_6_7 = float(psd_amount_6_7 / 2)
                        except:
                            print('bi 找不到psd  4！{},{}'.format(shopid, upc))
                            upc_psd_amount_avg_1 = 0
                            upc_psd_amount_avg_1_5 = 0
                            upc_psd_amount_avg_6_7 = 0
                        upc_psd_amount_avg_4 = 0
                        try:
                            cursor_dmstore.execute(
                                "select goods_id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (goods_id, upc_price, purchase_price, stock) = cursor_dmstore.fetchone()
                            end_date = str(time.strftime('%Y%m%d', time.localtime()))
                            start_date_4 = str(
                                (datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(
                                    days=-28)).strftime("%Y%m%d"))
                            sql_2 = "select psd from tj_goods_day_psd where mch_id = {} and shop_id = {} and goods_code = {} and  date >= {} and date < {}".format(
                                mch_id, shopid, goods_id,int(start_date_4),int(end_date))
                            cursor_bi.execute(sql_2)
                            res2 = cursor_bi.fetchall()
                            if res2 is None or len(res2) < 1:
                                upc_psd_amount_avg_4 = 0
                            else:
                                res_len2 = 0
                                psd_amount2 = 0
                                for re in res2:
                                    psd_amount2 += re[0]
                                    res_len2 += 1
                                upc_psd_amount_avg_4 = float(psd_amount2 / 28)
                        except:
                            print('bi 找不到psd  4！{},{}'.format(shopid,upc))
                            upc_psd_amount_avg_4 = 0
                        # 单天最大psd
                        oneday_max_psd = 0
                        try:
                            if shopid in list(config.shellgoods_params['start_shop'].keys()):
                                cursor_dmstore.execute(
                                    "select goods_id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                        upc, shopid))
                                (goods_id, upc_price, purchase_price, stock) = cursor_dmstore.fetchone()
                                start_shop_date = int(config.shellgoods_params['start_shop'][shopid])
                                end_date = str (time.strftime('%Y%m%d', time.localtime()))
                                sql_2 = "select psd from tj_goods_day_psd where mch_id = {} and shop_id = {} and goods_code = {} and  date >= {} and date <= {} order by psd desc limit 1 ".format(
                                    mch_id, shopid, goods_id, start_shop_date, int(end_date))
                                cursor_bi.execute(sql_2)
                                (oneday_max_psd,) = cursor_bi.fetchone()
                                print ("找到  oneday_max_psd "+str(oneday_max_psd)+",upc="+str(upc))
                                print ("%s,%s,%s,%s,%s" % (str(mch_id), str(shopid), str(goods_id), str(start_shop_date), str(int(end_date))))
                        except:
                            print('bi 找不到psd  one_day max ！{},{}'.format(shopid, upc))
                            traceback.print_exc()
                            oneday_max_psd = 0

                        psd_nums_2_cls, psd_amount_2_cls = 0, 0
                        try:
                            psd_nums_2_cls, psd_amount_2_cls = utils.select_category_psd_data(category_id,shopid,14)
                        except:
                            print("select_psd_data is error ,upc=" + str(upc) + ",shop_id=" + str(shopid))
                            psd_nums_2_cls, psd_amount_2_cls = 0, 0
                        psd_nums_4, psd_amount_4 = 0, 0
                        psd_nums_2, psd_amount_2 = 0, 0
                        try:
                            psd_nums_4, psd_amount_4 = utils.select_psd_data(upc, shopid, 28)
                            psd_nums_2, psd_amount_2 = utils.select_psd_data(upc, shopid, 14)
                        except:
                            print("select_psd_data is error ,upc=" + str(upc)+",shop_id="+str(shopid))
                            traceback.print_exc()
                            psd_nums_4 = 0
                            psd_amount_4 = 0
                            psd_nums_2, psd_amount_2 = 0,0


                        ret[mch_code] = DataRawGoods(mch_code, goods_name, upc, tz_display_img,corp_classify_code, spec, volume, width, height, depth,
                                                      start_sum,multiple,
                                                     stock = stock,
                                                     predict_sales = sales,
                                                     supply_stock=supply_stock,old_sales = sales_nums,delivery_type=delivery_type,category1_id=category1_id,
                                                     category2_id=category2_id,category_id=category_id,storage_day=storage_day,shelf_inss=shelf_inss,
                                                     shop_name=shop_name,uc_shopid=uc_shopid,package_type=package_type,dmstore_shopid=shopid,
                                                     up_shelf_date = up_shelf_date,up_status = up_status,sub_count = sub_count,upc_price=upc_price,
                                                     upc_psd_amount_avg_4=upc_psd_amount_avg_4,purchase_price = purchase_price,upc_psd_amount_avg_1=upc_psd_amount_avg_1,
                                                     psd_nums_4=psd_nums_4,psd_amount_4=psd_amount_4,max_scale=max_scale,oneday_max_psd = oneday_max_psd,psd_nums_2=psd_nums_2,
                                                     psd_amount_2=psd_amount_2,psd_nums_2_cls=psd_nums_2_cls, psd_amount_2_cls=psd_nums_2_cls,
                                                     upc_psd_amount_avg_1_5 = upc_psd_amount_avg_1_5,upc_psd_amount_avg_6_7 = upc_psd_amount_avg_6_7, loss_avg = loss_avg,
                                                     loss_avg_profit_amount = loss_avg_profit_amount, loss_avg_amount = loss_avg_amount,loss_avg_nums=loss_avg_nums)
    cursor.close()
    cursor_dmstore.close()
    cursor_erp.close()
    cursor_ai.close()
    if cursor_bi is not None:
        cursor_bi.close()
    procee_max_disnums(ret)
    return ret

# 最大陈列量做处理
def procee_max_disnums(ret):
    for mch_code in ret:
        drg_ins = ret[mch_code]
        drg_ins.max_disnums = drg_ins.max_disnums * drg_ins.max_scale

class DataRawGoods():
    def __init__(self, mch_code, goods_name, upc, tz_display_img, corp_classify_code, spec, volume, width, height, depth,  start_sum, multiple,
                 stock=0, predict_sales=0,supply_stock=0,old_sales=0,delivery_type=None,category1_id=None,category2_id=None,category_id=None,
                 storage_day=None,shelf_inss=None,shop_name=None,uc_shopid =None,package_type=None,dmstore_shopid = None,up_shelf_date = None,
                 up_status=None,sub_count = None,upc_price = None,upc_psd_amount_avg_4 = None,purchase_price = None,upc_psd_amount_avg_1=None,
                 psd_nums_4=None, psd_amount_4=None,max_scale=None,oneday_max_psd = None ,psd_nums_2=None, psd_amount_2=None,psd_nums_2_cls=None, psd_amount_2_cls=None,
                 upc_psd_amount_avg_1_5= None, upc_psd_amount_avg_6_7 = None, loss_avg = None,loss_avg_profit_amount = None, loss_avg_amount = None,loss_avg_nums = None):
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
        if width is None:
            self.width = 0
        else:
            self.width = width
        if height is None:
            self.height = 0
        else:
            self.height = height
        if oneday_max_psd is None :
            self.oneday_max_psd = 0
        else:
            self.oneday_max_psd = float(oneday_max_psd)
        if up_shelf_date is None:
            self.up_shelf_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        else:
            self.up_shelf_date = up_shelf_date
        if up_status is None :
            self.up_status = 1
        else:
            self.up_status = up_status

        if loss_avg is None:
            self.loss_avg = 0
        else:
            self.loss_avg = loss_avg
        if loss_avg_profit_amount is None:
            self.loss_avg_profit_amount = 0
        else:
            self.loss_avg_profit_amount = loss_avg_profit_amount

        if loss_avg_amount is None:
            self.loss_avg_amount = 0
        else:
            self.loss_avg_amount = loss_avg_amount

        if loss_avg_nums is None:
            self.loss_avg_nums = 0
        else:
            self.loss_avg_nums = loss_avg_nums


        if sub_count is None :
            self.sub_count = 0
        else:
            self.sub_count = float(sub_count)
        if upc_psd_amount_avg_4 is None:
            self.upc_psd_amount_avg_4 = 0
        else:
            self.upc_psd_amount_avg_4 = float(upc_psd_amount_avg_4)
        if upc_psd_amount_avg_1 is None:
            self.upc_psd_amount_avg_1 = 0
        else:
            self.upc_psd_amount_avg_1= float(upc_psd_amount_avg_1)

        if upc_psd_amount_avg_1_5 is None:
            self.upc_psd_amount_avg_1_5 = 0
        else:
            self.upc_psd_amount_avg_1_5 = float(upc_psd_amount_avg_1_5)

        if upc_psd_amount_avg_6_7 is None:
            self.upc_psd_amount_avg_6_7 = 0
        else:
            self.upc_psd_amount_avg_6_7 = float(upc_psd_amount_avg_6_7)

        if purchase_price is None:
            self.purchase_price = 1
        else:
            self.purchase_price = float(purchase_price)
        if upc_price is None or int(upc_price) == 0:
            self.upc_price = 1
        else:
            self.upc_price = float(upc_price)
        if psd_nums_4 is None:
            self.psd_nums_4 = 0
        else:
            self.psd_nums_4 = float(psd_nums_4)
        if psd_amount_4 is None:
            self.psd_amount_4 = 0
        else:
            self.psd_amount_4 = float(psd_amount_4)

        if psd_nums_2 is None:
            self.psd_nums_2 = 0
        else:
            self.psd_nums_2 = float(psd_nums_2)
        if psd_amount_2 is None:
            self.psd_amount_2 = 0
        else:
            self.psd_amount_2 = float(psd_amount_2)

        if psd_nums_2_cls is None:
            self.psd_nums_2_cls = 0
        else:
            self.psd_nums_2_cls = float(psd_nums_2_cls)
        if psd_amount_2_cls is None:
            self.psd_amount_2_cls = 0
        else:
            self.psd_amount_2_cls = float(psd_amount_2_cls)

        if package_type is None:
            self.package_type = 0
        else:
            self.package_type = package_type
        try:
            if depth is None or depth == '' or  float(depth) == 0 :
                self.depth = 0.001
            else:
                self.depth = float(depth)
        except:
            self.depth = 0.001
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
            self.delivery_type_true = 0
        if category_id is None:
            self.category_id = 0
        else:
            self.category_id = category_id
        if max_scale is None:
            self.max_scale = 1
        else:
            self.max_scale = float(max_scale)
        new_shelf_inss = []
        max_disnums = 0
        min_disnums = 0
        face_num = 0
        for shelf_ins in shelf_inss:
            if shelf_ins.mch_code == mch_code:
                face_num += shelf_ins.face_num
                min_disnums += shelf_ins.face_num
                max_disnums += int(shelf_ins.face_num * math.floor(shelf_ins.level_depth / self.depth))
                new_shelf_inss.append(shelf_ins)
        self.face_num = face_num
        self.shelf_inss = new_shelf_inss
        self.max_disnums = max_disnums
        self.min_disnums = min_disnums
        self.isnew_goods = False
        try:
            if storage_day is not None and int(storage_day) > 0:
                self.storage_day = storage_day
        except:
            print("商品的保质期error,mch_code=" + str(self.mch_code)+",goods_name="+str(self.goods_name))
            self.storage_day = 0


class Shelf:
    taizhang_id = None
    shelf_id = None
    shelf_type = None
    mch_code = None
    goods_level_id = None
    level_depth = 0
    face_num = 0
    shelf_length = None
    shelf_height = None
    shelf_depth = None
