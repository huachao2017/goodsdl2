import os
import smtplib,pymysql
from email.mime.text import MIMEText
import numpy as np
from PIL import Image as PILImage
import json
import django
import os
import time
import datetime
from  decimal import Decimal

import datetime
import math
from django.db import connections
import traceback
from set_config import config
from goods.third_tools.dingtalk import send_message
from goods.sellgoods.salesquantity.service.order_version_5.data_util.goods_info import *



import main.import_django_settings
from django.db import connections



class SendEmail():
    """
    注意️：
    只支持163和qq，需要登录邮箱开启smtp服务
    passwd: 163的话是邮箱密码，qq的话是授权码
    """

    def __init__(self, mail_account, passwd, recv):
        """
        :param mail_account: 邮箱账号
        :param passwd: 163的话是邮箱密码，qq的话是授权码
        :param recv: 邮箱接收人地址，多个账号以逗号隔开

        """
        self.mail_account = mail_account
        self.passwd = passwd
        self.recv = recv
        # self.title = title
        # self.content = content
        self.mail_host = mail_account.split('@')[1].split('.')[0]

    def send_mail(self,title,content):
        """
        :param title: 邮件标题
        :param content: 邮件内容
        :return:
        """

        try:
            msg = MIMEText(content)  # 邮件内容
            msg['Subject'] = title  # 邮件主题
            msg['From'] = self.mail_account  # 发送者账号
            msg['To'] = self.recv  # 接收者账号列表
            smtp = None
            if self.mail_host == '163':
                smtp = smtplib.SMTP('smtp.163.com', port=25)  # 连接邮箱，传入邮箱地址，和端口号，smtp的端口号是25
            if self.mail_host == 'qq':
                smtp = smtplib.SMTP_SSL('smtp.qq.com', port=465)
            smtp.login(self.mail_account, self.passwd)  # 发送者的邮箱账号，密码
            smtp.sendmail(self.mail_account, self.recv, msg.as_string())
            # 参数分别是发送者，接收者，第三个是把上面的发送邮件的内容变成字符串
            smtp.quit()  # 发送完毕后退出smtp
            print('email send success.')
        except:
            print('email send error.')

def calculate_goods_up_datetime(uc_shopid):
    """
    基于台账的计算商品的上架时间
    :param uc_shopid:  台账系统的shopid
    :return:
    """
    conn = connections['ucenter']
    cursor = conn.cursor()
    conn_ai = connections['default']
    cursor_ai = conn_ai.cursor()
    # 当前的台账
    select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    insert_sql = "insert into goods_up_shelf_datetime(upc,shopid,name,up_shelf_date,is_new_goods,taizhang_batch_no) values (%s,{},%s,%s,1,%s)"
    select_sql_03 = "select upc,taizhang_batch_no from goods_up_shelf_datetime where shopid={}"
    delete_sql = "delete from goods_up_shelf_datetime where shopid={} and upc in ({})"

    cursor.execute(select_sql_02)
    all_data = cursor.fetchall()

    cursor_ai.execute(select_sql_03.format(uc_shopid))
    history_data = cursor_ai.fetchall()

    history_upc_dict = {}    # 键为upc，值批次号
    for data in history_data:
        history_upc_dict[data[0]] = data[1]



    # 1、遍历新的台账，如果某个商品在所有历史的商品里，则不做操作；如果没在，则插入
    insert_data_list = []
    update_data_list = []
    new_upc_list = []
    for data in all_data:
        for goods_info in json.loads(data[4]):
            for layer in goods_info['layerArray']:
                for goods in layer:
                    goods_upc = goods['goods_upc']
                    new_upc_list.append(goods_upc)
                    goods_name = goods['name']
                    goods_up_shelf_datetime = data[2].split('_')[1]
                    if not goods_upc in history_upc_dict:      # 如果不在历史里，则作为新的插入
                        insert_data_list.append((goods_upc,goods_name,goods_up_shelf_datetime,data[2]))
                    else:
                        if data[2] != history_upc_dict[goods_upc]:     # 如果批次不相等，则是新的台账，品也相同，所以is_new_goods置为0
                            cursor_ai.execute("update goods_up_shelf_datetime set is_new_goods=0 where shopid={} and upc='{}'".format(uc_shopid,goods_upc))

    print('insert_data_list:',insert_data_list)
    cursor_ai.executemany(insert_sql.format(uc_shopid), tuple(insert_data_list))
    conn_ai.commit()
    print("上架时间插入成功")
    # 2、遍历历史商品表，如果每个商品没在新的台账里，则说明是下架的品，则删除
    delete_data_list = []
    for upc in history_upc_dict:
        if not upc in new_upc_list:
            delete_data_list.append(upc)
    print('delete_data_list:',delete_data_list)
    if delete_data_list:
        print('delete_sql',delete_sql.format(uc_shopid,tuple(delete_data_list)))
        cursor_ai.execute(delete_sql.format(uc_shopid,",".join(delete_data_list)))
        conn_ai.commit()
    print("下架商品删除成功")

