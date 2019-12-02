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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
import math
from django.db import connections

from dl.util import visualize_boxes_and_labels_on_image_array_for_shelf

def wrap_ret(ret):
    standard_ret = {
        'status': 200,
        'message': '成功',
        'attachment': ret,
    }
    return standard_ret

def shelf_visualize(boxes, image_path):
    image = PILImage.open(image_path)
    text_infos = []
    color_infos = []
    for one in boxes:
        text_infos.append('{}-{}'.format(one['level'], one['upc']))
        color = 'black'
        if one['result'] == 0:
            color = 'blue'
        elif one['result'] == 1 or one['result'] == 2:
            color = 'red'
        color_infos.append(color)
    image_np = np.array(image)
    visualize_boxes_and_labels_on_image_array_for_shelf(
        image_np,
        boxes,
        text_infos,
        color_infos
    )
    output_image = PILImage.fromarray(image_np)
    image_dir = os.path.dirname(image_path)
    result_image_name = 'visual_' + os.path.split(image_path)[-1]
    result_image_path = os.path.join(image_dir, result_image_name)
    # (im_width, im_height) = image.size
    # output_image.thumbnail((int(im_width), int(im_height)), PILImage.ANTIALIAS)
    output_image.save(result_image_path)
    return result_image_name


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
    # 已完成的台账
    # select_sql_01 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=3 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    # 当前的台账
    select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    insert_sql = "insert into goods_up_shelf_datetime(upc,shopid,name,up_shelf_date) values (%s,{},%s,%s)"
    select_sql_03 = "select upc from goods_up_shelf_datetime where shopid={}"
    delete_sql = "delete from goods_up_shelf_datetime where shopid={} and upc in {}"

    cursor.execute(select_sql_01)
    all_data = cursor.fetchall()

    cursor_ai.execute(select_sql_03.format(uc_shopid))
    history_data = cursor_ai.fetchall()

    history_upc_list = [i[0] for i in history_data]

    # 0、把旧的台账里的商品的is_new_goods的状态置为0
    cursor_ai.execute("update goods_up_shelf_datetime set is_new_goods ")
    # 1、遍历新的台账，如果某个商品在所有历史的商品里，则不做操作；如果没在，则插入
    insert_data_list = []
    update_data_list = []
    new_upc_list = []
    for data in all_data:
        # print(type(data[1]))
        # if data[1] == 1088:
        #     if not data[2].startswith('1142_20191106'):
        #         continue
        # if data[1] == 1096:
        #     if not data[2].startswith('1142_20191106'):
        #         continue
        for goods_info in json.loads(data[4]):
            for layer in goods_info['layerArray']:
                for goods in layer:
                    goods_upc = goods['goods_upc']
                    new_upc_list.append(goods_upc)
                    goods_name = goods['name']
                    goods_up_shelf_datetime = data[2].split('_')[1]
                    if not goods_upc in history_upc_list:
                        insert_data_list.append((goods_upc,goods_name,goods_up_shelf_datetime))
    print('insert_data_list:',insert_data_list)
    cursor_ai.executemany(insert_sql.format(uc_shopid), tuple(insert_data_list))
    conn_ai.commit()
    print("上架时间插入成功")
    # 2、遍历历史商品表，如果每个商品没在新的台账里，则说明是下架的品，则删除
    delete_data_list = []
    for upc in history_upc_list:
        if not upc in new_upc_list:
            delete_data_list.append(upc)
    print('delete_data_list:',delete_data_list)
    if delete_data_list:
        cursor_ai.execute(delete_sql.format(uc_shopid,tuple(delete_data_list)))
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
    # 当前的台账
    select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(
        uc_shopid)
    insert_sql = "insert into goods_up_shelf_datetime(upc,shopid,name,up_shelf_date) values (%s,{},%s,%s)"
    select_sql_03 = "select upc from goods_up_shelf_datetime where shopid={}"
    delete_sql = "delete from goods_up_shelf_datetime where shopid={} and upc in {}"

    cursor.execute(select_sql_01)
    all_data = cursor.fetchall()

    cursor_ai.execute(select_sql_03.format(uc_shopid))
    history_data = cursor_ai.fetchall()

    history_upc_list = [i[0] for i in history_data]

    # 0、把旧的台账里的商品的is_new_goods的状态置为0

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
                    insert_data_list.append((goods_upc, goods_name, goods_up_shelf_datetime))
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
    template_dict = {1284:3598}  # 临时解决方案，先写死
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
    conn.close()
    if result:
        try:
            # print(result)
            return result[0]/(result[4]*time_range),result[0]/time_range
        except:
            # print("psd计算异常")
            return None,None
    else:
        return None,None



if __name__ == '__main__':
    """Test code: Uses the two specified"""

    # boxes = [{'level': 1, 'xmin': 200, 'ymin': 200, 'xmax': 400, 'ymax': 400, 'result': 1, 'upc':''}]
    # image_path = 'c:/fastbox/1.jpg'
    #
    # shelf_visualize(boxes,image_path)

    # email_user = 'wlgcxy2012@163.com'  # 发送者账号
    # # email_user = '1027342194@qq.com'  # 发送者账号
    # email_pwd = '2012wl'  # 发送者密码
    # # email_pwd = 'rwpgeglecgribeei'  # 发送者密码
    # maillist = '1027342194@qq.com'
    # # maillist = 'wlgcxy2012@163.com'
    # title = '测试邮件005'
    # content = '这里是邮件内容'
    # a = SendEmail(email_user, email_pwd, maillist)
    # a.send_mail(title, content)

    # calculate_goods_up_datetime(806)

    calculate_goods_up_datetime_first(806)

    # print(select_psd_data('6921581540102',1284,28))