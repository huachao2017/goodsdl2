#  stock_util 从陈列设计中  取upc
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
    sql2 = sales_quantity.sql_params["tz_sums2"]
    sql2 = sql2.format(shop_id)
    results2 = mysql_ins.selectAll(sql2)
    if results2 is None or len(list(results2))<=0:
        print("shop 未设计台账")
        return None

    print ("len(results2)"+str(len(results2)))
    shelf_good_infos =[]
    shelf_infos = []
    tz_ids = []
    for row2 in results2:
        tz_ids.append(row2[0])
        shelf_good_info = row2[1]
        shelf_good_infos.append(shelf_good_info)
        shelf_info = row2[2]
        shelf_infos.append(shelf_info)
    upcs, upcs_shelf_infos = get_min_sku(shelf_good_infos,shelf_infos,tz_ids,mysql_ins)
    print ("upcs:"+str(len(list(set(upcs)))))
    upc_min_nums = get_min_sku_upc(list(set(upcs)))
    upcs_max_nums = get_max_sku_upc(list(set(upcs)),upcs_shelf_infos)
    upc_min_max = {}
    for upc in upc_min_nums:
        if upc in list(upcs_max_nums.keys()):
            upc_min_max[upc] = (upc_min_nums[upc],upcs_max_nums[upc])
        else:
            upc_min_max[upc] = (upc_min_nums[upc], None)
    return upc_min_max

def get_min_sku_upc(upcs):
    upc_mins = {}
    for upc in upcs:
       upc_mins[upc]=0
    for upc in upc_mins:
        i = 0
        for upc1 in upcs:
            if upc == upc1:
                i+=1
        upc_mins[upc] = i
    return upc_mins

def get_max_sku_upc(upcs_set,upcs_shelf_info):
    upc_max_nums = {}
    for upc in  upcs_set:
        upc_max_nums[upc] = 0
    for upc in upc_max_nums:
        i = 0
        for upc_info in upcs_shelf_info:
            (upc1, shelf_id, shelf_depth,upc_depth) = upc_info
            if upc1 == upc:
                max_nums = 0
                if float(upc_depth) != 0.0:
                    max_nums = int(float(shelf_depth) / float(upc_depth))
                i+=max_nums
        upc_max_nums[upc] = i
    return upc_max_nums


#解析shelf_good_info 获取upcs 和 upc shelf shelf_depth
def get_min_sku(shelf_good_infos,shelf_infos,tz_ids,mysql_ins):
    shelfs = []
    upcs = []
    upcs_shelf_info=[]
    for shelf_good_info in shelf_good_infos:
        # for shelf_kk in list(demjson.decode(shelf_good_info)):
        #     shelfs.append(shelf_kk)
        shelfs.append(dict(list(demjson.decode(shelf_good_info))[0]))
    shelf_ids_info = []
    for shelf_info in shelf_infos:
        shelfid = dict(demjson.decode(shelf_info))['shelf_id']
        depth = dict(demjson.decode(shelf_info))['depth']
        shelf_ids_info.append((shelfid,depth))
    lens = len(shelf_ids_info)
    for i in range(lens):
        tz_id = tz_ids[i]
        # 获取 mch_id 上家id
        sql_mch_id = sales_quantity.sql_params["tz_mch_id"]
        sql_mch_id = sql_mch_id.format(tz_id)
        result = mysql_ins.selectOne(sql_mch_id)
        mch_id = result[0]
        shelf = dict(shelfs[i])
        shelf_id_info = shelf_ids_info[i]
        layerArray = list(shelf["layerArray"])
        floor_num = len(layerArray)
        floor = range(floor_num)
        for fl, fl_goods in zip(floor, layerArray):
            fl_goods = list(fl_goods)
            for good in fl_goods:
                good = dict(good)
                mch_goods_code = good['mch_goods_code']
                upc = good['goods_upc']
                if str(upc) != 'undefined' and str(upc) != '' :
                    sql_upc_depth = sales_quantity.sql_params["upc_mch_code"]
                    sql_upc_depth = sql_upc_depth.format(upc,mch_id,mch_goods_code)
                    print (sql_upc_depth)
                    upc_result = mysql_ins.selectOne(sql_upc_depth)
                    if upc_result is not None:
                        upc1_depth = upc_result[4]
                        upc1 = upc_result[1]
                        if upc == upc1:
                            upcs_shelf_info.append((str(upc), shelf_id_info[0],shelf_id_info[1],upc1_depth))
                            upcs.append(str(upc))
                        else:
                            print ("upc select one error !!!!  failed     "+sql_upc_depth)
                            upcs_shelf_info.append((str(upc), shelf_id_info[0], shelf_id_info[1], 0))
                            upcs.append(str(upc))
    return upcs,upcs_shelf_info




