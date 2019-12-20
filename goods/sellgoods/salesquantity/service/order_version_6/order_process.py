import os
import django
import main.import_django_settings
from django.db import connections
import time
from goods.sellgoods.salesquantity.bean import taskflow
from goods.sellgoods.salesquantity.service.order_version_6 import generate_order_2saler_add,generate_order_shop
from goods.sellgoods.salesquantity.service.order_version_6.data_util import cacul_util
from goods.sellgoods.salesquantity.local_util import erp_interface
from set_config import config
import datetime
import traceback
sql_workflow = "select id,batch_id,uc_shopid,erp_warehouse_id from goods_allworkflowbatch where type = {} and order_goods_status=1"
update_sql_01 = "update goods_allworkflowbatch set order_goods_status=2 where id={}"  # 2是正在计算、3是计算结束
update_sql_02 = "update goods_allworkflowbatch set order_goods_status={},order_goods_calculate_time={} where id={}"  # 2是正在计算、3是计算结束
insert_goods_batch_order = "insert into goods_batch_order (batch_order_id,order_data,create_time,update_time,order_all_data) values (%s,%s,%s,%s,%s)"
select_goods_batch_order = "select id,batch_order_id order_data from goods_batch_order where batch_order_id='{}'"
update_goods_batch_order = "update goods_batch_order set order_data = '{}',update_time='{}',order_all_data='{}' where id = {}"
sql_uc_shop = "select mch_shop_code from uc_shop where id = {}"

sql_dmshop = "select shop_id from erp_shop_related where erp_shop_id = {} and erp_shop_type = 1"
# 订货单
def day_order_process():
    conn = connections['default']
    conn_ucenter = connections['ucenter']
    conn_dmstore = connections['dmstore']
    ucenter_cursor = conn_ucenter.cursor()
    cursor_ai = conn.cursor()
    cursor_dmstore = conn_dmstore.cursor()
    # 获取日常订单
    cursor_ai.execute(sql_workflow.format(taskflow.day_order_type))
    first_flow_data = cursor_ai.fetchall()
    if first_flow_data is not None:
        for data in first_flow_data:
            try:
                id = data[0]
                batch_id = data[1]
                erp_warehouse_id = data[3]
                cursor_dmstore.execute(sql_dmshop.format(int(erp_warehouse_id)))
                dmstore_shopids = ucenter_cursor.fetchall()
                if dmstore_shopids is not None and len(dmstore_shopids) > 0 :
                    cursor_ai.execute(update_sql_01.format(id))  # 更新到“正在计算”
                    cursor_ai.connection.commit()
                    start_time = time.time()
                    print("日常订单 batch_id =" + str(batch_id))
                    goods_orders_all = []
                    for dmstore_shopid in dmstore_shopids:
                        dmstore_shopid = int (dmstore_shopid)
                        goods_orders = generate_order_2saler_add.generate(dmstore_shopid)
                        if goods_orders is None:
                            print ("下订单时，仓库下单失败 erp_warehouse_id = {}， 存在一个店 下单失败 dmstore_shopid={}".format(erp_warehouse_id,dmstore_shopid))
                            cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, int(time.time() - start_time),
                                                                   id))  # 更新到“结束计算”和耗时多少
                            cursor_ai.connection.commit()
                            return
                        else:
                            # 把结果转成json , 存入数据库
                            for drg_ins in goods_orders:
                                goods_orders_all.append(drg_ins)
                    print ("非日配 和 日配 订单所有店 所有商品数 ："+str(len(goods_orders_all)))
                    cursor_ai.execute(select_goods_batch_order.format(batch_id))
                    goods_batch_data = cursor_ai.fetchone()
                    if goods_batch_data is None:
                        inert_data = cacul_util.get_goods_batch_order_data_warhouse(batch_id,goods_orders_all)
                        cursor_ai.executemany(insert_goods_batch_order, inert_data)
                        cursor_ai.connection.commit()
                    else:
                        update_data = cacul_util.get_goods_batch_order_data_warhouse(batch_id,goods_batch_data)
                        cursor_ai.execute(update_goods_batch_order.format(update_data[0][1], update_data[0][3],update_data[0][4],goods_batch_data[0]))
                        cursor_ai.connection.commit()
                    # 更新数据库状态
                    cursor_ai.execute(
                        update_sql_02.format(taskflow.cal_status_end, int(time.time() - start_time), data[0]))
                    cursor_ai.connection.commit()
            except Exception as e:
                print ("data is error data="+str(data))
                traceback.print_exc()
                cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, 0,
                                                       data[0]))  # 更新到“结束计算”和耗时多少
                cursor_ai.connection.commit()

    conn.close()
    conn_ucenter.close()


# 补货单
def add_order_process():
    conn = connections['default']
    conn_ucenter = connections['ucenter']
    ucenter_cursor = conn_ucenter.cursor()
    cursor_ai = conn.cursor()
    # 获取日常订单
    cursor_ai.execute(sql_workflow.format(taskflow.add_order_type))
    add_flow_data = cursor_ai.fetchall()
    if add_flow_data is not None:
        for data in add_flow_data:
            try:
                id = data[0]
                batch_id = data[1]
                uc_shop_id = data[2]
                ucenter_cursor.execute(sql_uc_shop.format(int(uc_shop_id)))
                (dmstore_shopid,) = ucenter_cursor.fetchone()
                cursor_ai.execute(update_sql_01.format(id))  # 更新到“正在计算”
                conn.commit()
                start_time = time.time()
                print("补货单 batch_id =" + str(batch_id))
                dmstore_shopid = int(dmstore_shopid)
                sales_order_inss,result = generate_order_shop.generate(dmstore_shopid)
                if sales_order_inss is None:
                    cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, int(time.time() - start_time),
                                                        id))  # 更新到“结束计算”和耗时多少
                    cursor_ai.connection.commit()
                else:
                    # 把结果转成json , 存入数据库
                    print("补货 订单商品数 ：" + str(len(sales_order_inss)))
                    cursor_ai.execute(select_goods_batch_order.format(batch_id))
                    goods_batch_data = cursor_ai.fetchone()
                    if goods_batch_data is None:
                        inert_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,result)
                        cursor_ai.executemany(insert_goods_batch_order, inert_data)
                        cursor_ai.connection.commit()
                    else:
                        update_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,result)
                        cursor_ai.execute(update_goods_batch_order.format(update_data[0][1],update_data[0][3],update_data[0][4],goods_batch_data[0]))
                        cursor_ai.connection.commit()
                    # 更新数据库状态
                    cursor_ai.execute(
                        update_sql_02.format(taskflow.cal_status_end, int(time.time() - start_time), id))
                    cursor_ai.connection.commit()
                    # 把订单结果和批次结果 通知给摩售
                    shop_type = config.shellgoods_params['shop_types'][0]  # 门店
                    erp_interface.order_commit(dmstore_shopid,shop_type,sales_order_inss,batch_id=batch_id)
            except Exception as e:
                cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, 0,
                                                       data[0]))  # 更新到“结束计算”和耗时多少
                cursor_ai.connection.commit()
                print ("data is error!" +str(data))
                traceback.print_exc()
    conn.close()
    conn_ucenter.close()