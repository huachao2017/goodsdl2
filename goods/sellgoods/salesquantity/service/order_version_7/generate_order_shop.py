"""
门店向二批补货  （1284 --> 1284）
"""
from set_config import config
import traceback
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.service.order_version_7.data_util import cacul_util
import math
shop_type = config.shellgoods_params['shop_types'][0]  # 门店
yinliao_cat_ids = config.shellgoods_params['yinliao_cat_ids'] # 饮料台账分类
def generate(shop_id = None):
    try:
        sales_order_inss = []
        print ("门店向二批补货,shop_id"+str(shop_id))
        if shop_id == None:
            return None
        result = cacul_util.data_process(shop_id,add_type=True)
        print ("规则0 商品数："+str(len(result.keys())))
        for mch_code  in result:
            drg_ins = result[mch_code]
            if drg_ins.delivery_type==2:
                drg_ins.safe_stock = max(drg_ins.min_disnums, drg_ins.upc_psd_nums_avg_4,
                                             drg_ins.upc_psd_nums_avg_1)
            else:
                if drg_ins.storage_day < 15:
                    min_disnums = 1
                else:
                    min_disnums = 2
                drg_ins.safe_stock = min_disnums
            if (drg_ins.delivery_type==2 and max(0,drg_ins.stock) < drg_ins.max_disnums and drg_ins.category_id in yinliao_cat_ids)  or (drg_ins.delivery_type==2 and max(0,drg_ins.stock) <= drg_ins.min_disnums and drg_ins.category_id not in yinliao_cat_ids) or (drg_ins.delivery_type==1 and drg_ins.supply_stock > 0 ):
                # 非日配
                if drg_ins.delivery_type == 2:
                    order_sale = min(drg_ins.max_disnums-max(0,drg_ins.stock),max(0,drg_ins.supply_stock))
                else:
                    order_sale = drg_ins.supply_stock
                order_sale = order_sale
                if order_sale <= 0:
                    continue
                sales_order_ins = cacul_util.get_saleorder_ins(drg_ins, shop_id,shop_type)
                sales_order_ins.order_sale = order_sale
                sales_order_inss.append(sales_order_ins)
        sales_order_inss = order_rule.rule_filter_order_sale(sales_order_inss)
        print("规则三：商品数：" + str(len(sales_order_inss)))
        return sales_order_inss,result
    except Exception as e:
        print("add order failed  e = {}".format(e))
        traceback.print_exc()
        return None,None
if __name__=='__main__':
    generate(1284)