# -*- coding: utf-8 -*-
import pymysql
import datetime
import os,django,time,math,sys
from goods.utils import SendEmail
from goods.sellgoods.auto_choose_goods.haolinju_template import *
from goods.sellgoods.auto_choose_goods.daily_change_goods import DailyChangeGoods


import main.import_django_settings

from goods.models import AllWorkFlowBatch

from django.db import connections
from django.db import close_old_connections


def get_taizhang_goods(uc_shop_id):
    """
    获取当前台账的商品列表
    :return:
    """
    uc_conn = connections['ucenter']
    uc_cursor = uc_conn.cursor()
    # 获取当前的台账
    select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info,t.mch_id from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(uc_shop_id)
    uc_cursor.execute(select_sql_02)
    all_data = uc_cursor.fetchall()
    if all_data:
        return 1   # 非首次
    else:
        return 0   # 首次





def start_choose_goods(batch_id,uc_shop_id,pos_shopid):
    flag = get_taizhang_goods(uc_shop_id)
    if flag == 0:   # 首次
        print("首次选品")
        a = get_data(pos_shopid, '88,3156,3238')
        print("uc_shopid,pos_shopid", uc_shop_id, pos_shopid)
        # a = storage_day_choose(a)
        # c = choose_goods(a)
        # c = check_order(c)
        save_data(a, batch_id, uc_shop_id)
    elif flag == 1:   # 非首次
        print("汰换选品")
        # f = DailyChangeGoods(pos_shopid, "88,3156,3238",batch_id,uc_shop_id)
        f = DailyChangeGoods(pos_shopid, "1284,3955,3779,1925,4076,1924,3598",batch_id,uc_shop_id)
        f.recommend_03()
    else:
        raise Exception("获取台账失败！")



# if __name__ == '__main__':
#     # conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)
#     # cursor = conn.cursor()
#     select_sql = "select id,batch_id,uc_shopid from goods_allworkflowbatch where select_goods_status=1"
#     select_sql_shopid = "select mch_shop_code from uc_shop where id = {}"
#     update_sql_01 = "update goods_allworkflowbatch set select_goods_status={} where id={}"    #2是正在计算、3是计算结束
#     update_sql_02 = "update goods_allworkflowbatch set select_goods_status=3,select_goods_calculate_time={} where id={}"    #2是正在计算、3是计算结束
#     email = SendEmail('1027342194@qq.com', 'rwpgeglecgribeei', 'wlgcxy2012@163.com')
#
#     while True:
#
#         print("circulation")
#         try:
#             conn = connections['default']
#             cursor = conn.cursor()
#             cursor.execute(select_sql)
#             all_data = cursor.fetchall()
#             conn.close()
#             for data in all_data:
#                 start_time = time.time()
#                 # for i in range(2):
#                 try:
#                     conn = connections['default']
#                     cursor = conn.cursor()
#                     cursor.execute(update_sql_01.format(2,data[0]))   # 更新到“正在计算”
#                     print('正在计算中...')
#                     conn.commit()
#                     # conn.close()
#                     ucenter_conn = connections['ucenter']
#                     ucenter_cursor = ucenter_conn.cursor()
#                     ucenter_cursor.execute(select_sql_shopid.format(data[2]))
#                     shopid = ucenter_cursor.fetchone()[0]
#                     ucenter_conn.close()
#
#                     # time.sleep(5)
#                     # for i in range(3):
#                     print('shopid',shopid)
#                     print('id',data[0])
#
#                     start_choose_goods(data[1],shopid)   #计算中
#                     # break
#                     conn = connections['default']
#                     cursor = conn.cursor()
#                     cursor.execute(update_sql_02.format(math.ceil(time.time() - start_time), data[0]))  # 更新到“结束计算”和耗时多少
#                     conn.commit()
#                     conn.close()
#
#                 except Exception as e:
#                     # print('选品第{}次出错：{}'.format(i + 1, e))
#                     print('选品出错：{}'.format( e))
#                     # email.send_mail('选品第{}次出错'.format(i + 1), '选品第{}次出错：{}'.format(i + 1, e))
#                     email.send_mail('选品出错'.format(1), '选品出错：{}'.format(e))
#                     conn = connections['default']
#                     cursor = conn.cursor()
#                     cursor.execute(update_sql_01.format(4, data[0]))  # 4代表失败
#                     conn.commit()
#                     conn.close()
#                     # continue
#
#         except Exception as e:
#             print('守护进程出现错误：{}'.format(e))
#             email.send_mail('选品出错', '守护进程出现错误：{}'.format(e))
#         time.sleep(5)


if __name__ == "__main__":

    path = os.path.abspath(os.path.dirname(__file__))
    type = sys.getfilesystemencoding()

    email = SendEmail('1027342194@qq.com', 'rwpgeglecgribeei', 'wlgcxy2012@163.com')
    select_sql_shopid = "select mch_shop_code from uc_shop where id = {}"
    while True:
        print('workflow deamon is alive')
        close_old_connections()
        try:
            workflows = AllWorkFlowBatch.objects.filter(select_goods_status=1).all()
            for workflow in workflows:
                for i in range(2):
                    try:
                        workflow.select_goods_status = 2
                        workflow.save()
                        begin_time = time.time()
                        shopid = None
                        try:
                            ucenter_conn = connections['ucenter']
                            ucenter_cursor = ucenter_conn.cursor()
                            ucenter_cursor.execute(select_sql_shopid.format(workflow.uc_shopid))
                            pos_shopid = ucenter_cursor.fetchone()[0]
                            ucenter_conn.close()
                        except Exception as e:
                            print('选品时shopid转换时出现错误：{}'.format(e))
                            email.send_mail('选品出错', '选品时shopid转换时出现错误：{}'.format(e))
                            workflow.select_goods_status = 4
                            workflow.select_goods_calculate_time = 0
                            workflow.save()
                            break

                        try:
                            start_choose_goods(workflow.batch_id, workflow.uc_shopid,pos_shopid)  # 计算中
                        except Exception as e:
                            print('选品过程中出现错误：{}'.format(e))
                            email.send_mail('选品出错', '选品过程中出现错误：{}'.format(e))
                            workflow.select_goods_status = 4
                            workflow.select_goods_calculate_time = 0
                            workflow.save()
                            continue

                        # 更新workflow
                        workflow.select_goods_status = 3
                        workflow.select_goods_calculate_time = math.ceil(time.time() - begin_time)
                        workflow.save()
                        break
                    except Exception as e:
                        print('选品第{}次出错：{}'.format(i+1,e))
                        email.send_mail('选品第{}次出错'.format(i+1),'选品第{}次出错：{}'.format(i+1,e))
                        # 更新workflow
                        workflow.auto_display_status = 4
                        workflow.select_goods_calculate_time = 0
                        workflow.save()
                        time.sleep(10)
                        continue

        except Exception as e:
            print('守护进程出现错误：{}'.format(e))
            email.send_mail('选品出错', '守护进程出现错误：{}'.format(e))

        time.sleep(60)

