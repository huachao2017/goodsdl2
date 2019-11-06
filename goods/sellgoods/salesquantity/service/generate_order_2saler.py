"""
二批向供货商订货  （1284 --> 好邻居）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.local_util import calu_stock
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.goodsdata import get_shop_order_goods
from goods.goodsdata import DataRawGoods
order_shop_idsfirst = config.shellgoods_params['order_shop_idsfirst']
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate():
    for (shop_id,isfirst) in order_shop_idsfirst:
        result = get_shop_order_goods(shop_id,shop_type)
        upc_ordersales = {}
        shop_upc_ordersales = []
        if result == None or len(result.keys()) < 1:
            print("shop_id day generate order failed ,get_data error   " + str(shop_id))
            return
        print ("规则0 商品数："+str(len(result.keys())))
        for mch_code  in result:
            drg_ins = result[mch_code]
            upc = drg_ins.upc
            upc_depth = drg_ins.depth
            shelf_depth = drg_ins.shelf_depth
            faces = drg_ins.face_num
            stock = drg_ins.stock
            multiple = drg_ins.multiple
            start_sum = drg_ins.start_sum
            sale = drg_ins.sales
            max_stock, min_stock = calu_stock.get_stock(upc_depth,shelf_depth,faces)
            if stock is None or stock < 0:
                stock = 0
            if multiple is None or multiple == 0:
                multiple = 1
            if start_sum is None or start_sum == 0:
                start_sum = 1
            upc_ordersales = order_rule.rule_isAndNotFir(max_stock, min_stock, stock, upc_ordersales, upc, sale,
                                                             multiple, start_sum, isfir=isfirst)
        print("规则一：商品数：" + str(len(upc_ordersales.keys())))
        upc_ordersales = order_rule.rule_start_sum(upc_ordersales)
        print("规则二：商品数：" + str(len(upc_ordersales.keys())))
        for upc in upc_ordersales :
            (order_sale, predict_sale, min_stock, max_stock, stock, multiple, start_sum, start_min, start_max) = upc_ordersales[upc]
            salesorder_ins = SalesOrder()
            salesorder_ins.shopid = shop_id
            salesorder_ins.upc = upc
            salesorder_ins.stock = stock
            salesorder_ins.min_stock = min_stock
            salesorder_ins.max_stock = max_stock
            salesorder_ins.order_sale = order_sale
            salesorder_ins.erp_shop_type = shop_type
            salesorder_ins.start_max = start_max
            salesorder_ins.start_min = start_min
            salesorder_ins.start_sum = start_sum
            salesorder_ins.multiple = multiple
            salesorder_ins.predict_sale = predict_sale
            shop_upc_ordersales.append(salesorder_ins)
        if len(shop_upc_ordersales) > 0:
            erp_interface.order_commit(shop_id,shop_type,shop_upc_ordersales)
            print("erp_interface.order_commit success!")


if __name__=='__main__':
    generate()