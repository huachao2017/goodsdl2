
import pymysql
import datetime
import os,django,time,math
from goods.sellgoods.auto_choose_goods.haolinju_template import start_choose_goods

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections

if __name__ == '__main__':
    # conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)
    # cursor = conn.cursor()
    select_sql = "select id,batch_id,uc_shopid from goods_allworkflowbatch where select_goods_status=1"
    select_sql_shopid = "select mch_shop_code from uc_shop where id = {}"
    update_sql_01 = "update goods_allworkflowbatch set select_goods_status={} where id={}"    #2是正在计算、3是计算结束
    update_sql_02 = "update goods_allworkflowbatch set select_goods_status=3,select_goods_calculate_time={} where id={}"    #2是正在计算、3是计算结束
    while True:
        time.sleep(5)
        print("circulation")
        conn = connections['default']
        cursor = conn.cursor()
        cursor.execute(select_sql)
        all_data = cursor.fetchall()
        if all_data:
            for data in all_data:
                start_time = time.time()
                try:
                    cursor.execute(update_sql_01.format(2,data[0]))   # 更新到“正在计算”
                    print('正在计算中...')
                    conn.commit()
                    # conn.close()
                    ucenter_conn = connections['ucenter']
                    ucenter_cursor = ucenter_conn.cursor()
                    ucenter_cursor.execute(select_sql_shopid.format(data[2]))
                    shopid = ucenter_cursor.fetchone()[0]
                    ucenter_conn.close()

                    # time.sleep(5)
                    # for i in range(3):
                    print('shopid',shopid)
                    print('id',data[0])

                    start_choose_goods(data[1],shopid,conn)   #计算中

                except Exception as e:
                    print('Exception',e)
                    cursor.execute(update_sql_01.format(4, data[0]))  # 4代表失败
                    continue

                cursor = conn.cursor()
                cursor.execute(update_sql_02.format(math.ceil(time.time() - start_time),data[0]))  # 更新到“结束计算”和耗时多少
                conn.commit()
        conn.close()
