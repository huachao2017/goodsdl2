from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.sellgoods.salesquantity.service.order_version_3.data_util.goods_info import get_shop_order_goods
from goods.sellgoods.salesquantity.local_util.config_table_util import ConfigTableUtil
from goods.sellgoods.salesquantity.bean import goods_config_disnums,goods_config_safedays
import math
def get_saleorder_ins(drg_ins, shop_id,shop_type):
    sales_order_ins = SalesOrder()
    sales_order_ins.shopid = shop_id
    sales_order_ins.start_max = drg_ins.max_disnums
    sales_order_ins.start_min = drg_ins.min_disnums
    sales_order_ins.upc = drg_ins.upc
    sales_order_ins.predict_sale = drg_ins.predict_sales
    sales_order_ins.erp_shop_type = shop_type
    sales_order_ins.order_sale = 0
    sales_order_ins.max_stock = drg_ins.max_disnums
    sales_order_ins.min_stock = drg_ins.min_disnums
    sales_order_ins.stock = drg_ins.stock
    sales_order_ins.start_sum = drg_ins.start_sum
    sales_order_ins.multiple = drg_ins.multiple
    sales_order_ins.goods_name = drg_ins.goods_name
    sales_order_ins.supply_stock = drg_ins.supply_stock
    sales_order_ins.sales_nums = drg_ins.old_sales
    sales_order_ins.delivery_type = drg_ins.delivery_type
    return sales_order_ins




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
        data.append((config_safedays_ins.shop_id,config_safedays_ins.upc,config_safedays_ins.safe_day_nums,config_safedays_ins.goods_name,config_safedays_ins.create_time,config_safedays_ins.update_time))

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
                min_disnums += disnums_inss_dict[key].single_face_min_disnums
                max_disnums += shelf_ins.face_num * disnums_inss_dict[key].single_face_max_disnums
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
            data.append((config_disnums_ins.shop_id,config_disnums_ins.shelf_id,config_disnums_ins.shelf_type,config_disnums_ins.shelf_depth,config_disnums_ins.upc,config_disnums_ins.goods_name,config_disnums_ins.goods_depth,config_disnums_ins.single_face_min_disnums,config_disnums_ins.single_face_max_disnums,config_disnums_ins.create_time,config_disnums_ins.update_time))
    return data

def init_configsafedays(shop_id,drg_ins):
    configsafeday_ins = goods_config_safedays.ConfigSafedayas()
    configsafeday_ins.shop_id = shop_id
    configsafeday_ins.upc = drg_ins.upc
    configsafeday_ins.goods_name = drg_ins.goods_name
    configsafeday_ins.safe_day_nums = drg_ins.safe_day_nums

    return configsafeday_ins



def init_configdisnums(shop_id,shelf_ins,drg_ins):
    config_disnums_ins = goods_config_disnums.ConfigDisnums()
    config_disnums_ins.shop_id = shop_id
    config_disnums_ins.shelf_id = shelf_ins.shelf_id
    config_disnums_ins.upc = drg_ins.upc
    config_disnums_ins.shelf_depth = shelf_ins.level_depth
    config_disnums_ins.goods_name = drg_ins.goods_name
    config_disnums_ins.goods_depth = drg_ins.depth
    config_disnums_ins.shelf_type = shelf_ins.shelf_type
    if config_disnums_ins.shelf_depth >= config_disnums_ins.goods_depth :
        config_disnums_ins.single_face_min_disnums = 1
        config_disnums_ins.single_face_max_disnums = math.floor(float(config_disnums_ins.shelf_depth)/config_disnums_ins.goods_depth)

    return config_disnums_ins