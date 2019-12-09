from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.sellgoods.salesquantity.service.order_version_5.data_util.goods_info import get_shop_order_goods
from goods.sellgoods.salesquantity.local_util.config_table_util import ConfigTableUtil
from goods.sellgoods.salesquantity.bean import goods_config_disnums,goods_config_safedays
from goods.sellgoods.salesquantity.bean import taskflow
import math
import demjson
import time
def get_saleorder_ins(drg_ins, shop_id,shop_type):
    sales_order_ins = SalesOrder()
    sales_order_ins.shopid = shop_id
    if drg_ins.package_type in taskflow.package_type_name_dict.keys():
        sales_order_ins.package_type = taskflow.package_type_name_dict[drg_ins.package_type]
    else:
        sales_order_ins.package_type = taskflow.package_type_name_dict[0]
    sales_order_ins.shop_name = drg_ins.shop_name
    sales_order_ins.start_max = drg_ins.max_disnums
    sales_order_ins.start_min = drg_ins.min_disnums
    sales_order_ins.upc = drg_ins.upc
    sales_order_ins.predict_sale = drg_ins.predict_sales
    sales_order_ins.erp_shop_type = shop_type
    sales_order_ins.order_sale = 0
    sales_order_ins.max_stock = drg_ins.max_disnums
    sales_order_ins.min_stock = drg_ins.min_disnums
    sales_order_ins.min_disnums = drg_ins.min_disnums
    sales_order_ins.max_disnums = drg_ins.max_disnums
    sales_order_ins.stock = drg_ins.stock
    sales_order_ins.start_sum = drg_ins.start_sum
    sales_order_ins.multiple = drg_ins.multiple
    sales_order_ins.goods_name = drg_ins.goods_name
    sales_order_ins.supply_stock = drg_ins.supply_stock
    sales_order_ins.sales_nums = drg_ins.old_sales
    sales_order_ins.delivery_type = drg_ins.delivery_type
    sales_order_ins.storage_day = drg_ins.storage_day
    sales_order_ins.mch_goods_code = drg_ins.mch_code
    sales_order_ins.category_id = drg_ins.category_id
    sales_order_ins.category1_id = drg_ins.category1_id
    sales_order_ins.category2_id = drg_ins.category2_id
    sales_order_ins.psd_nums_4 = drg_ins.psd_nums_4
    sales_order_ins.psd_amount_4 = drg_ins.psd_amount_4
    sales_order_ins.face_num = 0
    sales_order_ins.sub_count = drg_ins.sub_count
    sales_order_ins.up_status = drg_ins.up_status
    sales_order_ins.upc_price = drg_ins.upc_price
    sales_order_ins.upc_psd_amount_avg_4 = drg_ins.upc_psd_amount_avg_4
    sales_order_ins.upc_psd_amount_avg_1 = drg_ins.upc_psd_amount_avg_1
    sales_order_ins.purchase_price = drg_ins.purchase_price
    sales_order_ins.max_scale = drg_ins.max_scale
    sales_order_ins.oneday_max_psd = drg_ins.oneday_max_psd
    shelf_data = []
    for shelf_ins in drg_ins.shelf_inss:
        sales_order_ins.face_num += shelf_ins.face_num
        shelf_data.append({"tz_id":shelf_ins.taizhang_id,"shelf_id":shelf_ins.shelf_id,"shelf_order":0,"face_num":shelf_ins.face_num})
    sales_order_ins.shelf_order_info = shelf_data
    return sales_order_ins


