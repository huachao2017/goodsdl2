from set_config import config
from goods.sellgoods.salesquantity.local_util import stock_util
from goods.sellgoods.salesquantity.local_util import sales_util
from goods.sellgoods.salesquantity.service import out_service
from goods.sellgoods.salesquantity.local_util import save_mysql_sales
from goods.sellgoods.salesquantity.local_util import erp_interface
import time
import datetime
order_shop_ids = config.shellgoods_params['order_shop_ids']
def generate():
    shop_upc_stock = stock_util.get_stock(order_shop_ids)
    print ("shop_upc_stock")
    print (shop_upc_stock)
    shop_upc_sales = sales_util.get_predict_sales(order_shop_ids)
    print ("shop_upc_sales")
    print (shop_upc_sales)
    shop_ids, upcs, yes_time, day_sales = get_none_sales_features(shop_upc_stock,shop_upc_sales)
    if len(upcs)>0:
        shop_upc_sales = get_predict_sales(shop_ids, upcs, yes_time, day_sales,shop_upc_sales)
    shop_upc_ordersales = {}
    for shop_id1 in shop_upc_stock:
        upc_stock = shop_upc_stock[shop_id1]
        upc_sales = {}
        if shop_id1 in list(shop_upc_sales.keys()):
            upc_sales = shop_upc_sales[shop_id1]
        upc_ordersales = {}
        for upc in upc_stock:
            (min_stock,max_stock,stock) = upc_stock[upc]
            sale = upc_sales[upc]
            if min_stock is not None and max_stock is not None and stock is not None and sale is not None:
                if max_stock-stock > sale:
                    upc_ordersales[upc] = (sale,sale,min_stock,max_stock,stock)
                else:
                    upc_ordersales[upc] = (max_stock-stock,sale,min_stock,max_stock,stock)
        shop_upc_ordersales[int(shop_id1)] = upc_ordersales
    # 保存mysql 订单表
    save_mysql_sales.save_oreder(shop_upc_ordersales)
    # 通知魔兽订单
    erp_interface.order_commit()
    print ("erp_interface.order_commit success!")


def get_none_sales_features(shop_upc_stock,shop_upc_sales):
    # 没有销量的特征信息
    shop_ids = []
    upcs = []
    exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    yes_time = str(
        (datetime.datetime.strptime(exe_time, "%Y-%m-%d") + datetime.timedelta(days=-1)).strftime(
            "%Y-%m-%d"))
    day_sales = []
    for shop_id1 in shop_upc_stock:
        upc_stock = shop_upc_stock[shop_id1]
        upc_sales = {}
        if shop_id1 in list(shop_upc_sales.keys()):
            upc_sales = shop_upc_sales[shop_id1]
        for upc in upc_stock:
            sale = None
            if upc in list(upc_sales.keys()):
                sale = upc_sales[upc]
            if sale is None:
                # 送入预测模型预测销量
                shop_ids.append(shop_id1)
                upcs.append(upc)
                day_sales.append(0)
    return shop_ids,upcs,yes_time,day_sales
def get_predict_sales(shop_ids,upcs,yes_time,day_sales,shop_upc_sales):
    predicts_info = out_service.get_nextday_sales(shop_ids,upcs,yes_time,day_sales)
    for predict_info in predicts_info:
        shop_id = predict_info['shop_id']
        upc = predict_info['upc']
        nextday_sale = predict_info['predict_day_sales'][0]
        for shop_id1 in shop_upc_sales:
            upcs_sales1 =  shop_upc_sales[shop_id1]
            if shop_id == shop_id1:
                upcs_sales1 [upc] = nextday_sale
            shop_upc_sales[shop_id1] = upcs_sales1
    return shop_upc_sales

if __name__=='__main__':
    generate()