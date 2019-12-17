import django
import os
import main.import_django_settings
from django.db import connections
import demjson
def cal_order_nums1(batch_id,upc_set):
    """
    到货后更新选品表门店的订货次数
    :param batch_id: 订货的批次
    :param order_sale_dict: 订货单字典
    :return:
    """
    print("到货后，更新选品表订货次数")
    # 查询订货批次下的 ，仓库下门店选品 批次字典（demstore）
    sql1 = "select dsshopid_selectbatch,order_data from goods_batch_order where batch_order_id = {}"
    cursor_ai = connections['default'].cursor()
    cursor_ai.execute(sql1.format(batch_id))
    (dsshopid_selectbatch,order_data) = cursor_ai.fetchone()
    dsshopid_selectbatch = demjson.decode(dsshopid_selectbatch)
    order_data = demjson.decode(order_data)

    order_batch_set = []
    for order_d in list(order_data):
        order_d = dict(order_d)
        order_batch_set.append([order_d['upc']])
    order_batch_set = set(order_batch_set)
    sql2 = "update goods_goodsselectionhistory set order_number = order_number-1 where shopid = {} and batch_id = {} and upc = {}  "
    # 查询当前
    for ds_shopid in dsshopid_selectbatch:
        select_batchid = dsshopid_selectbatch[ds_shopid]
        for upc in order_batch_set:
            if upc not in upc_set:
                sql2 = sql2.format(ds_shopid, select_batchid, upc)
                print (sql2)
                cursor_ai.execute(sql2)
                cursor_ai.connection.commit()

def cal_order_nums2(shopid,select_batch_id,upc):
    sql1 = "update goods_goodsselectionhistory set order_number = order_number+1 where shopid = {} and batch_id = {} and upc = {}  "
    cursor_ai = connections['default'].cursor()
    cursor_ai.execute(sql1.format(shopid,select_batch_id,upc))
    cursor_ai.connection.commit()