def get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result):
    jsondata = []
    for sales_order_ins in sales_order_inss:
        data_dict = {}
        data_dict['order_sale'] = sales_order_ins.order_sale
        data_dict['mch_goods_code'] = sales_order_ins.mch_goods_code
        data_dict['upc'] = sales_order_ins.upc
        data_dict['min_disnums'] = sales_order_ins.min_disnums
        data_dict['max_disnums'] = sales_order_ins.max_disnums
        data_dict['shop_stock'] = sales_order_ins.stock
        data_dict['supply_stock'] = sales_order_ins.supply_stock
        data_dict['shelf_order_info'] = sales_order_ins.shelf_order_info
        jsondata.append(data_dict)
    order_data = demjson.encode(jsondata)
    order_all_data = get_order_all_data(result,sales_order_inss)
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return [(batch_id,order_data,create_time,update_time,uc_shop_id,order_all_data)]


def get_order_all_data(result,sales_order_inss):
    jsondata=[]
    print("订货数,门店id,门店名称,商品id,upc,商品名称,"
          "一级分类,二级分类,三级分类,face数,陈列规格,"
          "模板店4周预估psd,模板店4周预估psd金额,配送单位,最小陈列数,"
          "最大陈列数,门店库存,仓库库存,配送类型,保质期,"
          "起订量,在途订货数,进货价,商品单价,开店以来单天最大psd数量,"
          "最大陈列比例,4周实际销售psd数量,1周实际销售psd数量,是否是新品,安全天数")
    for mch_code in result:
        mch_goods_dict = {}
        drg_ins = result[mch_code]
        order_sale = 0
        for sales_order_ins in sales_order_inss:
            if drg_ins.upc == sales_order_ins.upc:
                order_sale = sales_order_ins.order_sale
        mch_goods_dict['order_sale'] = order_sale
        mch_goods_dict['ucshop_id'] = drg_ins.ucshop_id
        mch_goods_dict['shop_name'] = drg_ins.shop_name
        mch_goods_dict['mch_code'] = drg_ins.mch_code
        mch_goods_dict['upc'] = drg_ins.upc
        mch_goods_dict['goods_name'] = drg_ins.goods_name
        mch_goods_dict['category1_id'] = drg_ins.category1_id
        mch_goods_dict['category2_id'] = drg_ins.category2_id
        mch_goods_dict['category_id'] = drg_ins.category_id
        mch_goods_dict['face_num'] = drg_ins.face_num
        mch_goods_dict['package_type'] = drg_ins.package_type
        mch_goods_dict['psd_nums_4'] = drg_ins.psd_nums_4
        mch_goods_dict['psd_amount_4'] = drg_ins.psd_amount_4
        mch_goods_dict['start_sum'] = drg_ins.start_sum
        mch_goods_dict['min_disnums'] = drg_ins.min_disnums
        mch_goods_dict['max_disnums'] = drg_ins.max_disnums
        mch_goods_dict['stock'] = drg_ins.stock
        mch_goods_dict['supply_stock'] = drg_ins.supply_stock
        mch_goods_dict['delivery_type'] = drg_ins.delivery_type
        mch_goods_dict['storage_day'] = drg_ins.storage_day
        mch_goods_dict['sub_count'] = drg_ins.sub_count
        mch_goods_dict['purchase_price'] = drg_ins.purchase_price
        mch_goods_dict['upc_price'] = drg_ins.upc_price
        mch_goods_dict['oneday_max_psd'] = float(drg_ins.oneday_max_psd / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_4'] = float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_1'] = float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)
        mch_goods_dict['up_status'] = drg_ins.up_status
        mch_goods_dict['safe_day_nums'] = drg_ins.safe_day_nums
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              % (str(order_sale),
                 str(drg_ins.ucshop_id), str(drg_ins.shop_name), str(drg_ins.mch_code),
                 str(drg_ins.upc), str(drg_ins.goods_name),
                 str(drg_ins.category1_id), str(drg_ins.category2_id), str(drg_ins.category_id), str(drg_ins.face_num),
                 str(drg_ins.package_type),
                 str(drg_ins.psd_nums_4), str(drg_ins.psd_amount_4), str(drg_ins.start_sum), str(drg_ins.min_disnums),
                 str(drg_ins.max_disnums), str(drg_ins.stock), str(drg_ins.supply_stock), str(drg_ins.delivery_type),
                 str(drg_ins.storage_day),
                 str(drg_ins.start_sum), str(drg_ins.sub_count), str(drg_ins.purchase_price), str(drg_ins.upc_price),
                 str(float(drg_ins.oneday_max_psd / drg_ins.upc_price)),
                 str(drg_ins.max_scale), str(float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)),
                 str(float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)), str(drg_ins.up_status),
                 str(drg_ins.safe_day_nums),
                 ))
        jsondata.append(mch_goods_dict)
    order_all_data = demjson.encode(jsondata)
    return order_all_data



