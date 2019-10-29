from set_config import config
# 生成自动陈列
shelf_display = config.shellgoods_params['shelf_display']
def generate_displays(shopids_isfir=None):
    if shopids_isfir == None:
        for (shop_id,isfir) in shelf_display:
            shopids_isfir.append((shop_id,isfir))

    for (shop_id, isfir) in shelf_display:
        print (shop_id)
        


