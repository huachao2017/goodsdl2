"""
门店向二批订货  （1284 --> 1284）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import calu_stock
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.goodsdata import get_shop_order_goods
import time

order_shop_ids = config.shellgoods_params['order_shop_hour_ids']
shop_type = config.shellgoods_params['shop_types'][0]  # 门店
def generate():
    # create_date = str(time.strftime('%Y-%m-%d', time.localtime()))
    # create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    shop_upc_ordersales = []
    for shop_id in order_shop_ids:
        result = get_shop_order_goods(shop_id)
        if result == None or len(result) < 1:
            print ("shop_id  hour generate order failed ,get_data error   "+str(shop_id))
            return
        for mch_code  in result:
            drg_ins = result[mch_code]
            upc = drg_ins.upc
            upc_depth = drg_ins.depth
            shelf_depth = drg_ins.shelf_depth
            faces = drg_ins.face_num
            stock = drg_ins.stock
            min_stock,max_stock = calu_stock.get_stock(upc_depth,shelf_depth,faces)
            ordersales = max_stock - stock
            if ordersales > 0 :
                salesorder_ins = SalesOrder()
                salesorder_ins.shopid = shop_id
                salesorder_ins.upc = upc
                salesorder_ins.erp_shop_type = shop_type
                salesorder_ins.order_sale = ordersales
                salesorder_ins.max_stock = max_stock
                salesorder_ins.min_stock = min_stock
                salesorder_ins.stock = stock
                shop_upc_ordersales.append(salesorder_ins)
    if len(shop_upc_ordersales) > 0 :
        erp_interface.order_commit(shop_upc_ordersales)
        print("erp_interface.order_commit success!")




if __name__=='__main__':
    generate()