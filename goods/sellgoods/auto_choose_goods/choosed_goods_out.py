

# 输出选品结果给运营angela查看


import decimal
import json
from  decimal import Decimal
import datetime,pymysql,time
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections
from django.db import close_old_connections


def goods_out(uc_shopid,template_shop_ids,batch_id,days):
    """
    输出选品结果给运营angela查看
    :return:
    """
    # conn_ucenter = connections['ucenter']
    # cursor_ucenter = conn_ucenter.cursor()
    conn_ai = connections['default']
    cursor_ai = conn_ai.cursor()
    # conn_dmstore = connections['dmstore']
    # cursor_dmstore = conn_dmstore.cursor()
    print("时间,门店id,门店名称,一级分类,二级分类,三级分类,四级分类,配送类型,商品编码,商品名称,商品upc,策略标签,商品角色,上品优先级排名,商品实际销售4周预期psd金额,商品实际销售4周预期psd,组内门店4周预期psd金额,组内门店4周预期psd")


    select_sql = "select * from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}' and upc is not NULL and goods_role in (1,2,4,0,3)"
    select_sql_02 = "select mch_goods_code from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}' and upc is NULL and goods_role=3"
    cursor_ai.execute(select_sql.format(uc_shopid,batch_id))
    all_data = cursor_ai.fetchall()
    cursor_ai.execute(select_sql_02.format(uc_shopid, batch_id))
    all_data_02 = cursor_ai.fetchall()
    conn_ai.close()
    tem = ""
    for data in all_data[:]:
        close_old_connections()
        conn_ucenter = connections['ucenter']
        cursor_ucenter = conn_ucenter.cursor()
        conn_dmstore = connections['dmstore']
        cursor_dmstore = conn_dmstore.cursor()
        # print('==================================================')
        # if not data[19] in [ 1, 3]:
        #     continue

        # print('data',data)
        "时间,门店id,门店名称,一级分类,二级分类,三级分类,配送类型,商品编码,商品名称,商品upc,策略标签,商品角色	,上品优先级排名,商品实际销售4周预期psd,商品实际销售4周预期psd金额,组内门店4周预期psd	组内门店4周预期psd金额	全店4周预期psd	全店4周预期psd金额"
        line_str = ""    # 一条记录
        line_str += str(data[12])  # 时间
        line_str += ","

        line_str += str(data[2])   #门店id
        line_str += ","

        shop_name_sql = "select shop_name from uc_shop a where id={}"
        # close_old_connections()
        cursor_ucenter.execute(shop_name_sql.format(uc_shopid))
        try:
            line_str += str(cursor_ucenter.fetchone()[0])   #门店名称
        except:
            line_str += str('None')  # 门店名称
        tem = line_str
        line_str += ","



        class_type_sql = "select display_first_cat_id,display_second_cat_id,display_third_cat_id,display_fourth_cat_id,delivery_type from uc_merchant_goods where mch_goods_code={} and width > 0"
        cursor_ucenter.execute(class_type_sql.format(data[10]))
        class_type_data_all = cursor_ucenter.fetchall()
        try:
            class_type_data = class_type_data_all[0]
            # print(i)
            if len(class_type_data_all) > 1:
                for d in class_type_data_all:
                    if d[0] != '0':
                        class_type_data = d
        except:
            class_type_data = None

        # class_type_sql = "SELECT DISTINCT first_cate_id,second_cate_id,third_cate_id from goods WHERE neighbor_goods_id ={} AND corp_id=2"
        # cursor_dmstore.execute(class_type_sql.format(data[10]))
        # class_type_data = cursor_dmstore.fetchone()
        # print('分类',data[10],class_type_data)
        try:
            line_str += str(class_type_data[0])  # 一级分类
            line_str += ","
        except:
            line_str += str('None')
            line_str += ","
        try:
            line_str += str(class_type_data[1])  # 二级分类
            line_str += ","
        except:
            line_str += str('None')
            line_str += ","
        try:
            line_str += str(class_type_data[2])  # 三级分类
            line_str += ","
        except:
            line_str += str('None')
            line_str += ","

        try:
            line_str += str(class_type_data[3])  # 四级分类
            line_str += ","
        except:
            line_str += str('None')
            line_str += ","

        delivery_type_sql = "select DISTINCT a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code where a.supplier_id = 1 and order_status = 1 AND supplier_goods_code={}"
        cursor_ucenter.execute(delivery_type_sql.format(data[10]))

        delivery_type_dict = {1:'日配',2:'非日配','1':'日配','2':'非日配'}
        try:
            delivery = cursor_ucenter.fetchone()[1]
            # print(data[21])
            # line_str += str(delivery_type_dict[data[21]])  # 配送类型
            line_str += str(delivery_type_dict[delivery])  # 配送类型
            line_str += ","
        except:
            line_str += str('None')
            line_str += ","

        line_str += str(data[10])  # 商品编码
        line_str += ","

        line_str += str(data[5])  # 商品名称
        line_str += ","

        line_str += str(data[4])  # 商品upc
        line_str += ","

        #策略标签
        which_strategy_dict = {0:'结构品',1:'畅销品',2:'关联品',3:'品库可定商品',4:'品谱选品',5:'决策树标签选品',6:'人工临时加品',7:'网红品'}
        # print('data[19]',data[19])
        # if data[19] == 1:
        try:
            if data[15] == 1:
                line_str += str(which_strategy_dict[0])  # 策略标签
            elif data[16] == 1:
                line_str += str(which_strategy_dict[1])  # 策略标签
            else:
                line_str += str('None')  # 策略标签
        except:
            line_str += str('None')  # 策略标签
        # else:
        #     line_str += str('None')  # 策略标签
        line_str += ","

        # 商品角色
        goods_role_dict = {0:'保护品',1:'必上',2:'必下',3:'可选上架',4:'可选下架'}
        if data[19] in [0,1,2,3,4]:
            try:
                line_str += str(goods_role_dict[data[19]])  # 商品角色
            except:
                line_str += str('None')  # 商品角色
        else:
            line_str += str('None')  # 商品角色
        line_str += ","

        # 上品优先级排名
        if data[19] == 3:
            try:
                line_str += str(data[14])  # 上品优先级排名
            except:
                line_str += str('None')  #上品优先级排名
        else:
            line_str += str('None')  # 上品优先级排名
        line_str += ","

        now = datetime.datetime.now()
        now_date = data[12]
        now = time.mktime(time.strptime(now_date, '%Y-%m-%d %H:%M:%S'))
        # now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        #商品实际销售4周预期psd,商品实际销售4周预期psd金额,组内门店4周预期psd	组内门店4周预期psd金额	全店4周预期psd	全店4周预期psd金额
        psd_sql = "select sum(p.amount),g.first_cate_id,g.second_cate_id,g.third_cate_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id ={} and g.neighbor_goods_id={};"
        # close_old_connections()
        cursor_dmstore.execute(psd_sql.format(week_ago,now_date,data[1],data[10]))
        print(psd_sql.format(week_ago,now_date,data[1],data[10]))
        psd_data = cursor_dmstore.fetchone()
        # print('psd_data',psd_data)
        if psd_data[0]:
            line_str += str(psd_data[0]/days)  # psd金额
            line_str += ","
            try:
                line_str += str(psd_data[0] / (days*psd_data[4]))  # psd
            except:
                line_str += str(0)  # psd
            line_str += ","
        else:
            line_str += str(0)  # psd金额
            line_str += ","
            line_str += str(0)  # psd
            line_str += ","

        psd_sql_shops = "select sum(p.amount), COUNT(DISTINCT shop_id),g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in {} and g.neighbor_goods_id={};"
        # close_old_connections()
        cursor_dmstore.execute(psd_sql_shops.format(week_ago,now_date,tuple(template_shop_ids.split(',')),data[10]))
        psd_data_shops = cursor_dmstore.fetchone()
        # print('psd_data_shops',psd_data_shops)
        if psd_data_shops[0]:
            line_str += str(psd_data_shops[0] / (days * psd_data_shops[1]))  # psd金额,同组
            line_str += ","
            try:
                line_str += str(psd_data_shops[0] / (days * psd_data_shops[1] * psd_data_shops[2]))  # psd,同组
            except:
                line_str += str(0)
            # line_str += ","
        else:
            line_str += str(0)  # psd金额,同组
            line_str += ","
            line_str += str(0)  # psd,同组
            # line_str += ","
        print(line_str)
        conn_ucenter.close()
        conn_dmstore.close()





    tem_mch_list = [i[0] for i in all_data_02]
    conn_ucenter = connections['ucenter']
    cursor_ucenter = conn_ucenter.cursor()

    sql2 = "SELECT mch_goods_code,upc ,goods_name,display_first_cat_id,display_second_cat_id,display_third_cat_id,display_fourth_cat_id,delivery_type from uc_merchant_goods where mch_goods_code ={}"
    # d = cursor_ucenter.fetchall()
    # print("订货0的mch的len", len(tem_mch_list))
    # print("订货0的len", len(d))

    for t in tem_mch_list[:]:
        try:
            cursor_ucenter.execute(sql2.format(t))
            data = cursor_ucenter.fetchall()
            i = data[0]
            # print(i)
            if len(data) > 1:
                for d in data:
                    if d[3] != '0':
                        i = d

            delivery_type_sql = "select DISTINCT a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code where a.supplier_id = 1 and order_status = 1 AND supplier_goods_code={}"
            cursor_ucenter.execute(delivery_type_sql.format(t))
            delivery_type_dict = {1: '日配', 2: '非日配', '1': '日配', '2': '非日配'}
            delivery_str = ''
            try:
                delivery = cursor_ucenter.fetchone()[1]
                delivery_str = str(delivery_type_dict[delivery])  # 配送类型
            except:
                delivery_str = str('None')


            print("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(tem, i[3], i[4], i[5], i[6], delivery_str, i[0],
                                                                           i[2], i[1], None, '可选上架', 0, None, None, None,
                                                                           None))
        except:
            continue
    conn_ucenter.close()