def data_process(shop_id,shop_type):
    result = get_shop_order_goods(shop_id, shop_type)
    sales_order_inss = []
    if result == None or len(result.keys()) < 1:
        print("shop_id day generate order failed ,get_data error   " + str(shop_id))
        return

    config_ins = ConfigTableUtil()
    disnums_inss = config_ins.select_all_disnums(shop_id)

    #插入最小最大陈列数 单face   并同时修订最小最大陈列数
    data1 = get_insert_disnums_data(shop_id ,disnums_inss,result)

    if len(data1) == 0 :
        print ("任务执行的一个周期内， 没有单face的最小最大陈列数 修订... ")
    else:
        config_ins.insert_many_disnums(data1)

    # 插入安全库存天数 ， 并同时修订安全库存天数
    safedays_inss = config_ins.select_all_safedays(shop_id)
    data2 = get_insert_safedays_data(shop_id,safedays_inss,result)
    if len(data2) == 0 :
        print ("任务执行的一个周期内， 没有安全天数的 修订... ")
    else:
        config_ins.insert_many_safedays(data2)

    return result


def get_insert_safedays_data(shop_id,safedays_inss,result):
    config_safedays_inss = []
    safedays_inss_dict = {}
    for safedays_ins in safedays_inss:
        safedays_inss_dict[str(safedays_ins.upc)] = safedays_ins

    for mch_code in result:
        drg_ins = result[mch_code]
        if drg_ins.upc in list(safedays_inss_dict.keys()):
            drg_ins.safe_day_nums = safedays_inss_dict[drg_ins.upc].safe_day_nums
        else:
            config_safedays_ins = init_configsafedays(shop_id,drg_ins)
            config_safedays_inss.append(config_safedays_ins)
    data = []
    for config_safedays_ins in config_safedays_inss:
        data.append((config_safedays_ins.shop_id,config_safedays_ins.upc,config_safedays_ins.goods_name,config_safedays_ins.safe_day_nums,config_safedays_ins.create_time,config_safedays_ins.update_time))
    return data
