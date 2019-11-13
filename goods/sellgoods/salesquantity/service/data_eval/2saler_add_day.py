"""
二批向供货商订货  （1284 --> 好邻居）
"""
from set_config import config
from goods.sellgoods.salesquantity.local_util import erp_interface
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.local_util import combean_to_mybean
from goods.goodsdata_eval import get_shop_order_goods
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
        print ("获取 商品数："+str(len(result.keys())))
        print ("商品名称,条形码,配送类型,face数,商品深度,货架深度,陈列店内码,小仓库库存,起订量,步长,门店库存,历史销量,预测销量")
        for mch_code  in result:
            drg_ins = result[mch_code]
            print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"
                  % (str(drg_ins.goods_name),
                     str(drg_ins.upc),
                     str(drg_ins.delivery_type),
                     str(drg_ins.face_num),
                     str(drg_ins.depth),
                     str(drg_ins.shelf_depth),
                     str(drg_ins.mch_code),
                     str(drg_ins.supply_stock),
                     str(drg_ins.start_sum),
                     str(drg_ins.multiple),
                     str(drg_ins.stock),
                     str(drg_ins.sales_nums),
                     str(drg_ins.sales),
                    ))



if __name__=='__main__':
    generate()