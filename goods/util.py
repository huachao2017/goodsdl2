import os
import smtplib
from email.mime.text import MIMEText
import numpy as np
from PIL import Image as PILImage
import json
import django
import os
import time
import datetime
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
    conn = connections['ucenter']
    cursor = conn.cursor()
    conn_dmstore = connections['dmstore']
    cursor_dmstore = conn_dmstore.cursor()
    select_sql_01 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=3 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(uc_shopid)
    insert_sql = "insert into goods_up_shelf_datetime(upc,shopid,name,up_shelf_date) values (%s,{},%s,%s)"

    cursor.execute(select_sql_01)
    all_data = cursor.fetchall()
    data_list = []
    for data in all_data:
        # print(type(data[1]))
        if data[1] == 1088:
            if not data[2].startswith('1142_20191106'):
                continue
        if data[1] == 1096:
            if not data[2].startswith('1142_20191106'):
                continue

        # dd = [{"shelfId":"ZDJ-242-1142-001","layerArray":[[{"top":20.2070796460177,"left":176.09026548672566,"width":150,"height":250.00000000000003,"goods_upc":"6922300664833","name":"Z泉利堂盐津葡萄128g","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da83336c0b4a403.jpg","psd":"0.81","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1100","rotate":"0","goods_num":"1","mch_goods_code":"2043296"},{"top":17.320353982300887,"left":326.2,"width":150,"height":250.00000000000003,"goods_upc":"6922300664796","name":"Z泉利堂话梅条128g","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da83336ca19e429.jpg","psd":"1.22","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1100","rotate":"0","goods_num":"1","mch_goods_code":"2043297"},{"top":5.773451327433628,"left":516.7238938053098,"width":160,"height":250.00000000000003,"goods_upc":"6922279401866","name":"Z简索加州西梅170g_Hi*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da8323546a8e516.jpg","psd":"0.63","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1700","rotate":"90","goods_num":"1","mch_goods_code":"2032250"},{"top":28.86725663716814,"left":2.886725663716814,"width":177,"height":240,"goods_upc":"6936030000243","name":"Z小梅屋六味老梅干80g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832cc43fb5808.jpg","psd":"0.61","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1650","rotate":"0","goods_num":"1","mch_goods_code":"2036734"},{"top":17.320353982300887,"left":707.2477876106195,"width":170,"height":250.00000000000003,"goods_upc":"6913189335655","name":"Z同享话梅120g*","icon_url":"http://lximages.xianlife.com//g1/1911/0619/5dc2b54713c43914.png","psd":"1.1","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"990","compressible":"0","rotate":"0","mch_goods_code":"2005993"}],[{"top":109.69557522123894,"left":135.67610619469028,"width":190,"height":210,"goods_upc":"6922621129684","name":"Z老奶奶花生米180g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da831dfd0217939.jpg","psd":"1.73","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"780","rotate":"0","goods_num":"1","mch_goods_code":"2009647"},{"top":170.31681415929202,"left":788.0761061946903,"width":99.99999999999999,"height":150,"goods_upc":"6948004700400","name":"Z鲜引力柠檬片16g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da8320b887c9450.jpg","psd":"0.83","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"450","rotate":"0","goods_num":"1","mch_goods_code":"2028065"},{"top":135.67610619469028,"left":640.8530973451327,"width":140,"height":185,"goods_upc":"4809010272010","name":"Z-7D芒果干100g（J)*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da83208b29b0396.jpg","psd":"1.96","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"2650","rotate":"0","goods_num":"1","mch_goods_code":"2027404"},{"top":54.84778761061947,"left":493.6300884955752,"width":175,"height":265,"goods_upc":"6940935200264","name":"Z腾飞甘草野杏肉180g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da8321e4eef5911.jpg","psd":"1.22","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1100","rotate":"0","goods_num":"1","mch_goods_code":"2030321"},{"top":54.84778761061947,"left":317.53982300884957,"width":180,"height":265,"goods_upc":"6920771614111","name":"Z恒康碧根果仁108g","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832dd7f16f317.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"3800","compressible":"1","rotate":"0","mch_goods_code":"2037489"},{"top":98.14867256637169,"left":0,"width":135,"height":220,"goods_upc":"6925843404225","name":"Z黄飞红麻辣花生210g*","icon_url":"http://lximages.xianlife.com//g1/1911/0619/5dc2b4b5a235d467.png","psd":"0.5","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1350","compressible":"0","rotate":"0","mch_goods_code":"2022260"}],[{"top":152.99646017699115,"left":0,"width":116,"height":108,"goods_upc":"6959479300316","name":"Z沃隆每日坚果25g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832853c9bf616.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"6","rotate":"0","goods_num":"1","mch_goods_code":"2034639"},{"top":152.99646017699115,"left":129.90265486725664,"width":116,"height":108,"goods_upc":"6959479300316","name":"Z沃隆每日坚果25g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832853c9bf616.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"6","rotate":"0","goods_num":"1","mch_goods_code":"2034639"},{"top":152.99646017699115,"left":265.5787610619469,"width":116,"height":108,"goods_upc":"6959479300323","name":"Z沃隆每日坚果（B）25g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832cb5d23e296.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"6","rotate":"0","goods_num":"1","mch_goods_code":"2036716"},{"top":152.99646017699115,"left":398.3681415929204,"width":116,"height":108,"goods_upc":"6959479300323","name":"Z沃隆每日坚果（B）25g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da832cb5d23e296.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"6","rotate":"0","goods_num":"1","mch_goods_code":"2036716"},{"top":98.14867256637169,"left":531.1575221238938,"width":70,"height":165,"goods_upc":"8809022201035","name":"汤姆农场蜂蜜黄油扁桃仁35g（J）","icon_url":"http://lximages.xianlife.com//g1/1910/1818/5da98eef87fb3816.png","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"9.9","rotate":"0","goods_num":"1","mch_goods_code":"2037690"},{"top":51.96106194690265,"left":617.7592920353982,"width":125.00000000000001,"height":210,"goods_upc":"6947954100872","name":"Z雾岭山山楂球100g","icon_url":"http://lximages.xianlife.com//g1/1910/1818/5da98ef2c2b11659.png","psd":"1.11","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"750","rotate":"0","goods_num":"1","mch_goods_code":"2043567"},{"top":63.50796460176991,"left":759.2088495575222,"width":138,"height":199.99999999999997,"goods_upc":"6947954100889","name":"Z雾岭山果丹皮100g","icon_url":"http://lximages.xianlife.com//g1/1910/2414/5db1423420ccf340.png","psd":"0.28","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"750","rotate":"0","goods_num":"1","mch_goods_code":"2043568"}],[{"top":34.64070796460177,"left":176.09026548672566,"width":165,"height":265,"goods_upc":"6924187828544","name":"Z洽洽瓜子308g*","icon_url":"http://lximages.xianlife.com//g1/1910/1818/5da98eecabe5e201.png","psd":"1.5","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1350","rotate":"0","goods_num":"1","mch_goods_code":"2016445"},{"top":23.093805309734513,"left":352.1805309734513,"width":180,"height":265,"goods_upc":"6922133606086","name":"Z金鸽葵花子160g","icon_url":"http://lximages.xianlife.com//g1/1910/2414/5db14234cad0d442.png","psd":"1.17","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"790","rotate":"0","goods_num":"1","mch_goods_code":"2044197"},{"top":31.753982300884957,"left":545.5911504424779,"width":169,"height":254.99999999999997,"goods_upc":"6920609900539","name":"Z芝麻官怪味胡豆120g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da831f4b4936509.jpg","psd":"1","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"450","rotate":"0","goods_num":"1","mch_goods_code":"2021143"},{"top":0,"left":718.7946902654867,"width":180,"height":245,"goods_upc":"6940188803595","name":"甘源蟹黄蚕豆75g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da83205b0be2433.jpg","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"5","compressible":"1","rotate":"0","mch_goods_code":"2027047"},{"top":31.753982300884957,"left":2.886725663716814,"width":167,"height":258,"goods_upc":"6923299611761","name":"Z阿海鱼豆腐烧烤味100g*","icon_url":"http://lximages.xianlife.com//g1/1911/0619/5dc2b4464d80b606.png","psd":"0.28","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"750","compressible":"0","rotate":"0","mch_goods_code":"2033568"}],[{"top":0,"left":0,"width":190,"height":285,"goods_upc":"6901757301010","name":"Z老四川五香牛肉干138g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da83200ce8d2171.jpg","psd":"2.81","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"3800","rotate":"0","goods_num":"1","mch_goods_code":"2025885"},{"top":2.886725663716814,"left":352.1805309734513,"width":184,"height":281,"goods_upc":"6952675319915","name":"Z久久丫甜辣鸭脖110g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da8323e939da159.jpg","psd":"1.44","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1950","rotate":"0","goods_num":"1","mch_goods_code":"2032641"},{"top":0,"left":534.0442477876106,"width":190,"height":240,"goods_upc":"6952675337735","name":"Z久久丫薄豆干185g*","icon_url":"http://lximages.xianlife.com//g1/1910/1717/5da8329013163997.jpg","psd":"2.69","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1450","rotate":"0","goods_num":"1","mch_goods_code":"2034831"},{"top":0,"left":173.20353982300884,"width":190,"height":285,"goods_upc":"6901757300020","name":"Z老四川香辣牛肉干100g*","icon_url":"http://lximages.xianlife.com//g1/1911/0619/5dc2b38b01c10278.png","psd":"1.07","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"2900","compressible":"0","rotate":"0","mch_goods_code":"2023000"},{"top":0,"left":713.0212389380531,"width":190,"height":285,"goods_upc":"6920382723202","name":"Z乐惠小黄鱼106g*","icon_url":"http://lximages.xianlife.com//g1/1911/0611/5dc23ca963bb5855.png","psd":"","salenumber_psd":"","remark":"","is_fitting":"0","goods_price":"1150","compressible":"1","rotate":"0","mch_goods_code":"2031206"}]]}]

        for goods_info in json.loads(data[4]):
            for layer in goods_info['layerArray']:
                for goods in layer:
                    goods_upc = goods['goods_upc']
                    goods_name = goods['name']
                    goods_up_shelf_datetime = data[2].split('_')[1]
                    data_list.append((goods_upc,goods_name,goods_up_shelf_datetime))

    cursor_dmstore.executemany(insert_sql.format(uc_shopid), tuple(data_list))
    conn_dmstore.commit()




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

    calculate_goods_up_datetime(806)