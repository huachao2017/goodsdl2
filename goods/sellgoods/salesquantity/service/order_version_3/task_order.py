from goods.sellgoods.salesquantity.local_util import config_table_util
import datetime
from goods.sellgoods.salesquantity.service.order_version_3 import generate_order_2saler_first,generate_order_2saler_day_first,generate_order_2saler_add,generate_order_2saler_add_day,generate_order_shop

order_process_dict={
    1:generate_order_2saler_first,
    2:generate_order_2saler_day_first,
    3:generate_order_2saler_add,
    4:generate_order_2saler_add_day,
    5:generate_order_shop
}

def process():
    ct_ins = config_table_util.ConfigTableUtil()
    cshops_inss = ct_ins.select_all_configshops()
    exe_hour = datetime.datetime.now().hour
    exe_weekday = datetime.datetime.now().weekday() + 1
    if len(cshops_inss) > 0 :
        for shop_ins in cshops_inss:
            if exe_hour in shop_ins.hours_time and exe_weekday in shop_ins.weekdays_time:
                if shop_ins.order_type in list(order_process_dict.keys()):
                    order_process_dict[shop_ins.order_type].generate(shop_ins.shop_id)


if __name__=='__main__':
    process()