def calculate_goods_up_datetime_first(uc_shopid):
    """
    基于台账的计算商品的上架时间
    :param uc_shopid:  台账系统的shopid
    :return:
    """
    conn = connections['ucenter']
    cursor = conn.cursor()
    conn_ai = connections['default']
    cursor_ai = conn_ai.cursor()
    # 已完成的台账
    select_sql_01 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=3 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    insert_sql = "insert into goods_up_shelf_datetime(upc,shopid,name,up_shelf_date,taizhang_batch_no) values (%s,{},%s,%s,%s)"
    select_sql_03 = "select upc from goods_up_shelf_datetime where shopid={}"
    delete_sql = "delete from goods_up_shelf_datetime where shopid={} and upc in {}"

    cursor.execute(select_sql_01)
    all_data = cursor.fetchall()

    cursor_ai.execute(select_sql_03.format(uc_shopid))



    # 1、遍历新的台账，如果某个商品在所有历史的商品里，则不做操作；如果没在，则插入
    insert_data_list = []
    update_data_list = []
    new_upc_list = []
    for data in all_data:
        print(type(data[1]))
        if data[1] == 1088:
            if not data[2].startswith('1142_20191106'):
                continue
        if data[1] == 1096:
            if not data[2].startswith('1169_20191107'):
                continue
        if data[1] == 1100:
            if not data[2].startswith('1169_20191107'):
                continue
        for goods_info in json.loads(data[4]):
            for layer in goods_info['layerArray']:
                for goods in layer:
                    goods_upc = goods['goods_upc']
                    new_upc_list.append(goods_upc)
                    goods_name = goods['name']
                    goods_up_shelf_datetime = data[2].split('_')[1]
                    insert_data_list.append((goods_upc, goods_name, goods_up_shelf_datetime,data[2]))
    print('insert_data_list:', insert_data_list)
    cursor_ai.executemany(insert_sql.format(uc_shopid), tuple(insert_data_list))
    conn_ai.commit()
    print("上架时间插入成功")
    cursor_ai.execute("update goods_up_shelf_datetime set is_new_goods=0 where shopid={}".format(uc_shopid))

def select_psd_data(upc,shop_id,time_range):
    """
    计算某商品在模板店一定取数周期内的psd和psd金额
    :param upc:
    :param shop_id: 目标门店，根据此id去查询模板id
    :param time_range: 取数周期
    :return: psd,psd金额
    """
    template_dict = {1284:3598,'1284':3598}  # 临时解决方案，先写死
    template_shop_id = template_dict[shop_id]
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d %H:%M:%S')
    week_ago = (now - datetime.timedelta(days=time_range)).strftime('%Y-%m-%d %H:%M:%S')
    sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id={} and g.upc='{}';"
    # conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
    conn = connections['dmstore']
    cursor = conn.cursor()
    cursor.execute(sql.format(week_ago,now_date,template_shop_id,upc))
    result = cursor.fetchone()
    cursor.close()
    # conn.close()
    if result:
        try:
            # print(result)
            return result[0]/(result[4]*time_range),result[0]/time_range
        except:
            # print("psd计算异常")
            return None,None
    else:
        return None,None

def select_category_psd_data(category,shop_id,time_range):
    """
    计算模板店的三级分类下的平均每个商品每天的psd和psd金额
    :param category: 三级分类
    :param shop_id: pos系统的门店id
    :param time_range: 取数周期
    :return: psd,psd金额
    """
    template_dict = {1284: 3598, '1284': 3598}  # 临时解决方案，先写死
    template_shop_id = template_dict[shop_id]
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d %H:%M:%S')
    week_ago = (now - datetime.timedelta(days=time_range)).strftime('%Y-%m-%d %H:%M:%S')
    sql = "select sum(p.amount),COUNT(DISTINCT g.neighbor_goods_id),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id={} and g.corp_classify_code='{}';"
    # conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
    conn = connections['dmstore']
    cursor = conn.cursor()
    cursor.execute(sql.format(week_ago, now_date, template_shop_id, category))
    result = cursor.fetchone()
    cursor.close()
    # conn.close()
    if result:
        try:
            # print(result)
            return result[0] / (result[5] * time_range * int(result[1])), result[0] / (time_range * int(result[1]))
        except:
            # print("psd计算异常")
            return None, None
    else:
        return None, None


