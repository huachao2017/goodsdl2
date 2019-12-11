import os
import django
import main.import_django_settings
from django.db import connections
import time
from goods.sellgoods.salesquantity.bean import taskflow
from goods.sellgoods.salesquantity.service.order_version_5 import generate_order_2saler_first,generate_order_2saler_add,generate_order_2saler_add_day,generate_order_shop,generate_order_2saler_newshop_notday
from goods.sellgoods.salesquantity.service.order_version_5.data_util import cacul_util
from goods.sellgoods.salesquantity.local_util import erp_interface
from set_config import config
import datetime
import traceback
sql_workflow = "select id,batch_id,uc_shopid from goods_allworkflowbatch where type = {} and order_goods_status=1"
update_sql_01 = "update goods_allworkflowbatch set order_goods_status=2 where id={}"  # 2是正在计算、3是计算结束
update_sql_02 = "update goods_allworkflowbatch set order_goods_status={},order_goods_calculate_time={} where id={}"  # 2是正在计算、3是计算结束
insert_goods_batch_order = "insert into goods_batch_order (batch_order_id,order_data,create_time,update_time,uc_shop_id,order_all_data) values (%s,%s,%s,%s,%s,%s)"
select_goods_batch_order = "select id,batch_order_id order_data from goods_batch_order where batch_order_id='{}' and uc_shop_id = {} "
update_goods_batch_order = "update goods_batch_order set order_data = '{}',update_time='{}',order_all_data='{}' where id = {}"
sql_uc_shop = "select mch_shop_code from uc_shop where id = {}"
# 首次订货单
def first_order_process():
    conn = connections['default']
    conn_ucenter = connections['ucenter']
    ucenter_cursor = conn_ucenter.cursor()
    cursor_ai = conn.cursor()
    # 获取首次订单
    cursor_ai.execute(sql_workflow.format(taskflow.first_order_type))
    first_flow_data = cursor_ai.fetchall()
    if first_flow_data is not None:
        for data in first_flow_data:
            try:
                id = data[0]
                batch_id = data[1]
                uc_shop_id = data[2]
                ucenter_cursor.execute(sql_uc_shop.format(int(uc_shop_id)))
                (dmstore_shopid,) = ucenter_cursor.fetchone()
                cursor_ai.execute(update_sql_01.format(id))  # 更新到“正在计算”
                cursor_ai.connection.commit()
                start_time = time.time()
                print("首次订单 batch_id =" + str(batch_id))
                dmstore_shopid = int(dmstore_shopid)
                sales_order_inss,result = generate_order_2saler_first.generate(dmstore_shopid)
                if sales_order_inss is None:
                    cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, int(time.time() - start_time),
                                                           id))  # 更新到“结束计算”和耗时多少
                    cursor_ai.connection.commit()
                else:
                    # 把结果转成json , 存入数据库
                    print("首次 订单商品数 ：" + str(len(sales_order_inss)))
                    cursor_ai.execute(select_goods_batch_order.format(batch_id,uc_shop_id))
                    goods_batch_data = cursor_ai.fetchone()
                    if goods_batch_data is None:
                        inert_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result)
                        cursor_ai.executemany(insert_goods_batch_order, inert_data)
                        cursor_ai.connection.commit()
                    else:
                        update_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,result)
                        cursor_ai.execute(update_goods_batch_order.format(update_data[0][1], update_data[0][3],update_data[0][5],goods_batch_data[0]))
                        cursor_ai.connection.commit()
                    # 更新数据库状态
                    cursor_ai.execute(
                        update_sql_02.format(taskflow.cal_status_end, int(time.time() - start_time), data[0]))
                    cursor_ai.connection.commit()
            except Exception as e:
                print ("process error , data="+str(data))
                traceback.print_exc()
                cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, 0,
                                                       data[0]))  # 更新到“结束计算”和耗时多少
                cursor_ai.connection.commit()
    conn.close()
    conn_ucenter.close()

# 日常订单
def day_order_process():
    conn = connections['default']
    conn_ucenter = connections['ucenter']
    ucenter_cursor = conn_ucenter.cursor()
    cursor_ai = conn.cursor()
    # 获取日常订单
    cursor_ai.execute(sql_workflow.format(taskflow.day_order_type))
    first_flow_data = cursor_ai.fetchall()
    if first_flow_data is not None:
        for data in first_flow_data:
            try:
                id = data[0]
                batch_id = data[1]
                uc_shop_id = data[2]
                ucenter_cursor.execute(sql_uc_shop.format(int(uc_shop_id)))
                (dmstore_shopid,) = ucenter_cursor.fetchone()
                cursor_ai.execute(update_sql_01.format(id))  # 更新到“正在计算”
                cursor_ai.connection.commit()
                start_time = time.time()
                end_date = str(time.strftime('%Y%m%d', time.localtime()))
                start_date = str(
                    (datetime.datetime.strptime(end_date, "%Y%m%d") + datetime.timedelta(
                        days=-30)).strftime("%Y%m%d"))
                print("日常订单 batch_id =" + str(batch_id))
                dmstore_shopid = int (dmstore_shopid)
                if dmstore_shopid in config.shellgoods_params["start_shop"].keys() and config.shellgoods_params["start_shop"][dmstore_shopid] > int(start_date):
                    print ("该店处于新店期，dmstore_shopid = "+str(dmstore_shopid))
                    sales_order_inss1,result = generate_order_2saler_newshop_notday.generate(dmstore_shopid)
                else:
                    sales_order_inss1,result = generate_order_2saler_add.generate(dmstore_shopid)
                sales_order_inss2,result1 = generate_order_2saler_add_day.generate(dmstore_shopid)
                if sales_order_inss1 is None or sales_order_inss2 is None:
                    cursor_ai.execute(update_sql_02.format(taskflow.cal_status_failed, int(time.time() - start_time),
                                                           id))  # 更新到“结束计算”和耗时多少
                    cursor_ai.connection.commit()
                else:
                    # 把结果转成json , 存入数据库
                    sales_order_inss=[]
                    print ("非日配 订单商品数 ："+str(len(sales_order_inss1)))
                    print("日配 订单商品数 ：" + str(len(sales_order_inss2)))
                    for sales_order_ins in sales_order_inss1:
                        sales_order_inss.append(sales_order_ins)
                    for sales_order_ins in sales_order_inss2:
                        sales_order_inss.append(sales_order_ins)

                    cursor_ai.execute(select_goods_batch_order.format(batch_id,uc_shop_id))
                    goods_batch_data = cursor_ai.fetchone()
                    if goods_batch_data is None:
                        inert_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result1)
                        cursor_ai.executemany(insert_goods_batch_order, inert_data)
                        cursor_ai.connection.commit()
                    else:
                        update_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result1)
                        cursor_ai.execute(update_goods_batch_order.format(update_data[0][1], update_data[0][3],update_data[0][5],goods_batch_data[0]))
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
                    cursor_ai.execute(select_goods_batch_order.format(batch_id,uc_shop_id))
                    goods_batch_data = cursor_ai.fetchone()
                    if goods_batch_data is None:
                        inert_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result)
                        cursor_ai.executemany(insert_goods_batch_order, inert_data)
                        cursor_ai.connection.commit()
                    else:
                        update_data = cacul_util.get_goods_batch_order_data(batch_id,sales_order_inss,uc_shop_id,result)
                        cursor_ai.execute(update_goods_batch_order.format(update_data[0][1],update_data[0][3],update_data[0][5],goods_batch_data[0]))
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