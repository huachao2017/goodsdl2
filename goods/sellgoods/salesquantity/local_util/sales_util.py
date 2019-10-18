from set_config import config
from goods.sellgoods.salesquantity.utils import mysql_util
from goods.sellgoods.sql import sales_quantity
import time
erp = config.erp_dev
def get_predict_sales(shop_ids):
    mysql_ins = mysql_util.MysqlUtil(erp)
    sql = sales_quantity.sql_params["sales_ai"]
    exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    sql = sql.format(shop_ids,exe_time)
    results = mysql_ins.selectAll(sql)

    shop_ids = []
    upcs = []
    predict_sales = []
    for row in results:
        shop_id = row[0]
        upc = row[1]
        predict_sale = row[2]
        shop_ids.append(shop_id)
        upcs.append(upc)
        predict_sales.append(predict_sale)
    shop_upc_sales = {}
    for shop_id in list(set(shop_ids)):
        upc_sales = {}
        for shop_id1,upc,predict_sale in zip(shop_ids,upcs,predict_sales):
            if shop_id == shop_id1:
                upc_sales[upc] = predict_sale
        shop_upc_sales[shop_id] = upc_sales
    return shop_upc_sales
