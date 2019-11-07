from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.sellgoods.salesquantity.local_util import calu_stock
def get_saleorder_ins(drg_ins, shop_id,shop_type):
    upc = drg_ins.upc
    upc_depth = drg_ins.depth
    shelf_depth = drg_ins.shelf_depth
    faces = drg_ins.face_num
    stock = drg_ins.stock
    multiple = drg_ins.multiple
    start_sum = drg_ins.start_sum
    sale = drg_ins.sales
    max_stock, min_stock = calu_stock.get_stock(upc_depth, shelf_depth, faces)
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