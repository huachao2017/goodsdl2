from goods.sellgoods.salesquantity.utils.mysql_util import MysqlUtil
from goods.sellgoods.sql import sales_quantity
from set_config import config
# import logging
import demjson
# logger = logging.setLoggerClass("detect")
erp = config.erp
ucenter = config.ucenter
def get_stock(shop_ids):
    shop_id_info = {}
    for shop_id in shop_ids:
        upc_stock = get_stock_from_erp(shop_id)
        upc_min_max=get_min_max_stock_from_ucenter(shop_id)
        upc_min_max_stock = {}
        for upc in upc_min_max:
            (min_stock,max_stock) = upc_min_max[upc]
            stock = None
            if upc in list(upc_stock.keys()):
                stock = upc_stock[upc]
            upc_min_max_stock[upc] = (min_stock,max_stock,stock)
        shop_id_info[shop_id] = upc_min_max_stock
    return shop_id_info


# 从erp取库存数据
def get_stock_from_erp(shop_id):
    mysql_ins = MysqlUtil(erp)
    sql = sales_quantity.sql_params["get_stock_erp"]
    sql = sql.format(shop_id)
    print (sql)
    results = mysql_ins.selectAll(sql)
    stocks = []
    total_stocks = []
    upcs = []
    shop_ids = []
    for row in results:
        stocks.append(row[0])
        total_stocks.append(row[1])
        upcs.append(row[2])
        shop_ids.append(row[3])
    upc_stock={}
    for upc,stock in zip(upcs,stocks):
        if upc not in list(upc_stock.keys()):
            upc_stock[upc] = 1
        else:
            upc_stock[upc] += 1
    return upc_stock


# 从ucenter取台账库存数据
def get_min_max_stock_from_ucenter(shop_id):
    print ("get_stock_from_ucenter")
    mysql_ins = MysqlUtil(ucenter)
    # sql1 = sales_quantity.sql_params["tz_sums1"]
    # sql1 = sql1.format(shop_id)
    sql2 = sales_quantity.sql_params["tz_sums2"]
    sql2 = sql2.format(shop_id)
    # results1 = mysql_ins.selectAll(sql1)
    results2 = mysql_ins.selectAll(sql2)
    # if results1 is None or len(list(results1))<=0:
    #     #     logger.info("shop 未关联台账")
    #     #     return None
    if results2 is None or len(list(results2))<=0:
        print("shop 未设计台账")
        return None
    shopid_tzsum = {}
    tzs = 0
    # for row in results1:
    #     shop_id = row[0]
    #     tzsum = row[1]
    #     tzs += tzsum
    #     shopid_tzsum[shop_id] = tzsum
    # tzsum_dis = len(list(results2))
    # 去掉 该逻辑 作为执行条件
    # if tzsum_dis != tzs:
    #     logger.info("台账数据不一致，不执行获取最小库存和生成订单")
    #     return None
    shelf_infos = []
    shelf_good_infos =[]
    upcs = {}
    upcs_shelf_info=[]
    shelf_ids = []
    shelf_good_infos = []
    shelf_infos = []
    for row2 in results2:
        shelf_good_info = row2[1]
        shelf_info = row2[2]
    upcs,upcs_shelf_info,shelf_ids = get_min_sku(shelf_good_infos,upcs,upcs_shelf_info,shelf_ids,shelf_infos)
    sql3 = sales_quantity.sql_params["tz_shelf"]
    shelf_ids_s = None
    if len(shelf_ids)>1:
        shelf_ids_s = str(tuple(shelf_ids))
    elif(len(shelf_ids)==1):
        shelf_ids_s = str("("+shelf_ids[0]+")")
    sql3 = sql3.format(shelf_ids_s)
    print (sql3)
    print (str(tuple(shelf_ids)))
    shelf_results = mysql_ins.selectAll(sql3)
    print (shelf_results[0])
    sql4 = sales_quantity.sql_params["tz_upc"]
    if len(upcs) > 1:
        sql4 = sql4.format(str(tuple(list(upcs.keys()))))
    elif(len(upcs)==1):
        if list(upcs.keys())[0] == '':
            print ("get uc_merchant_goods error , upc = None")
            return None
        upcs_s = str("("+"' "+list(upcs.keys())[0]+" '"+")")
        sql4 = sql4.format(upcs_s)
    print (sql4)
    print (str(tuple(list(upcs.keys()))))
    upc_results = mysql_ins.selectAll(sql4)
    upcs_max = get_max_sku(upcs_shelf_info,shelf_results,upc_results,upcs)
    upc_min_max = {}
    for upc in upcs:
        upc_min_max[upc] = (upcs[upc],upcs_max[upc])
    return upc_min_max


def get_max_sku(upcs_shelf_info,shelf_results,upc_results,upcs):
    shelf_depth_info = {}
    for shelf_row in shelf_results:
        shelf_depth_info[str(shelf_row[0])] = shelf_row[3]
    upc_depth_info = {}
    for upc_row in upc_results:
        upc_depth_info[upc_row[0]] = upc_row[3]
    upc_max={}
    print (shelf_depth_info)
    print (upcs_shelf_info)
    for (upc,shelfid) in upcs_shelf_info:
        shelf_depth = shelf_depth_info[shelfid]
        upc_depth = upc_depth_info[upc]
        upc_max_sums = None
        if (upc_depth==0):
            upc_max_sums = None
        else:
            upc_max_sums = int(shelf_depth/upc_depth)
        if upc not in list(upc_max.keys()):
            upc_max[upc] = upc_max_sums
        else:
            if upc_max[upc] is None:
                if upc_max_sums is not None:
                    upc_max[upc]=upc_max_sums
            else:
                if upc_max_sums is not None:
                    upc_max[upc] += upc_max_sums
    return upc_max


#解析shelf_good_info 获取最小库存
def get_min_sku(shelf_good_infos,upcs,upcs_shelf_info,shelf_ids,shelf_infos):
    shelfs = []
    for shelf_good_info in shelf_good_infos:
        shelfs.append(dict(list(demjson.decode(shelf_good_info))[0]))
    shelf_ids = []
    for shelf_info in shelf_infos:
        shelfid = dict(demjson.decode(shelf_info))['shelf_id']
        shelf_ids.append(shelfid)
        if shelfid not in shelf_ids:
            shelf_ids.append(shelfid)
    lens = len(shelf_ids)
    for i in range(lens):
        shelf = dict(shelfs[i])
        shelf_id = shelf_ids[i]
        layerArray = list(shelf["layerArray"])
        floor_num = len(layerArray)
        floor = range(floor_num)
        for fl, fl_goods in zip(floor, layerArray):
            fl_goods = list(fl_goods)
            for good in fl_goods:
                good = dict(good)
                if "goods_upc" not in list(good.keys()) or "top" not in list(
                        good.keys()) or "left" not in list(good.keys()) or "width" not in list(
                        good.keys()) or "height" not in list(good.keys()):
                    continue
                upc = good['goods_upc']
                if upc != 'undefined' and upc != '' :
                    upcs_shelf_info.append((upc, shelf_id))
                    if upc not in list(upcs.keys()) :
                        upcs[upc] = 1
                    else:
                        upcs[upc] = upcs[upc]+1
    return upcs,upcs_shelf_info,shelf_ids




