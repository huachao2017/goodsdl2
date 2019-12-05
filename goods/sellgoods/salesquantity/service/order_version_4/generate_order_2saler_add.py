"""
二批向供货商非日配订货  （1284 --> 好邻居）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.proxy import order_rule
import traceback
from goods.sellgoods.salesquantity.service.order_version_5.data_util import cacul_util
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate(shop_id = None):
    try:
        print("二批向供货商非日配订货  ,shop_id" + str(shop_id))
        sales_order_inss = []
        if shop_id == None:
            return None
        result = cacul_util.data_process(shop_id, shop_type)
        print("规则0 商品数：" + str(len(result.keys())))
        print("商品upc,商品名,最大陈列数,最小陈列数,门店库存,小仓库库存")
        for mch_code in result:
            drg_ins = result[mch_code]
            print("%s,%s,%s,%s,%s,%s" % (str(drg_ins.upc),
                                         str(drg_ins.goods_name),
                                         str(drg_ins.max_disnums),
                                         str(drg_ins.min_disnums),
                                         str(drg_ins.stock),
                                         str(drg_ins.supply_stock)
                                         ))
            if drg_ins.delivery_type != 2:
                continue
            if drg_ins.safe_day_nums * drg_ins.old_sales / 7 - drg_ins.stock - drg_ins.supply_stock - drg_ins.sub_count>= 0:
                # print("规则1 ：max(安全天数内的销量，最小陈列量，起订量)")
                order_sale = max(max(drg_ins.safe_day_nums * drg_ins.old_sales / 7, drg_ins.min_disnums) - drg_ins.stock - drg_ins.supply_stock - drg_ins.sub_count,
                                 drg_ins.start_sum)
            else:
                order_sale = 0
            if order_sale <= 0 :
                continue
            # print("规则2： 起订量规则")
            order_sale = order_rule.rule_start_num2(order_sale, drg_ins.start_sum)
            sales_order_ins = cacul_util.get_saleorder_ins(drg_ins, shop_id, shop_type)
            sales_order_ins.order_sale = order_sale
            sales_order_inss.append(sales_order_ins)
        sales_order_inss = order_rule.rule_filter_order_sale(sales_order_inss)
        # 起订价规则
        for sales_order_ins in sales_order_inss:
            print("%s , %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s" % (
                str(sales_order_ins.order_sale), str(sales_order_ins.upc), str(sales_order_ins.goods_name),
                str(sales_order_ins.max_stock), str(sales_order_ins.min_stock), str(sales_order_ins.stock),
                str(sales_order_ins.supply_stock), str(sales_order_ins.storage_day), str(sales_order_ins.delivery_type),
                str(sales_order_ins.mch_goods_code), str(sales_order_ins.sub_count),
                str(sales_order_ins.purchase_price)))
        # print ("起订价规则  ： len = "+str(len(sales_order_inss)))
        # sales_order_inss = order_rule.rule_start_price(sales_order_inss,shop_id)
        print("规则三：商品数：" + str(len(sales_order_inss)))
        print("订货量,商品upc,商品名,最大陈列数,最小陈列数,门店库存,小仓库库存,保质期,配送类型,商品编码")
        for sales_order_ins in sales_order_inss:
            print("%s , %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s" % (
                str(sales_order_ins.order_sale), str(sales_order_ins.upc), str(sales_order_ins.goods_name),
                str(sales_order_ins.max_stock), str(sales_order_ins.min_stock), str(sales_order_ins.stock),
                str(sales_order_ins.supply_stock), str(sales_order_ins.storage_day), str(sales_order_ins.delivery_type),
                str(sales_order_ins.mch_goods_code),str(sales_order_ins.sub_count),str(sales_order_ins.purchase_price)))
        return sales_order_inss
    except Exception as e:
        print("day sales2 order faield ,e ={}".format(e))
        traceback.print_exc()
        return None
if __name__=='__main__':
    generate(1284)