"""
二批向供货商非日配的首次订货  （1284 --> 好邻居）  非新店期
"""
from set_config import config
from goods.sellgoods.salesquantity.proxy import order_rule
from goods.sellgoods.salesquantity.service.order_version_6.data_util import cacul_util
import traceback
import time
import datetime
import demjson
import math
# shop_type = config.shellgoods_params['shop_types'][1]  # 二批
def generate(shop_id = None):
    try:
        print("二批向供货商非日配的首次订货,shop_id" + str(shop_id))
        if shop_id == None:
            return None
        if shop_id in config.shellgoods_params['save_goods_days'].keys():
            bhuo_days = config.shellgoods_params['save_goods_days'][shop_id]
        else:
            bhuo_days = config.shellgoods_params['save_goods_days'][-8888]

        if shop_id in config.shellgoods_params['get_goods_days'].keys():
            gethuo_days = config.shellgoods_params['get_goods_days'][shop_id]
        else:
            gethuo_days = config.shellgoods_params['get_goods_days'][-8888]
        result = cacul_util.data_process(shop_id)
        print ("规则0 商品数："+str(len(result.keys())))
        goods_orders=[]
        for mch_code  in result:
            drg_ins = result[mch_code]
            order_sale = 0
            if drg_ins.delivery_type == 2:
                if drg_ins.upc_status_type == 0:# 首次订货
                    if drg_ins.psd_nums_4 > 0:
                        x = drg_ins.psd_nums_4 * bhuo_days + drg_ins.min_disnums
                    else:
                        x = 0
                    y = min(drg_ins.max_disnums, drg_ins.min_disnums * 2)
                    order_sale = max(x, y, drg_ins.start_sum)
                elif drg_ins.upc_status_type == 1: # 新品
                    if drg_ins.psd_nums_4 > 0:
                        x = drg_ins.psd_nums_4 * bhuo_days + drg_ins.min_disnums
                    else:
                        x = 0
                    y = min(drg_ins.max_disnums, drg_ins.min_disnums * 2)
                    a = max(x, y, drg_ins.start_sum)
                    if math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price) < a:
                        order_sale = a
                    else:
                        order_sale = math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price) + drg_ins.min_disnums
                else:
                    safe_stock = max(drg_ins.min_disnums,math.ceil(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price), math.ceil(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price))
                    track_stock =drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price * bhuo_days + safe_stock
                    order_sale =  math.ceil(track_stock)
                    # order_sale = track_stock - drg_ins.stock - drg_ins.supply_stock - drg_ins.sub_count
            else: # 日配订货
                # 日配类型 改变商品的最小陈列量
                if drg_ins.storage_day < 15:
                    drg_ins.min_disnums = 1
                else:
                    drg_ins.min_disnums = 2
                # 判断该品是否为新品  TODO 设置为新品期
                # drg_ins.upc_status_type = 1
                # 如果是新品， 订货规则
                if drg_ins.upc_status_type ==1 or drg_ins.upc_status_type ==0 :
                    psd_nums_2 = 2
                    if drg_ins.psd_nums_2 != 0:
                        psd_nums_2 = drg_ins.psd_nums_2
                    if drg_ins.psd_nums_2 == 0 and drg_ins.psd_nums_2_cls != 0:
                        psd_nums_2 = drg_ins.psd_nums_2_cls
                    end_safe_stock = drg_ins.min_disnums
                    safe_day = 0
                    if drg_ins.storage_day <= 2:
                        safe_day = drg_ins.storage_day
                    else:
                        safe_day = bhuo_days
                    track_stock = end_safe_stock + safe_day * psd_nums_2
                    order_sale =  math.ceil(track_stock)
                else:
                    # TODO  商品的psd*保质期＜1，则该商品建议剔除选品，不订货    目前psd 取不到真实值， 这段逻辑先不走
                    # if drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price * drg_ins.storage_day < 1:
                    #     continue
                    end_safe_stock = drg_ins.min_disnums
                    end_date = str(time.strftime('%Y%m%d', time.localtime()))
                    # 到货日
                    order_get_date = str(
                        (datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(
                            days=gethuo_days)).strftime("%Y%m%d"))
                    order_get_week_i = datetime.datetime.strptime(order_get_date, "%Y%m%d").weekday() + 1
                    one_day_psd = 0
                    if order_get_week_i>=1 and order_get_week_i<=5:
                        one_day_psd = float(drg_ins.upc_psd_amount_avg_1_5 / drg_ins.upc_price)
                    else:
                        one_day_psd = float(drg_ins.upc_psd_amount_avg_6_7 / drg_ins.upc_price)
                    loss_oneday_nums =  drg_ins.loss_avg * one_day_psd / (1- drg_ins.loss_avg)
                    fudong_nums = 0
                    # #  浮动量 这块去掉
                    if drg_ins.loss_avg_amount <=0:
                        fudong_nums = 0-drg_ins.loss_avg_nums
                    else:
                        if loss_oneday_nums > 1:
                            fudong_nums = -1
                        if loss_oneday_nums <= 0:
                            fudong_nums = 1
                    end_date1 = str(time.strftime('%Y-%m-%d', time.localtime()))
                    time1 = time.mktime(time.strptime(drg_ins.shelf_up_date, '%Y-%m-%d'))
                    time2 = time.mktime(time.strptime(end_date1, '%Y-%m-%d'))
                    days = int((time2 - time1) / (24 * 60 * 60))
                    if days <=7:
                        fudong_nums = 0
                    safe_day = 0
                    if drg_ins.storage_day < 2:
                        safe_day = drg_ins.storage_day
                    else:
                        safe_day = bhuo_days
                    track_stock = safe_day * one_day_psd + fudong_nums + end_safe_stock
                    order_sale = math.ceil(track_stock)
            drg_ins.order_sale = order_sale
            goods_orders.append(drg_ins)
        return goods_orders
    except Exception as e:
        print ("not day sales2 order faield ,e ={}".format(e))
        traceback.print_exc()
        return None

if __name__=='__main__':
    generate(1284)