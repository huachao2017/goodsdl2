import  math
from goods.sellgoods.salesquantity.bean import taskflow
from set_config import config

def rule_filter_order_sale(sales_order_inss):
    """
    过滤 订货商品<=0 的规则
    :param sales_order_inss:
    :return:
    """
    sales_order_inss_new = []
    for sales_order_ins in sales_order_inss:
        if sales_order_ins.order_sale > 0 :
            sales_order_inss_new.append(sales_order_ins)
    return sales_order_inss_new

def rule_start_num2(order_sale,start_sum):
    """
    起订量规则
    :param order_sale:
    :param start_sum:
    :return:
    """
    if start_sum is None or start_sum == 0 :
        return 0
    if order_sale <= start_sum:
        order_sale = start_sum
    else:
        order_sale = math.ceil(
            float((order_sale/ start_sum))) * start_sum
    return order_sale

def rule_start_price(sales_order_inss,dmshop_id):
    """
    订货价规则， 配置到店 ， 该规则已废弃
    :param sales_order_inss:
    :param dmshop_id:
    :return:
    """
    sum_price = 0
    for sales_order_ins in sales_order_inss:
        sum_price += sales_order_ins.order_sale * sales_order_ins.purchase_price

    if dmshop_id in config.shellgoods_params["start_price"].keys() and sum_price < config.shellgoods_params["start_price"][dmshop_id]:
        return []
    else:
        return sales_order_inss

def rule_daydelivery_type(sales_order_inss):
    """
    单店 使用的  对日配品订货，超出可用空间的限制
    :param sales_order_inss:
    :return:
    """
    shelf_id_dict = {}
    V_goods_sum = 0
    for sales_order_ins in sales_order_inss:
        if sales_order_ins.delivery_type != 2: # 日配品
            shelf_inss = sales_order_ins.shelf_inss
            V_goods_sum += sales_order_ins.height * sales_order_ins.width * sales_order_ins.depth
            for shelf_ins in shelf_inss:
                shelf_id_dict[shelf_ins.shelf_id] = shelf_ins
    V_shelf_sum = 0
    for shelf_id in shelf_id_dict:
        shelf_ins = shelf_id_dict[shelf_id]
        V_shelf_sum += shelf_ins.shelf_length * shelf_ins.shelf_height * shelf_ins.shelf_depth

    if V_goods_sum > V_shelf_sum:
        sales_order_inss_new = []
        for sales_order_ins in sales_order_inss:
            if sales_order_ins.delivery_type == 2:  # 非日配配品
                sales_order_inss_new.append(sales_order_ins)
        return sales_order_inss_new
    else:
        return sales_order_inss



from functools import cmp_to_key
def many_sort(drg_ins1, drg_ins2):
    if int(drg_ins1.psd_nums_4) > int(drg_ins2.psd_nums_4):
        return 1
    elif int(drg_ins1.psd_nums_4) < int(drg_ins2.psd_nums_4):
        return -1
    else:
        V1 = drg_ins1.depth *  drg_ins1.width * drg_ins1.height
        V2 = drg_ins2.depth *  drg_ins2.width * drg_ins2.height
        if V1 > V2:
            return -1
        else:
            return 1

def bingql_filter(drg_inss):
    print ("")


def rule_bingql(drg_inss):
    bingql_drg_inss = []
    for drg_ins in drg_inss:
        if drg_ins.category2_id == 101:
            bingql_drg_inss.append(drg_ins)
    bingql_drg_inss.sort(key=cmp_to_key(many_sort))

    for bingql_drg_ins in bingql_drg_inss:
        print ("")



