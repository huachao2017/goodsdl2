import time
import datetime
class ConfigDisnums:
    shop_id = None
    shelf_id = None
    shelf_type = None
    shelf_depth = None
    upc=None
    goods_name=None
    goods_depth=None
    single_face_min_disnums=0
    single_face_max_disnums=1
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