def get_insert_disnums_data(shop_id ,disnums_inss,result):
    config_disnums_inss = []
    disnums_inss_dict = {}
    for disnums_ins in disnums_inss:
        disnums_inss_dict[str(disnums_ins.shelf_id)+"_"+str(disnums_ins.upc)] = disnums_ins

    for mch_code in result:
        drg_ins = result[mch_code]
        min_disnums = 0
        max_disnums = 0
        for shelf_ins in drg_ins.shelf_inss:
            key = str(shelf_ins.shelf_id) + "_" + str(drg_ins.upc)
            if key in list(disnums_inss_dict.keys()):
                if disnums_inss_dict[key].single_face_min_disnums is not None and disnums_inss_dict[key].single_face_min_disnums > 0 and int(disnums_inss_dict[key].shelf_depth) == int(shelf_ins.level_depth) and int(disnums_inss_dict[key].goods_depth == drg_ins.depth):
                    min_disnums += disnums_inss_dict[key].single_face_min_disnums
                else:
                    min_disnums += get_single_face_min_disnums(drg_ins,shelf_ins)

                if disnums_inss_dict[key].single_face_max_disnums is not None and  disnums_inss_dict[key].single_face_max_disnums > 0 and int(disnums_inss_dict[key].shelf_depth == shelf_ins.level_depth) and int(disnums_inss_dict[key].goods_depth == drg_ins.depth):
                    max_disnums += shelf_ins.face_num * disnums_inss_dict[key].single_face_max_disnums
                else:
                    max_disnums += get_single_face_max_disnums(drg_ins,shelf_ins)
                if int(disnums_inss_dict[key].shelf_depth) != int(shelf_ins.level_depth) or int(disnums_inss_dict[key].goods_depth) != int(drg_ins.depth):
                    config_ins = ConfigTableUtil()
                    disnums_ins = get_update_disnums(drg_ins,shelf_ins,disnums_inss_dict[key])
                    config_ins.update_disnums(disnums_ins)
            else:
                drg_ins.isnew_goods = True
                config_disnums_ins = init_configdisnums(shop_id, shelf_ins, drg_ins)
                config_disnums_inss.append(config_disnums_ins)
        if drg_ins.min_disnums != min_disnums and min_disnums != 0 :
            drg_ins.min_disnums = min_disnums
        if drg_ins.max_disnums != max_disnums and max_disnums != 0 :
            drg_ins.max_disnums = max_disnums
    data = []
    if len(config_disnums_inss) > 0 :
        for config_disnums_ins in config_disnums_inss:
            data.append((config_disnums_ins.shop_id,config_disnums_ins.shelf_id,config_disnums_ins.shelf_type,config_disnums_ins.shelf_depth,config_disnums_ins.upc,config_disnums_ins.goods_name,config_disnums_ins.goods_depth,config_disnums_ins.create_time,config_disnums_ins.update_time))
    return data

def get_update_disnums(drg_ins,shelf_ins,disnums_ins):
    disnums_ins.shelf_type = shelf_ins.shelf_type
    disnums_ins.shelf_depth = shelf_ins.level_depth
    disnums_ins.goods_name = drg_ins.goods_name
    disnums_ins.goods_depth = drg_ins.depth
    disnums_ins.create_time =str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    disnums_ins.update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return disnums_ins

def init_configsafedays(shop_id,drg_ins):
    configsafeday_ins = goods_config_safedays.ConfigSafedayas()
    configsafeday_ins.shop_id = shop_id
    configsafeday_ins.upc = drg_ins.upc
    configsafeday_ins.goods_name = drg_ins.goods_name
    configsafeday_ins.safe_day_nums = drg_ins.safe_day_nums
    return configsafeday_ins

def get_single_face_min_disnums(drg_ins,shelf_ins):
    if drg_ins.storage_day < 15 :
        single_face_min_disnums = 1
    else:
        if shelf_ins.level_depth <= drg_ins.depth:
            min_face_disnum = 1
        else:
            min_face_disnum = math.floor(shelf_ins.level_depth / drg_ins.depth)
        single_face_min_disnums = min(3,min_face_disnum)
    return single_face_min_disnums

def get_single_face_max_disnums(drg_ins,shelf_ins):
    return max(1,math.floor(float(shelf_ins.level_depth) / drg_ins.depth))

def init_configdisnums(shop_id,shelf_ins,drg_ins):
    config_disnums_ins = goods_config_disnums.ConfigDisnums()
    config_disnums_ins.shop_id = shop_id
    config_disnums_ins.shelf_id = shelf_ins.shelf_id
    config_disnums_ins.upc = drg_ins.upc
    config_disnums_ins.shelf_depth = shelf_ins.level_depth
    config_disnums_ins.goods_name = drg_ins.goods_name
    config_disnums_ins.goods_depth = drg_ins.depth
    config_disnums_ins.shelf_type = shelf_ins.shelf_type
    config_disnums_ins.single_face_min_disnums = get_single_face_min_disnums(drg_ins,shelf_ins)
    config_disnums_ins.single_face_max_disnums = get_single_face_max_disnums(drg_ins,shelf_ins)
    return config_disnums_ins