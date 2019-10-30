from set_config import config
# 生成自动陈列
shelf_display = config.shellgoods_params['shelf_display']

def generate_displays(shopids_isfir=None):
    if shopids_isfir == None:
        shopids_isfir = shelf_display

    for (shop_id, isfir) in shelf_display:
        print (shop_id)
        # TODO 调用方法获取 门店内货架与商品信息
        shop = get_shop(shop_id,isfir)
        # 排列货架 生成陈列





def get_shop(shop_id,isfir=True):
    print ("do ............")