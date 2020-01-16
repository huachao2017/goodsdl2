import  math
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
    psd_nums_4_1 =max(drg_ins1.psd_nums_4,float(drg_ins1.upc_psd_amount_avg_4 / drg_ins1.upc_price))
    psd_nums_4_2 = max(drg_ins2.psd_nums_4, float(drg_ins2.upc_psd_amount_avg_4 / drg_ins2.upc_price))
    if int(psd_nums_4_1) > int(psd_nums_4_2):
        return 1
    elif int(psd_nums_4_1) < int(psd_nums_4_2):
        return -1
    else:
        V1 = drg_ins1.depth *  drg_ins1.width * drg_ins1.height
        V2 = drg_ins2.depth *  drg_ins2.width * drg_ins2.height
        if V1 > V2:
            return -1
        else:
            return 1

def bingql_filter(drg_inss,order_data_dict):
    """
    #  单库 单店， 可以这样遍历 drg_inss
    """
    V1 = 0 # 目标库存的总体积
    V2 = 0 # 货架的总体积
    shelf_id_dict={}
    for drg_ins in drg_inss:
        if drg_ins.category2_id == 124:
            key = str(drg_ins.mch_code)+","+str(drg_ins.upc)
            if key in order_data_dict.keys():
                order_sale = order_data_dict[key]
            else:
                order_sale = 0
            shelf_inss = drg_ins.shelf_inss
            save_goods_days = 0
            if drg_ins.dmstoreshop_id in config.shellgoods_params['save_goods_days'].keys():
                save_goods_days =  config.shellgoods_params['save_goods_days'][drg_ins.dmstoreshop_id]
            else:
                save_goods_days = config.shellgoods_params['save_goods_days'][-8888]
            V1 += drg_ins.height * drg_ins.width * drg_ins.depth * math.ceil(order_sale+drg_ins.sub_count - save_goods_days * float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price))
            for shelf_ins in shelf_inss:
                shelf_id_dict[str(shelf_ins.shelf_id) +"," +str(shelf_ins.goods_level_id)] = shelf_ins
    for shelf_level_id in shelf_id_dict:
        shelf_ins = shelf_id_dict[shelf_level_id]
        V2 += shelf_ins.level_width * shelf_ins.level_height * shelf_ins.level_depth
    if V1 <= V2*0.8:
        return True
    else:
        return False

def many_sort_daydelivery(drg_ins1, drg_ins2):
    ranking_1 = drg_ins1.ranking
    ranking_2 = drg_ins2.ranking
    if int(ranking_1) > int(ranking_2):
        return 1
    elif int(ranking_1) < int(ranking_2):
        return -1
    else:
        V1 = drg_ins1.depth *  drg_ins1.width * drg_ins1.height
        V2 = drg_ins2.depth *  drg_ins2.width * drg_ins2.height
        if V1 > V2:
            return -1
        else:
            return 1

def daydelivery_filter(drg_inss,order_data_dict):
    """
    #  单库 单店， 可以这样遍历 drg_inss  不是单库单店  时 ， 如果每个店的货架id 不同也没问题
    """
    V1 = 0 # 目标库存的总体积
    V2 = 0 # 货架的总体积
    shelf_id_dict={}
    for drg_ins in drg_inss:
        if drg_ins.delivery_type == 1:
            key = str(drg_ins.mch_code)+","+str(drg_ins.upc)
            if key in order_data_dict.keys():
                order_sale = order_data_dict[key]
            else:
                order_sale = 0
            shelf_inss = drg_ins.shelf_inss
            V1 += drg_ins.height * drg_ins.width * drg_ins.depth * math.ceil(order_sale+drg_ins.stock - 1* float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price))
            for shelf_ins in shelf_inss:
                shelf_id_dict[str(shelf_ins.shelf_id) +"," +str(shelf_ins.goods_level_id)] = shelf_ins
    for shelf_level_id in shelf_id_dict:
        shelf_ins = shelf_id_dict[shelf_level_id]
        V2 += shelf_ins.level_width * shelf_ins.level_height * shelf_ins.level_depth
    if V1 <= V2*0.8:
        return True
    else:
        return False




