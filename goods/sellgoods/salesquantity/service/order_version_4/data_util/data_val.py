from set_config import config
from goods.sellgoods.salesquantity.service.order_version_4.data_util import cacul_util
shop_type = config.shellgoods_params['shop_types'][0]  # 门店

def generate(shop_id = None):
    print ("数据验证程序,shop_id"+str(shop_id))
    if shop_id == None:
        return None
    result = cacul_util.data_process(shop_id,shop_type)
    print ("规则0 商品数："+str(len(result.keys())))
    print("upc,商品名称,门店库存,仓库库存,最小陈列量,最大陈列量")
    for mch_code  in result:
        drg_ins = result[mch_code]
        print("%s,%s,%s,%s,%s,%s" % (
            drg_ins.upc,
            drg_ins.goods_name,
            drg_ins.stock,
            drg_ins.supply_stock,
            drg_ins.min_disnums,
            drg_ins.max_disnums
        ))

if __name__=="__main__":
    generate(1284)