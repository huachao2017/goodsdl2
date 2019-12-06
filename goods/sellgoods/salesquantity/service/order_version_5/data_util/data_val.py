from set_config import config
import demjson
from goods.sellgoods.salesquantity.service.order_version_5.data_util import cacul_util
shop_type = config.shellgoods_params['shop_types'][1]  # 门店
from goods.sellgoods.salesquantity.service.order_version_5 import generate_order_2saler_add
import math
def generate(shop_id = None):
    print ("数据验证程序,shop_id"+str(shop_id))
    if shop_id == None:
        return None
    result = cacul_util.data_process(shop_id,shop_type)
    sales_order_inss = generate_order_2saler_add.generate(shop_id)
    print ("规则0 商品数："+str(len(result.keys())))
    print("订货数,门店id,门店名称,商品id,upc,商品名称,"
          "一级分类,二级分类,三级分类,face数,陈列规格,"
          "模板店4周预估psd,模板店4周预估psd金额,配送单位,最小陈列数,"
          "最大陈列数,门店库存,仓库库存,配送类型,保质期,"
          "起订量,在途订货数,进货价,商品单价,开店以来单天最大psd数量,"
          "最大陈列比例,4周实际销售psd数量,1周实际销售psd数量,是否是新品,安全天数")
    for mch_code  in result:
        drg_ins = result[mch_code]
        order_sale = 0
        for sales_order_ins in sales_order_inss:
            if drg_ins.upc == sales_order_ins.upc:
                order_sale = sales_order_ins.order_sale
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
               % ( str(order_sale),
                str(drg_ins.ucshop_id), str(drg_ins.shop_name), str(drg_ins.mch_code),
                str(drg_ins.upc),str(drg_ins.goods_name),
                str(drg_ins.category1_id),str(drg_ins.category2_id),str(drg_ins.category_id), str(drg_ins.face_num), str(drg_ins.package_type),
                str(drg_ins.psd_nums_4),str(drg_ins.psd_amount_4), str(drg_ins.start_sum),str(drg_ins.min_disnums),
                str(drg_ins.max_disnums),str(drg_ins.stock),str(drg_ins.supply_stock),str(drg_ins.delivery_type),str(drg_ins.storage_day),
                str(drg_ins.start_sum),str(drg_ins.sub_count),str(drg_ins.purchase_price),str(drg_ins.upc_price),str(math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price)),
                str(drg_ins.max_scale),str(float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)),str(float(drg_ins.upc_psd_amount_avg_1/drg_ins.upc_price)),str(drg_ins.up_status),str(drg_ins.safe_day_nums),
                       ))

if __name__=="__main__":
    generate(1284)