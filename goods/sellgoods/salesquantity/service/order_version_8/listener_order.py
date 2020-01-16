"""
流程改动 日配品 选品 订货  陈列， 添加日配品空间限制  https://shimo.im/docs/D8pYpwpT66RQ6vYD/read
该版本上个版本 version6
"""
import time
from goods.sellgoods.salesquantity.service.order_version_8 import order_process
from django.db import close_old_connections
import traceback
def generate_data():
    print ("生成自动订单数据")
    while True:
        time.sleep(10)
        close_old_connections()
        try:
            order_process.day_order_process()
        except Exception as e:
            print("order_process.day_order_process  error e={}".format(e))
            time.sleep(10)
            traceback.print_exc()
        try:
            order_process.add_order_process()
        except Exception as e:
            print("order_process.add_order_process  error e={}".format(e))
            time.sleep(10)
            traceback.print_exc()
if __name__=='__main__':
    generate_data()