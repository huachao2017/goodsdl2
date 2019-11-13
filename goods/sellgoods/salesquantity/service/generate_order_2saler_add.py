"""
二批向供货商订货  （1284 --> 好邻居）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.local_util import combean_to_mybean
from goods.goodsdata import get_shop_order_goods
import math
order_shop_ids = config.shellgoods_params['order_shop_ids']
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate():
    for shop_id in order_shop_ids:
        result = get_shop_order_goods(shop_id,shop_type)
        sales_order_inss = []
        if result == None or len(result.keys()) < 1:
            print("shop_id day generate order failed ,get_data error   " + str(shop_id))
            return
        print ("规则0 商品数："+str(len(result.keys())))
        for mch_code  in result:
            drg_ins = result[mch_code]
            sales_order_ins = combean_to_mybean.get_saleorder_ins(drg_ins,shop_id,shop_type)

            if sales_order_ins.delivery_type is None or sales_order_ins.delivery_type != 1 or sales_order_ins.delivery_type != 2:
                print("%s delivery_type is error , goods_name=%s,upc=%s" % (
                str(sales_order_ins.delivery_type), str(sales_order_ins.goods_name), str(sales_order_ins.upc)))

            if sales_order_ins.sales_nums != None and sales_order_ins.sales_nums > 0 and sales_order_ins.sales_nums - sales_order_ins.stock-sales_order_ins.supply_stock > 0 and sales_order_ins.delivery_type == 2 :
                # 进入起订量规则
                if sales_order_ins.sales_nums <= sales_order_ins.start_sum:
                    sales_order_ins.order_sale = sales_order_ins.start_sum
                else:
                    max_order_sale = math.floor(
                        float((sales_order_ins.sales_nums / sales_order_ins.start_sum))) * sales_order_ins.start_sum
                    sales_order_ins.order_sale = max_order_sale
                sales_order_inss.append(sales_order_ins)
        print("规则1：商品数：" + str(len(sales_order_inss)))
        sales_order_inss = order_rule.rule_filter_order_sale(sales_order_inss)
        print("规则2：商品数：" + str(len(sales_order_inss)))

        print ("订货-补货，最终下单")
        print ("商品名称,订单数量,库存,近两周销量,起订量")
        for sales_order_ins  in sales_order_inss:
            print ("%s,%s,%s,%s,%s"
                   % (str(sales_order_ins.goods_name),
                      str(sales_order_ins.order_sale),str(sales_order_ins.stock),str(sales_order_ins.sales_nums),str(sales_order_ins.start_sum)))

        if len(sales_order_inss) > 0:
            erp_interface.order_commit(shop_id,shop_type,sales_order_inss)
            print("erp_interface.order_commit success!")

if __name__=='__main__':
    generate()