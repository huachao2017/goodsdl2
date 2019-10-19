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
    shelf_good_infos =[]
    shelf_infos = []
    for row2 in results2:
        shelf_good_info = row2[1]
        shelf_good_infos.append(shelf_good_info)
        shelf_info = row2[2]
        shelf_infos.append(shelf_info)
    mch_goods_codes, mch_goods_shelf_info = get_min_sku(shelf_good_infos,shelf_infos)
    sql4 = sales_quantity.sql_params["tz_upc"]
    if len(mch_goods_codes) > 1:
        sql4 = sql4.format(str(tuple(list(set(mch_goods_codes)))))
    elif(len(mch_goods_codes)==1):
        code_s = str("("+mch_goods_codes[0]+")")
        if code_s == '()':
            print("get uc_merchant_goods error1 , upc = None")
            return None
        sql4 = sql4.format(code_s)
    print (sql4)
    upc_results = mysql_ins.selectAll(sql4)
    upc_min_nums, code_upc = get_min_sku_upc(upc_results,mch_goods_codes)

    upcs_max_nums = get_max_sku(code_upc,mch_goods_shelf_info)
    upc_min_max = {}
    for upc in upc_min_nums:
        if upc in list(upcs_max_nums.keys()):
            upc_min_max[upc] = (upc_min_nums[upc],upcs_max_nums[upc])
        else:
            upc_min_max[upc] = (upc_min_nums[upc], None)
    return upc_min_max

def get_min_sku_upc(upc_results,mch_goods_codes):
    code_upc = {}
    for row in upc_results:
        code = row[0]
        upc = row[1]
        depth = row[4]
        code_upc[code] = (upc,depth)
    upc_min_nums = {}
    for code in mch_goods_codes:
        if code in list(code_upc.keys()):
            (upc,depth) = code_upc[code]
            if upc not in list(upc_min_nums.keys()):
                upc_min_nums[upc] = 1
            else:
                nums = upc_min_nums[upc]
                nums+=1
                upc_min_nums[upc] =  nums
    return upc_min_nums , code_upc






def get_max_sku(code_upc,mch_goods_shelf_info):
    upc_max_nums = {}
    for mch_goods_code in mch_goods_shelf_info:
        (mch_goods_code, shelf_id, shelf_depth) = mch_goods_code
        for key in code_upc:
            if mch_goods_code == key:
                (upc,depth) = code_upc[key]
                if float(depth) != 0.0:
                    max_nums = int(float(shelf_depth)/float(depth))
                    if upc not in (list(upc_max_nums.keys())):
                        upc_max_nums[upc] = max_nums
                    else:
                        nums = upc_max_nums[upc]
                        upc_max_nums[upc] = nums+1
    return upc_max_nums


#解析shelf_good_info 获取最小库存
def get_min_sku(shelf_good_infos,shelf_infos):
    shelfs = []
    mch_goods_codes = []
    mch_goods_shelf_info=[]
    for shelf_good_info in shelf_good_infos:
        shelfs.append(dict(list(demjson.decode(shelf_good_info))[0]))
    shelf_ids_info = []
    for shelf_info in shelf_infos:
        shelfid = dict(demjson.decode(shelf_info))['shelf_id']
        depth = dict(demjson.decode(shelf_info))['depth']
        shelf_ids_info = [(shelfid,depth)]
    lens = len(shelf_ids_info)
    for i in range(lens):
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
                if str(mch_goods_code) != 'undefined' and str(mch_goods_code) != '' :
                    mch_goods_shelf_info.append((mch_goods_code, shelf_id_info[0],shelf_id_info[1]))
                    mch_goods_codes.append(mch_goods_code)
    return mch_goods_codes,mch_goods_shelf_info