def data():
    pass
    # 结构品 = [0, 2021662, 2004083, 2043574, 2004998, 2004092, 2017999, 2045738, 2043718, 2021662, 2043551, 2019634, 2028665, 2031364, 2028203, 2042847, 2026210, 2041895, 2043896, 2014305, 2018177, 2034119, 2036442, 2037002, 2033756, 2044177, 2019972, 2032906, 2030866, 2026853, 2042505, 2033732, 2031718, 2045071, 2035555, 2045080, 2025103, 2035517, 2038948, 2004998, 2004476, 2043271, 2026210, 2023591, 2004353, 2043574, 2041510, 2045071, 2018800, 2030321, 2043025, 2032250, 2045001, 2045683, 2017286, 2032722, 2044726, 2041737, 2006927, 2044986, 2035742, 2017996, 2035037, 2018602, 2035958, 2026654, 2028935, 2036239, 2013136, 0, 2027750, 2022387, 2045611, 2044756, 2022531, 2036395, 2045296, 2040681, 2043569, 2018512, 2025479, 2027368, 2036446, 2034807, 2040996, 2041042, 2043303, 2023289, 2044754, 2046305, 2034603, 2045403, 2033756, 2045054, 2042847, 2023428, 2044026, 2040792, 2022531, 2004828, 2005413, 2034639, 2034566, 2043957, 2043972, 2044031, 2016445, 2009647, 2026654, 2005413, 2027345, 2009669, 2034603, 2022602, 2040681, 2027710, 2037196, 2034207, 2036691, 2017661, 2043956, 2044623, 2044127, 2042676, 2044732, 2043892, 2040764, 2044699, 2036395, 2026853, 2045084, 2042010, 2029277, 2004377, 2036717, 2035814, 2045235, 2034566, 2025105, 2038523, 2032104, 2044789, 2037707, 2045684, 2045508, 2044123, 2034697, 2013793, 2044854, 2042407, 2003963, 2023577, 2035115, 2024892, 2043255, 2036418, 2027602, 2031200, 2043405, 2023041, 2004642, 2013854, 2042689, 2034544, 2040891, 2028383, 2045014, 2044880, 2009628, 2038203, 2037979, 2040260, 2036446, 2014174, 2044091, 2045025, 2041250, 2021927, 2042874, 2035177, 2021143, 2022260, 2044460, 2035576, 2029958, 2035738, 2043612, 2014005, 2040878, 2043577, 2028823, 2017986, 2040875, 2044579, 2021143, 2041242, 2006922, 2045343, 2025696, 2045233, 2009286, 2038523, 2045335, 2036732, 2041833, 2044907, 2043317, 2042780, 2044580, 2045156, 2035489, 2043992, 2044197, 2044790, 2032104, 2035740, 2035958, 2028082, 2043144, 2044481, 2037786, 2045385, 2044789, 2037785, 2037979, 2009288, 2036938, 2034812, 2020598, 2044674, 2017511, 2044154, 2044437, 2032896, 2042392, 2031759, 2045277, 2017511, 2013787, 2045234, 2032527, 2044154, 2019197, 2045063, 2044711, 2045611, 2043662, 2042776, 2043254, 2037212, 2036500, 2024836, 2018964, 2044727, 2036646, 2019463, 2004638, 2042780, 2045695, 2032904, 2043613, 2045358, 2045169, 2029310, 2027479, 2044359, 2032284, 2040512, 2010834, 2037743, 2035177, 2045385, 2039612, 2013981, 2035865, 2014422, 2040947, 2013507, 2034101, 2044954, 2040953, 2036542, 2043759, 2032284, 2039612, 2032125, 2019629, 2023634, 2039955, 2044359, 2020615, 2032904, 2028495, 0]
    # 畅销品 = [0, 2042696, 2045321, 2008982, 2045803, 2045322, 0, 2043917, 2026470, 2042707, 2043897, 2023591, 2037283, 2042356, 2045807, 2043893, 2043815, 2043892, 2044866, 2043895, 2026471, 2036600, 2043546, 2028200, 2036441, 2018602, 2017307, 2034633, 2045590, 2042336, 2043814, 2037110, 2038689, 2042444, 2026253, 2037523, 2042496, 2028201, 2044994, 0, 2038960, 2045005, 2004134, 2037109, 2043249, 2026646, 2034697, 2004326, 2044033, 2017293, 2020054, 2035960, 2043552, 2025102, 2042337, 2038589, 2019634, 2036329, 2043553, 2026864, 2034688, 2035797, 2045594, 2038325, 2037064, 2042444, 2040128, 2036938, 2021612, 2044988, 2037513, 2032527, 2043658, 2037993, 2035961, 2033601, 2044032, 2041535, 0, 2032934, 0, 2035725, 2030716, 2045702, 2044583, 0, 2040893, 2040122, 2037196, 2043256, 2018133, 0, 2034519, 2043297, 2025104, 2043150, 2045483, 2045736, 2003228, 2017999, 2045365, 2022539, 2025909, 2041511, 2044596, 2039261, 2044417, 2045403, 2045802, 2039587, 2033770, 2033770, 2045800, 0, 2044757, 2025107, 2045351, 2020054, 2045500, 0, 2046513, 2041824, 2026864, 2045519, 0, 2041180, 0, 0, 0, 2043302, 2022532, 2041284, 2040272, 2034554, 0, 2041275, 2037777, 2003280, 2043902, 2045555, 2045533, 2045041, 0, 2045520, 2045006, 2032659, 0, 2026660, 2031641, 2014904, 2041201, 2011038, 2037750, 2044452, 2045294, 2045108, 2019442, 2022388, 2044182, 2031227, 2028492, 2031718, 2042009, 2034633, 2045482, 2045532, 2045319, 2026656, 2041200, 0, 2044756, 2021478, 2042990, 2042612, 2022386, 0, 2040323, 2044879, 2044416, 0, 2039050, 2044196, 2034859, 2043315, 2045521, 2045554, 2009198, 2036994, 2012543, 2019441, 2036716, 2034860, 2038952, 2045680, 2045405, 2043224, 2040139, 2036068, 2022385, 2036692, 2045000, 2032918, 2042838, 2025102, 2039096, 2035037, 2023287, 2045495, 2042008, 2043518, 2031759, 0, 0, 0, 2044138, 2044671, 2043223, 0, 0, 2034357, 2046472, 2046513, 2017660, 2040684, 2042675, 0, 2044695, 2021918, 2017661, 2045740, 2006295, 2030305, 2045260, 2044414, 2012716, 2042007, 2044123, 0, 2032689, 2044072, 2034544, 2038276, 2037778, 2040323, 2036691, 0, 2044731, 2040141, 2017400, 2044180, 2029278, 2028397, 2044757, 2036067, 2036996, 2044530, 2022292, 2017286, 2039502, 0, 2043139, 2028665, 2036958, 2017660, 2027019, 2036692, 2009137, 2045618, 2044074, 2027020, 0, 0, 2043842, 2044177, 2044176, 2045738, 2004134, 0, 2042007, 2044875, 2041923, 2039585, 2019518, 2028741, 0, 2045470, 2045429, 2036690, 2036690, 2045608, 2028900, 2042698, 2038708, 2033434, 2044412, 2044196, 0, 0, 0, 2028065, 2018380, 2006312, 0, 2027601, 2044129, 2034844, 2030304, 0, 2028719, 2040140, 2006295, 2045493, 2040620, 0, 0, 2039188, 0, 2038325, 2044571, 2044649, 2038322, 0, 0, 2046434, 2022539, 0, 2045807, 2023621, 2028227, 2045614, 2016125, 2024836, 2043121, 0, 2034280, 2006326, 2038978, 0, 2044193, 2045245, 2044195, 2044699, 2045296, 2041871, 2039101, 2046582, 2023577, 2043122, 2045254, 2027711, 2044780, 2037493, 2044622, 2032586, 0, 2045013, 0, 2044483, 2035074, 0, 2044174, 0, 2045043, 2040661, 2044619, 0, 2032255, 2043569, 2045740, 2042860, 2032590, 2044173, 2045246, 2043958, 2044289, 2045400, 2038489, 2036716, 2045298, 2039082, 2039161, 2039160, 2045735, 2045688, 2041094, 2045699, 2044193, 0, 2045821, 2034286, 2035935, 2009137, 2029094, 2043758, 2034283, 0, 0, 0, 2037986, 0, 0, 0, 2012543, 2034209, 2035625, 2041005, 2045333, 2036067, 2044953, 2017293, 2033386, 2037233, 0, 2045045, 2045482, 2036068, 2045512, 2046617, 0, 0, 2044451, 2037533, 2046586, 0, 2045703, 2042337, 2031205, 0, 2027602, 2038707, 2045534, 2027601, 2044698, 2043297, 0, 0, 0, 2027203, 2017307, 0, 2037978, 0, 2045313, 0, 2043552, 2035797, 2045301, 2036120, 2032140, 2040648, 2045326, 2036908, 2045734, 0, 2045604, 2041517, 2040111, 2034207, 2039102, 0, 2039192, 2031460, 0, 2042498, 2031740, 2044604, 2039100, 0, 2042614, 2042777, 0, 0, 2022615, 0, 2039058, 2045609, 0, 2045021, 0, 2033611, 2040647, 0, 2013629, 2033362, 2044451, 2044880, 0, 2045352, 2026686, 2036996, 0, 2045051, 2035885, 2039601, 0, 2044856, 2040664, 2045398, 2046509, 2036162, 2044450, 2031641, 2045044, 2037114, 2022457, 2028720, 0, 2046583, 2044603, 2009628, 0, 2032255, 2019441, 2044012, 2036239, 2019444, 2044904, 2009628, 2033398, 2042238, 2028820, 2028818, 2036733, 2045013, 2044577, 2044904, 2036163, 2021490, 2044191, 2045020, 2033373, 2014521, 2028083, 2045383, 2041835, 2042491, 2023329, 2036734, 2044387, 2011017, 2005993, 2041833, 2040047, 2044158, 2044010, 2044160, 2040071, 2031206, 2036540, 2045601, 2044168, 2006304, 2016771, 2026431, 2004828, 2017678, 2028703, 2037482, 2009628, 2025328, 2040047, 2043139, 2018964, 2014904, 2024892, 2044913, 2042712, 2032589, 2040793, 2044761, 2043680, 2034287, 2032590, 2034280, 2034843, 2032586, 2033611, 2034844, 2045766, 2045761, 2017678, 2045770]

if __name__ == '__main__':
    goods_out(806,"1284,3955,3779,1925,4076,1924,3598",'lishu_test_006',28)






