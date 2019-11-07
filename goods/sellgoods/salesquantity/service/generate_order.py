"""
二批向供货商订货  （1284 --> 好邻居）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import stock_util1
from goods.sellgoods.salesquantity.local_util import sales_util
from goods.sellgoods.salesquantity.service import out_service
from goods.sellgoods.salesquantity.local_util import save_mysql_sales
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.local_util import start_order_util
from goods.sellgoods.salesquantity.proxy import order_rule
import time
import datetime
order_shop_ids = config.shellgoods_params['order_shop_ids']
order_shop_isfirst = config.shellgoods_params['order_shop_idsfirst']
def generate(salves_ins=None,MeanEncoder=None):
    shop_upc_stock = stock_util1.get_stock(order_shop_ids)
    print ("shop_upc_stock")
    print (shop_upc_stock)
    shop_upc_sales = sales_util.get_predict_sales(order_shop_ids)
    print ("shop_upc_sales")
    print (shop_upc_sales)
    shop_upc_ordersales = {}
    for shop_id1 in shop_upc_stock:
        upc_stock = shop_upc_stock[shop_id1]
        upc_sales = {}
        if shop_id1 in list(shop_upc_sales.keys()):
            upc_sales = shop_upc_sales[shop_id1]
        if len(list(upc_sales.keys())) < 1:
            continue
        upc_ordersales = {}
        for upc in upc_stock:
            (min_stock,max_stock,stock) = upc_stock[upc]
            multiple,start_sum = start_order_util.start_order(shop_id1,upc)
            sale = None
            if upc in list(upc_sales.keys()):
                sale = upc_sales[upc]
            if min_stock is None:
                min_stock = 1
            if max_stock is None:
                max_stock =  3
            if stock is None or stock < 0:
                stock = 0
            if multiple is None:
                multiple = 1
            if start_sum is None:
                start_sum = 1

            if min_stock is not None and max_stock is not None and stock is not None:
                for (shop_id3,isfir) in order_shop_isfirst:
                    if shop_id3 == shop_id1:
                        # 首次订单规则
                        upc_ordersales = order_rule.rule_isAndNotFir(max_stock,min_stock,stock,upc_ordersales,upc,sale,multiple,start_sum,isfir=isfir)
        print ("规则一：商品数："+str(len(upc_ordersales.keys())))
        # 最小起订量规则 和 上限  下限规则
        upc_ordersales = order_rule.rule_start_sum(upc_ordersales)
        print("规则二：商品数：" + str(len(upc_ordersales.keys())))
        shop_upc_ordersales[int(shop_id1)] = upc_ordersales
    print ("shop_upc_ordersales:")
    print (shop_upc_ordersales)
    if len(list(shop_upc_ordersales.keys())) > 0:
        # 保存mysql 订单表
        save_mysql_sales.save_oreder(shop_upc_ordersales)
        # # 通知魔兽订单
        # erp_interface.order_commit()
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
def get_predict_sales(shop_ids,upcs,yes_time,day_sales,shop_upc_sales,salves_ins,MeanEncoder):
    predicts_info = out_service.get_nextday_sales(shop_ids,upcs,yes_time,day_sales,salves_ins,MeanEncoder)
    shop_ids = []
    data = []
    for predict_info in predicts_info:
        shop_id = predict_info['shop_id']
        upc = predict_info['upc']
        nextday_sale = predict_info['predict_day_sales'][0]
        if shop_id in list(shop_upc_sales.keys()):
            for shop_id1 in shop_upc_sales:
                upcs_sales1 =  shop_upc_sales[shop_id1]
                if shop_id == shop_id1:
                    if upc not in list(upcs_sales1):
                        upcs_sales1 [upc] = nextday_sale
                shop_upc_sales[shop_id1] = upcs_sales1
        else:
            shop_ids.append(shop_id)
            data.append((shop_id,upc,nextday_sale))

    if len(shop_ids) > 0 :
        for shop_id in list(set(shop_ids)):
            upc_sale = {}
            for (shop_id1,upc,nextday_sale) in data:
                if shop_id1 == shop_id:
                    if upc not in list(upc_sale.keys()):
                        upc_sale[upc] = nextday_sale
                    else:
                        sms  = upc_sale[upc]
                        upc_sale[upc] = sms+nextday_sale
            shop_upc_sales[shop_id] = upc_sale
    return shop_upc_sales

if __name__=='__main__':
    generate()