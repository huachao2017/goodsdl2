
import os
import django
import main.import_django_settings
from django.db import connections
from goods.third_tools.dingtalk import send_message
import time
from django.db import close_old_connections
import traceback
sql_workflow = "select id,batch_id,uc_shopid,erp_warehouse_id,type,status,create_time from goods_allworkflowbatch where type in (1,2) and order_goods_status in (1,4) and (unix_timestamp(now()) -unix_timestamp(create_time)) > 240 and (unix_timestamp(now()) -unix_timestamp(create_time)) < 600 "
def alarm_order():
    print ("告警....")
    while True:
        time.sleep(240)
        close_old_connections()
        try:
            order_process()
        except Exception as e:
            print("alarm_order  error e={}".format(e))
            time.sleep(240)
            traceback.print_exc()


def order_process():
    conn = connections['default']
    cursor_ai = conn.cursor()
    # 获取日常订单
    cursor_ai.execute(sql_workflow)
    first_flow_data = cursor_ai.fetchall()
    if first_flow_data is not None and len(first_flow_data) > 0 :
        for data in first_flow_data:
            id = data[0]
            batch_id = data[1]
            erp_warehouse_id = data[3]
            uc_shopid = data[3]
            type = data[4]
            status = data[5]
            create_time = str(data[6])
            msg = "订货计算异常，batch_id={},erp_warehouse_id={},uc_shopid={},type={},status={},create_time={}".format(batch_id,erp_warehouse_id,uc_shopid,type,status,create_time)
            print (msg)
            send_message(msg,3)
    cursor_ai.close()
    conn.close()


if __name__=='__main__':
    alarm_order()