def rule_bingql(drg_inss,order_data_dict):
    flag = bingql_filter(drg_inss,order_data_dict)
    if flag:
        return order_data_dict
    bingql_drg_inss = []
    for drg_ins in drg_inss:
        if drg_ins.category2_id == 124 and drg_ins.upc_status_type == 2:
            bingql_drg_inss.append(drg_ins)
    bingql_drg_inss.sort(key=cmp_to_key(many_sort))
    # 不减品的 减少起订量
    for bingql_drg_ins in bingql_drg_inss:
        key = str(bingql_drg_ins.mch_code) + "," + str(bingql_drg_ins.upc)
        if key in order_data_dict.keys():
            order_sale = order_data_dict[key]
        else:
            order_sale = 0
        order_sale = order_sale + bingql_drg_ins.stock + bingql_drg_ins.supply_stock + bingql_drg_ins.sub_count
        while order_sale > 2*bingql_drg_ins.start_sum:
            order_data_dict[key] = order_sale - bingql_drg_ins.start_sum - (bingql_drg_ins.stock + bingql_drg_ins.supply_stock + bingql_drg_ins.sub_count)
            order_sale = order_sale - bingql_drg_ins.start_sum
            print ("bing qi lin rule , 不减品的 ,该品减少了一倍的起订量="+str(bingql_drg_ins.goods_name))
            if bingql_filter(drg_inss,order_data_dict):
                return order_data_dict
    # 减品的减少起订量
    for bingql_drg_ins in bingql_drg_inss:
        key = str(bingql_drg_ins.mch_code) + "," + str(bingql_drg_ins.upc)
        if key in order_data_dict.keys():
            order_sale = order_data_dict[key]
        else:
            order_sale = 0
        order_sale = order_sale + bingql_drg_ins.stock + bingql_drg_ins.supply_stock + bingql_drg_ins.sub_count
        while order_sale > 0:
            order_data_dict[key] = order_sale - bingql_drg_ins.start_sum - (
                        bingql_drg_ins.stock + bingql_drg_ins.supply_stock + bingql_drg_ins.sub_count)
            order_sale = order_sale - bingql_drg_ins.start_sum
            print("bing qi lin rule , 减品的 ,该品减少了一倍的起订量=" + str(bingql_drg_ins.goods_name))
            if bingql_filter(drg_inss, order_data_dict):
                return order_data_dict
    return order_data_dict




def rule_daydelivery_type2(drg_inss,order_data_dict):
    """
    version 8  20200115
    单店 使用的  对日配品订货，超出可用空间的限制   参考 https://shimo.im/docs/D8pYpwpT66RQ6vYD/read
    :param sales_order_inss:
    :return:
    """
    flag = daydelivery_filter(drg_inss,order_data_dict)
    if flag:
        return order_data_dict
    dayd_drg_inss = []
    for drg_ins in drg_inss:
        if drg_ins.delivery_type == 1:
            dayd_drg_inss.append(drg_ins)
    dayd_drg_inss.sort(key=cmp_to_key(many_sort))
    # 不减品的 减少起订量
    for dayd_drg_ins in dayd_drg_inss:
        key = str(dayd_drg_ins.mch_code) + "," + str(dayd_drg_ins.upc)
        if key in order_data_dict.keys():
            order_sale = order_data_dict[key]
        else:
            order_sale = 0
        order_sale = order_sale + dayd_drg_ins.stock + dayd_drg_ins.supply_stock + dayd_drg_ins.sub_count
        while order_sale > 2*dayd_drg_ins.start_sum:
            order_data_dict[key] = order_sale - dayd_drg_ins.start_sum -  (dayd_drg_ins.stock + dayd_drg_ins.supply_stock + dayd_drg_ins.sub_count)
            order_sale = order_sale - dayd_drg_ins.start_sum
            print ("rule_daydelivery_type2 rule , 不减品的 ,该品减少了一倍的起订量="+str(dayd_drg_ins.goods_name))
            if daydelivery_filter(drg_inss,order_data_dict):
                return order_data_dict
    # 减品的减少起订量
    for dayd_drg_ins in dayd_drg_inss:
        key = str(dayd_drg_ins.mch_code) + "," + str(dayd_drg_ins.upc)
        if key in order_data_dict.keys():
            order_sale = order_data_dict[key]
        else:
            order_sale = 0
        order_sale = order_sale + dayd_drg_ins.stock + dayd_drg_ins.supply_stock + dayd_drg_ins.sub_count
        while order_sale > 0:
            order_data_dict[key] = order_sale - dayd_drg_ins.start_sum - (
                    dayd_drg_ins.stock + dayd_drg_ins.supply_stock + dayd_drg_ins.sub_count)
            order_sale = order_sale - dayd_drg_ins.start_sum
            print("rule_daydelivery_type2 rule , 减品的 ,该品减少了一倍的起订量=" + str(dayd_drg_ins.goods_name))
            if daydelivery_filter(drg_inss, order_data_dict):
                return order_data_dict
    return order_data_dict
