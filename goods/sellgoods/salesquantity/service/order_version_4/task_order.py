from goods.sellgoods.salesquantity.local_util import config_table_util
import datetime
from goods.sellgoods.salesquantity.service.order_version_3 import generate_order_2saler_first,generate_order_2saler_day_first,generate_order_2saler_add,generate_order_2saler_add_day,generate_order_shop
from goods.sellgoods.salesquantity.local_util import erp_interface
from set_config import config
shop_type = config.shellgoods_params['shop_types'][1]  # 二批
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
    shop_ids = []
    for shop_ins in cshops_inss:
        shop_ids.append(shop_ins.shop_id)
    shop_ids = list(set(shop_ids))

    if len(shop_ids) > 0 :
        for shop_id in shop_ids:
            sales_order_inss_all = []
            for shop_ins in cshops_inss:
                if shop_id == shop_ins.shop_id:
                    if exe_hour in shop_ins.hours_time and exe_weekday in shop_ins.weekdays_time:
                        if shop_ins.order_type in list(order_process_dict.keys()):
                            sales_order_inss = order_process_dict[shop_ins.order_type].generate(shop_ins.shop_id)
                            if sales_order_inss is not None and len(sales_order_inss)> 0 :
                                for sales_order_ins in sales_order_inss:
                                    sales_order_inss_all.append(sales_order_ins)
                else:
                    break
            if len(sales_order_inss_all) > 0:
                erp_interface.order_commit(shop_id, shop_type, sales_order_inss_all)
                print("erp_interface.order_commit success!")


if __name__=='__main__':
    process()