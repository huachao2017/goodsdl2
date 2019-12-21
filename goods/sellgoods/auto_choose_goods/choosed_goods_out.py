

# 输出选品结果给运营angela查看


import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections


def goods_out(uc_shopid,template_shop_ids,batch_id,days):
    """
    输出选品结果给运营angela查看
    :return:
    """
    conn_ucenter = connections['ucenter']
    cursor_ucenter = conn_ucenter.cursor()
    conn_ai = connections['default']
    cursor_ai = conn_ai.cursor()
    conn_dmstore = connections['dmstore']
    cursor_dmstore = conn_dmstore.cursor()
    print("时间,门店id,门店名称,一级分类,二级分类,三级分类,配送类型,商品编码,商品名称,商品upc,策略标签,商品角色,上品优先级排名,商品实际销售4周预期psd金额,商品实际销售4周预期psd,组内门店4周预期psd金额,组内门店4周预期psd")


    select_sql = "select * from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}'"
    cursor_ai.execute(select_sql.format(uc_shopid,batch_id))
    all_data = cursor_ai.fetchall()
    for data in all_data[:]:
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
        cursor_ucenter.execute(shop_name_sql.format(uc_shopid))
        try:
            line_str += str(cursor_ucenter.fetchone()[0])   #门店名称
        except:
            line_str += str('None')  # 门店名称
        line_str += ","

        class_type_sql = "select category1_id,category2_id,category_id,delivery_type from uc_merchant_goods a where mch_goods_code={} and delivery_type is not Null"
        cursor_ucenter.execute(class_type_sql.format(data[10]))
        class_type_data = cursor_ucenter.fetchone()
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
        delivery_type_dict = {1:'日配',2:'非日配','1':'日配','2':'非日配'}
        try:
            line_str += str(delivery_type_dict[class_type_data[3]])  # 配送类型
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
        if data[19] == 1:
            try:
                line_str += str(which_strategy_dict[data[20]])  # 策略标签
            except:
                line_str += str('None')  # 策略标签
        else:
            line_str += str('None')  # 策略标签
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
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        #商品实际销售4周预期psd,商品实际销售4周预期psd金额,组内门店4周预期psd	组内门店4周预期psd金额	全店4周预期psd	全店4周预期psd金额
        psd_sql = "select sum(p.amount),g.first_cate_id,g.second_cate_id,g.third_cate_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id ={} and g.neighbor_goods_id={};"
        cursor_dmstore.execute(psd_sql.format(week_ago,now_date,data[1],data[10]))
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
        cursor_dmstore.execute(psd_sql_shops.format(week_ago,now_date,tuple(template_shop_ids.split(',')),data[10]))
        psd_data_shops = cursor_dmstore.fetchone()
        # print('psd_data_shops',psd_data_shops)
        if psd_data_shops[0]:
            line_str += str(psd_data_shops[0] / days)  # psd金额,同组
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

if __name__ == '__main__':
    goods_out(806,"1284,3955,3779,1925,4076,1924,3598",'lishu_test_003',28)