def check_order():
    """
    动态测试代码而已
    检查订货是否有异常的地方
    :return:
    """
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d %H:%M:%S')
    week_ago = (now - datetime.timedelta(days=28)).strftime('%Y-%m-%d %H:%M:%S')
    sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id={} and g.upc='{}';"
    sql_02 = "select name from dmstore.goods where upc='{}';"
    sql_03 = "select delivery_type,storage_day from uc_merchant_goods where upc='{}';"


    # conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
    conn = connections['dmstore']
    cursor = conn.cursor()
    conn_ucenter = connections['ucenter']
    cursor_ucenter = conn_ucenter.cursor()


    order_list = [{"max_disnums":5,"mch_goods_code":"2004083","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":2,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":23.0,"upc":"6921168509256"},{"max_disnums":5,"mch_goods_code":"2005413","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":10.0,"upc":"6925303721367"},{"max_disnums":5,"mch_goods_code":"2036329","min_disnums":4,"order_sale":2.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":3.0,"supply_stock":28.0,"upc":"6970399920132"},{"max_disnums":5,"mch_goods_code":"2040681","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":4.0,"upc":"6921317905014"},{"max_disnums":5,"mch_goods_code":"2043574","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":17.0,"upc":"6970399920415"},{"max_disnums":5,"mch_goods_code":"2040259","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":2.0,"upc":"6954767430461"},{"max_disnums":5,"mch_goods_code":"2003228","min_disnums":4,"order_sale":3.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":2.0,"supply_stock":49.0,"upc":"6906907401022"},{"max_disnums":6,"mch_goods_code":"2044177","min_disnums":4,"order_sale":2.0,"shelf_order_info":[{"face_num":2,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":2.0,"upc":"6954767417684"},{"max_disnums":5,"mch_goods_code":"2026864","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":27.0,"upc":"6921581540102"},{"max_disnums":5,"mch_goods_code":"2030866","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1096,"shelf_order":0,"tz_id":1169}],"shop_stock":4.0,"supply_stock":5.0,"upc":"6941067725571"},{"max_disnums":3,"mch_goods_code":"2004092","min_disnums":4,"order_sale":1.0,"shelf_order_info":[{"face_num":2,"shelf_id":1100,"shelf_order":0,"tz_id":1173}],"shop_stock":2.0,"supply_stock":14.0,"upc":"6921168520015"},{"max_disnums":1,"mch_goods_code":"2021477","min_disnums":3,"order_sale":1.0,"shelf_order_info":[{"face_num":1,"shelf_id":1101,"shelf_order":0,"tz_id":1174}],"shop_stock":0.0,"supply_stock":8.0,"upc":"6925303714840"}]

    merchant_dict = {1:'日配',2:'非日配',None:None}

    for d in order_list:
        print(d)
        # cursor.execute(sql.format(week_ago, now_date, 1284, d['upc']))
        # result = cursor.fetchone()
        # print(result)
        cursor.execute(sql_02.format(d['upc']))
        result_01 = cursor.fetchone()

        cursor_ucenter.execute(sql_03.format(d['upc']))
        result_02 = cursor_ucenter.fetchone()
        print('商品:{}'.format(result_01[0]),', 配送类型:{}'.format(merchant_dict[result_02[0]]),', 保质期（天）:{}'.format(result_02[1]))
        print()
        print()

def data_exception_alarm(shopid):
    """
        获取商店的所有货架及货架上的商品信息，进行数据异常报警
        :param shopid: fx系统的商店id
        """
    ret = []
    cursor = connections['ucenter'].cursor()
    cursor_dmstore = connections['dmstore'].cursor()
    cursor_erp = connections['erp'].cursor()
    cursor_ai = connections['default'].cursor()
    try:
        cursor_bi = connections['bi'].cursor()
    except:
        cursor_bi = None
    # 获取台账系统的uc_shopid
    cursor.execute('select id, shop_name , mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    (uc_shopid, shop_name, mch_id) = cursor.fetchone()
    if not uc_shopid:
        send_message('{}在台账系统找不到对应的shopid！'.format(shopid))
    # 获取erp系统的erp_shopid
    erp_resupply_id = None
    erp_supply_id = None
    try:
        cursor_dmstore.execute("select erp_shop_id from erp_shop_related where shop_id = {} and erp_shop_type = 0".format(shopid))
        (erp_shop_id,) = cursor_dmstore.fetchone()  # 门店id
        print("erp 门店id" + str(erp_shop_id))
        cursor_erp.execute("SELECT authorized_shop_id from ms_relation WHERE is_authorized_shop_id = {} and  status=1".format(erp_shop_id))
        (erp_supply_id,) = cursor_erp.fetchone()  # 仓库id
        print("erp 仓库id" + str(erp_supply_id))
        cursor_erp.execute("SELECT authorized_shop_id from ms_relation WHERE is_authorized_shop_id = {} and  status=1".format(erp_supply_id))
        (erp_resupply_id,) = cursor_erp.fetchone()  # 供货商id
        print("erp 供货商id" + str(erp_resupply_id))

        if erp_shop_id is None or erp_supply_id is None or erp_resupply_id is None:
            send_message('pos店号为{}的店，获取的erp_shop_id异常：{}'.format(shopid, None), 3)
    except:
        send_message('pos店号为{}的店，获取的erp_shop_id异常：{}'.format(shopid,None), 3)

    # 获取台账 TODO 只能获取店相关的台账，不能获取商家相关的台账
    cursor.execute(
        "select t.id, t.shelf_id, td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status in (1,2) and td.approval_status=1 and st.shop_id = {}".format(
            uc_shopid))
    taizhangs = cursor.fetchall()
    for taizhang in taizhangs:
        taizhang_id = taizhang[0]
        shelf_id = taizhang[1]
        shelf_type = ''
        shelf_type_id = None
        try:
            cursor.execute("select id,shelf_type_id from sf_shelf where id = {}".format(shelf_id))
            (id, shelf_type_id) = cursor.fetchone()
        except:
            print("台账找不到货架 ， shelf_id=" + str(shelf_id))
            traceback.print_exc()

        try:
            cursor.execute("select id,type_name from sf_shelf_type where id = {} ".format(shelf_type_id))
            (id, type_name) = cursor.fetchone()
            shelf_type = type_name
        except:
            print("台账找不到货架类型名称 ， shelf_type_id=" + str(shelf_type_id),3)
            traceback.print_exc()
        display_shelf_info = taizhang[2]
        display_goods_info = taizhang[3]
        display_shelf_info = json.loads(display_shelf_info)
        display_goods_info = json.loads(display_goods_info)
        shelfs = display_shelf_info['shelf']
        shelf_dict = {}
        goods_array_dict = {}
        for shelf in shelfs:
            shelf_dict[shelf['shelfId']] = shelf['layer']
        for goods_info in display_goods_info:
            goods_array_dict[goods_info['shelfId']] = goods_info['layerArray']

        for shelfId in shelf_dict.keys():
            level_array = shelf_dict[shelfId]
            goods_array = goods_array_dict[shelfId]
            for i in range(len(level_array)):
                level = level_array[i]
                goods_level_array = goods_array[i]
                level_depth = round(float(level['depth']))
                if level_depth is None or level_depth <= 0:
                    send_message('uc店号为{}、id为{}的货架的第{}层深度异常为{}'.format(uc_shopid,shelfId,i+1,level_depth),3)
                for goods in goods_level_array:
                    mch_code = goods['mch_goods_code']

                    # time.sleep(5)

                    if mch_code in ret:
                        print("该商品已查询过")
                    elif mch_code != "2027047" or mch_code != 2027047:
                        continue
                    else:
                        ret.append(mch_code)
                        # 从台账获取商品属性
                        try:
                            print(shelf_id)
                            p_depth = goods["p_depth"]
                            if p_depth is None or p_depth <=0:
                                send_message(
                                    "台账id为{}，货架id为{}，mch_goods_code为{}的商品p_depth属性异常：{}".format(taizhang_id, shelf_id,
                                                                                             mch_code,p_depth),3)
                        except:
                            send_message("台账id为{}，货架id为{}，mch_goods_code为{}的商品没有p_depth属性".format(taizhang_id,shelf_id,mch_code),3)

                        # continue
                        # 从库里获取商品属性
                        try:
                            cursor.execute(
                                "select id, goods_name,upc, tz_display_img, spec, volume, width,height,depth,is_superimpose,is_suspension,display_first_cat_id,display_second_cat_id,display_third_cat_id,storage_day,package_type,supplier_id,supplier_goods_code from uc_merchant_goods where mch_id = {} and mch_goods_code = {}".format(
                                    mch_id, mch_code))
                            (goods_id, goods_name, upc, tz_display_img, spec, volume, height, width, depth,
                             is_superimpose,is_suspension, display_first_cat_id,display_second_cat_id,display_third_cat_id, storage_day,
                             package_type,supplier_id,supplier_goods_code) = cursor.fetchone()

                            if upc is None or display_third_cat_id is None or display_third_cat_id ==0 or display_third_cat_id =="0" or storage_day is None or storage_day <=0 or depth <= 0:
                                send_message('mch_code为{}的商品存在空字段或异常值，upc:{}，陈列三级分类(display_third_cat_id):{}，保质期(storage_day):{}，陈列时所占深度(p_depth):{}'.format(mch_code,upc,display_third_cat_id,storage_day,depth),3)
                                print('mch_code为{}的商品存在空字段，upc:{}，陈列三级分类(display_third_cat_id):{}，保质期(storage_day):{}，陈列时所占深度(p_depth):{}'.format(mch_code,upc,display_third_cat_id,storage_day,depth))
                        except:
                            send_message('mch_code为{}的商品在库里找不到'.format(mch_code),3)
                            continue
                        # 获取最大陈列系数


                        # 单价和库存
                        try:
                            cursor_dmstore.execute(
                                "select id,price,purchase_price,stock FROM shop_goods where upc = '{}' and shop_id = {} order by modify_time desc ".format(
                                    upc, shopid))
                            (id, upc_price, purchase_price, stock) = cursor_dmstore.fetchone()
                            if upc_price is None or upc_price <= 0:
                                send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品单价异常:{}'.format(goods_name,uc_shopid,mch_code,upc,upc_price),3)
                            if stock is None or stock < 0:
                                send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品库存异常:{}'.format(goods_name,uc_shopid,mch_code,upc,stock),3)

                        except:
                            send_message('{}(uc店号:{},mch_code:{},upc:{})—>>库存和单价异常为：{}、{}'.format(goods_name, uc_shopid, mch_code,upc,None,None),3)


                        # 获取起订量
                        # if erp_resupply_id is not None:
                        #     try:
                        #         # 获取起订量
                        #         # "select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id in (select sku_id from ls_sku where model_id = '{0}' and ls_sku.prod_id in (select ls_prod.prod_id from ls_prod where ls_prod.shop_id = {1} ))"
                        #         cursor_erp.execute("select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}' AND s.party_code='{}'".format(erp_resupply_id, upc,mch_code))
                        #         (sku_id,) = cursor_erp.fetchone()
                        #         cursor_erp.execute("select start_sum,multiple from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(sku_id))
                        #         (start_sum, multiple) = cursor_erp.fetchone()
                        #
                        #         if start_sum is None or start_sum <= 0:
                        #             send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品起订量异常:{}'.format(goods_name, uc_shopid,mch_code, upc, start_sum),3)
                        #     except:
                        #         try:
                        #             # 看是什么原因导致查询不到，一可能是好邻居码和upc不对应，二可能是不可订货
                        #             cursor_erp.execute(
                        #                 "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} AND s.party_code='{}'".format(
                        #                     erp_resupply_id, mch_code))
                        #             (sku_id,) = cursor_erp.fetchone()
                        #             if sku_id:
                        #                 cursor_erp.execute(
                        #                     "select model_id ,party_code  from ls_prod where shop_id='{}' and  party_code='{}';".format(
                        #                         erp_resupply_id, mch_code))
                        #                 (upc_2,) = cursor_erp.fetchone()
                        #
                        #                 send_message(
                        #                     '{}(uc店号:{},mch_code:{},upc:{})—>>商品mch_code和upc不对应，该mch_code查出的upc为{}'.format(goods_name, uc_shopid,
                        #                                                                          mch_code, upc,upc_2), 3)
                        #         except:
                        #             send_message(
                        #                 '{}(uc店号:{},mch_code:{},upc:{})—>>商品在好邻居不可订货'.format(goods_name, uc_shopid,
                        #                                                                 mch_code, upc),3)

                        # 获取商品的 可定  起订量  配送类型

                        if erp_resupply_id is not None:
                            # try:
                                cursor.execute(
                                    "select min_order_num,order_status,delivery_type from uc_supplier_goods where supplier_id = {} and supplier_goods_code = {} and order_status = 1 ".format(
                                        supplier_id, supplier_goods_code))
                                (start_sum, order_status, delivery_type_str) = cursor.fetchone()
                                cursor.execute(
                                    "select delivery_attr from uc_supplier_delivery where delivery_code = '{}' ".format(
                                        delivery_type_str))
                                (delivery_type,) = cursor.fetchone()

                                if start_sum is None or start_sum <= 0:
                                    send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品起订量异常:{}'.format(goods_name, uc_shopid,mch_code, upc, start_sum),3)
                                if order_status is None or order_status not in (1,2,'1','2'):
                                    send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品是否可订货数据异常:{}'.format(goods_name, uc_shopid,mch_code, upc, order_status),3)
                                if delivery_type is None or delivery_type not in (1,2,'1','2'):
                                    send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品配送类型数据异常:{}'.format(goods_name, uc_shopid,mch_code, upc, delivery_type),3)

                            # except:
                            #     send_message(
                            #         '{}(uc店号:{},mch_code:{},upc:{})—>>获取商品的是否可定、起订量、配送类型数据失败'.format(goods_name, uc_shopid,
                            #                                                              mch_code, upc), 3)


                        # 获取小仓库库存
                        if erp_supply_id is not None:
                            try:
                                cursor_erp.execute(
                                    "select s.sku_id prod_id from ls_prod as p, ls_sku as s where p.prod_id = s.prod_id and p.shop_id = {} and s.model_id = '{}'".format(
                                        erp_supply_id, upc))
                                (sku_id,) = cursor_erp.fetchone()
                                cursor_erp.execute(
                                    "select stock from ms_sku_relation where ms_sku_relation.status=1 and sku_id = {}".format(
                                        sku_id))
                                (supply_stock,) = cursor_erp.fetchone()

                                if supply_stock is None or supply_stock < 0:
                                    send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品小仓库库存异常:{}'.format(goods_name,uc_shopid,mch_code,upc,supply_stock),3)
                            except:
                                send_message(
                                    '{}(uc店号:{},mch_code:{},upc:{})—>>商品小仓库库存异常:{}'.format(goods_name, uc_shopid, mch_code,
                                                                                       upc, None),3)

                        # 获取商品的上架时间、是否新品
                        try:
                            cursor_ai.execute(
                                "select up_shelf_date,is_new_goods from goods_up_shelf_datetime where shopid={} and upc='{}'".format(
                                    uc_shopid, upc))
                            (up_shelf_date, up_status) = cursor_ai.fetchone()
                            if not up_status in (0,1):
                                send_message('{}(uc店号:{},mch_code:{},upc:{})—>>商品的"是否新品"字段异常,is_new_goods:{}'.format(goods_name, uc_shopid, mch_code, upc,
                                                                                                            up_status),3)
                        except:
                            send_message(
                                '{}(uc店号:{},mch_code:{},upc:{})—>>商品的"是否新品"和"上架时间"字段异常:{},{}'.format(goods_name,uc_shopid,mch_code, upc,None,None),3)

                        # 获取商品的最小陈列量
                        try:
                            cursor_ai.execute(
                                "select single_face_min_disnums from goods_config_disnums where shop_id={} and shelf_id={} and upc='{}'".format(
                                    shopid,shelf_id,upc))
                            (single_face_min_disnums,) = cursor_ai.fetchone()
                            if single_face_min_disnums is None or single_face_min_disnums <= 0:
                                send_message(
                                    '{}(uc店号:{},货架id:{},mch_code:{},upc:{})—>>商品的最小陈列量字段异常:{}'.format(
                                        goods_name,shelf_id,uc_shopid,mch_code, upc,
                                        single_face_min_disnums),3)
                        except:
                            send_message(
                                '{}(uc店号:{},货架id:{},mch_code:{},upc:{})—>>商品的最小陈列量字段异常:{}'.format(
                                    goods_name,uc_shopid, shelf_id, mch_code, upc,
                                    None),3)


    cursor.close()
    cursor_dmstore.close()
    cursor_erp.close()
    cursor_ai.close()
    if cursor_bi is not None:
        cursor_bi.close()


if __name__ == '__main__':
    # calculate_goods_up_datetime(806)

    # calculate_goods_up_datetime_first(806)

    # print(select_psd_data('6922577726258',1284,28))

    # check_order()

    data_exception_alarm(1284)

