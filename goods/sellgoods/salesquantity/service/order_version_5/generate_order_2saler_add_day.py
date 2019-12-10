"""
二批向供货商日配订货  （1284 --> 好邻居）
"""
from set_config import config
import traceback
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.service.order_version_5.data_util import cacul_util
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate(shop_id = None):
    try:
        print("二批向供货商日配订货  ,shop_id" + str(shop_id))
        if shop_id == None:
            return None
        sales_order_inss = []
        result = cacul_util.data_process(shop_id, shop_type)
        print("规则0 商品数：" + str(len(result.keys())))
        for mch_code in result:
            drg_ins = result[mch_code]
            if drg_ins.delivery_type != 1:
                continue
            if drg_ins.safe_day_nums * drg_ins.old_sales / 7 - drg_ins.stock >= 0 :
                # print("规则1 ：max(安全天数内的销量，最小陈列量，起订量)")
                order_sale = max(max(drg_ins.safe_day_nums * drg_ins.old_sales / 7, drg_ins.min_disnums) - drg_ins.stock - drg_ins.sub_count,
                                 drg_ins.start_sum)
            else:
                order_sale = 0
            if order_sale <= 0:
                continue
            # print("规则2： 起订量规则")
            order_sale = order_rule.rule_start_num2(order_sale, drg_ins.start_sum)
            sales_order_ins = cacul_util.get_saleorder_ins(drg_ins, shop_id, shop_type)
            sales_order_ins.order_sale = order_sale
            sales_order_inss.append(sales_order_ins)
        sales_order_inss = order_rule.rule_filter_order_sale(sales_order_inss)
        print("规则三：商品数：" + str(len(sales_order_inss)))
        return sales_order_inss,result
    except Exception as e:
        print("day sales2 order faield ,e ={}".format(e))
        traceback.print_exc()
        return None,None



if __name__=='__main__':
    generate(1284)