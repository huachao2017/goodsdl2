from goods.sellgoods.sql import sales_quantity
from set_config import config
from goods.sellgoods.salesquantity.utils import mysql_util

erp = config.erp
ms = config.ms
def start_order(dmstore_shop_id,upc):
    try:
        erp_ins = mysql_util.MysqlUtil(erp)
        ms_get_shop = sales_quantity.sql_params['ms_get_shop']
        ms_get_shop = ms_get_shop.format(dmstore_shop_id)
        print ("查dmstore shop 关系表， 获取ms 的shop_id")
        print (ms_get_shop)
        result = erp_ins.selectOne(ms_get_shop)
        ms_shop_id = result[0]

        ms_get_ghs_id = sales_quantity.sql_params['ms_get_ghs_id']
        ms_get_ghs_id = ms_get_ghs_id.format(ms_shop_id)
        print (ms_get_ghs_id)
        ms_ins = mysql_util.MysqlUtil(ms)
        result2 = ms_ins.selectOne(ms_get_ghs_id)
        ghs_id = result2[0]
        ms_get_start_num = sales_quantity.sql_params['ms_get_start_num']
        ms_get_start_num = ms_get_start_num.format(upc,ghs_id)
        print("查ms  关系表， 获取ms 的步长和起订量")
        print (ms_get_start_num)
        result1 = ms_ins.selectOne(ms_get_start_num) # 步长 ，起订量
        return result1[0],result1[1]
    except:
        print ("get data from ms error!")
        return None, None