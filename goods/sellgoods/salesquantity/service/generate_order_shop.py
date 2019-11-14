"""
门店向二批订货  （1284 --> 1284）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import combean_to_mybean
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.goodsdata import get_shop_order_goods
order_shop_ids = config.shellgoods_params['order_shop_hour_ids']
shop_type = config.shellgoods_params['shop_types'][0]  # 门店
order_shop_hours = config.shellgoods_params['order_shop_hours']
def generate(shopid = None):
    if shopid != None:
        order_shop_ids = [shopid]
    # TODO 订货量 由库存计算改为用实际销售量计算
    for shop_id in order_shop_ids:
        result = get_shop_order_goods(shop_id,shop_type)
        if result == None or len(result.keys()) < 1:
            print ("shop_id  hour generate order failed ,get_data error   "+str(shop_id)+",shop_type:"+str(shop_type))
            return
        sales_order_inss = []
        for mch_code  in result:
            drg_ins = result[mch_code]
            sales_order_ins = combean_to_mybean.get_saleorder_ins(drg_ins,shop_id,shop_type)
            if  sales_order_ins.max_stock < 0 or sales_order_ins.stock < 0 :
                sales_order_ins.order_sale = 200000
            elif float(sales_order_ins.stock) <= float(2):
                sales_order_ins.order_sale = sales_order_ins.max_stock - sales_order_ins.stock
                print ("补货单..... upc=%s,name=%s,order_sale=%s,supply_stock=%s" % (str(sales_order_ins.upc),str(sales_order_ins.goods_name),str(sales_order_ins.order_sale),str(sales_order_ins.supply_stock)))
                if sales_order_ins.order_sale > sales_order_ins.supply_stock:
                    sales_order_ins.order_sale = sales_order_ins.supply_stock
            if sales_order_ins.order_sale > 0:
                sales_order_inss.append(sales_order_ins)
        if len(sales_order_inss) > 0:
            erp_interface.order_commit(shop_id, shop_type, sales_order_inss)
            print("erp_interface.order_commit success!")

if __name__=='__main__':
    generate()