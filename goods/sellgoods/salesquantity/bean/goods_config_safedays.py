import time
class ConfigSafedayas:
    shop_id = None
    upc = None
    safe_day_nums = 1
    goods_name = None
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))