"""
二批向供货商非日配的首次订货  （1284 --> 好邻居）  非新店期
"""
from set_config import config
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.service.order_version_5.data_util import cacul_util
import traceback
import demjson
import math
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate(shop_id = None,order_type=None):
    try:
        print("二批向供货商非日配的首次订货,shop_id" + str(shop_id))
        if shop_id == None:
            return None
        sales_order_inss = []
        result = cacul_util.data_process(shop_id,shop_type)
        print ("规则0 商品数："+str(len(result.keys())))
        for mch_code  in result:
            drg_ins = result[mch_code]
            if drg_ins.delivery_type != 2:
                continue
            order_sale = 0
            if drg_ins.up_status == 1: # 新品
                # print ("规则1 ：psd 数量 与 最小最大陈列量 起订量")
                if drg_ins.psd_nums_4 > 0:
                    x = drg_ins.psd_nums_4 * 2.5  + drg_ins.min_disnums
                else:
                    x = 0
                y = min(drg_ins.max_disnums,drg_ins.min_disnums * 2 )
                order_sale = max(x,y,drg_ins.start_sum)
                if drg_ins.delivery_type == 2: #非日配
                    order_sale = order_sale - drg_ins.stock - drg_ins.sub_count
            else:
                safe_stock = max(drg_ins.min_disnums,math.ceil(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price), math.ceil(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price))
                track_stock =int(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price * 2.5) + safe_stock
                order_sale = track_stock - drg_ins.stock - drg_ins.supply_stock - drg_ins.sub_count
            if order_sale <= 0:
                continue
            # print ("规则2： 起订量规则")
            order_sale = order_rule.rule_start_num2(order_sale,drg_ins.start_sum)
            sales_order_ins = cacul_util.get_saleorder_ins(drg_ins, shop_id,shop_type)
            sales_order_ins.order_sale = order_sale
            sales_order_inss.append(sales_order_ins)
        sales_order_inss = order_rule.rule_filter_order_sale(sales_order_inss)
        # 起订价规则
        # sales_order_inss = order_rule.rule_start_price(sales_order_inss,shop_id)
        print("规则三：商品数：" + str(len(sales_order_inss)))
        return sales_order_inss,result
    except Exception as e:
        print ("not day sales2 order faield ,e ={}".format(e))
        traceback.print_exc()
        return None,None

if __name__=='__main__':
    generate(1284)