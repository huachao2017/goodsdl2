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
        sales_order_inss = []
        if result == None or len(result.keys()) < 1:
            print("shop_id day generate order failed ,get_data error   " + str(shop_id))
            return
        print ("规则0 商品数："+str(len(result.keys())))
        for mch_code  in result:
            drg_ins = result[mch_code]
            sales_order_ins = get_saleorder_ins(drg_ins,shop_id)
            sales_order_ins = order_rule.rule_isAndNotFir(sales_order_ins ,isfir=isfirst)
            if sales_order_ins != None:
                sales_order_inss.append(sales_order_ins)
        print("规则一：商品数：" + str(len(upc_ordersales.keys())))
        upc_ordersales = order_rule.rule_start_sum(upc_ordersales)
        print("规则二：商品数：" + str(len(upc_ordersales.keys())))
        if len(sales_order_inss) > 0:
            erp_interface.order_commit(shop_id,shop_type,sales_order_inss)
            print("erp_interface.order_commit success!")

def get_saleorder_ins(drg_ins,shop_id):
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
    sales_order_ins = SalesOrder()
    sales_order_ins.shopid = shop_id
    sales_order_ins.start_max = max_stock  # 上限
    sales_order_ins.start_min = max(int(max_stock / 2), min_stock)  # 下限
    sales_order_ins.upc = upc
    sales_order_ins.predict_sale = sale
    sales_order_ins.erp_shop_type = shop_type
    sales_order_ins.order_sale = 0
    sales_order_ins.max_stock = max_stock
    sales_order_ins.min_stock = min_stock
    sales_order_ins.stock = stock
    return sales_order_ins
if __name__=='__main__':
    generate()