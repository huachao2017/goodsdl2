





import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections





conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
cursor = conn.cursor()
sql = "select sum(p.amount),g.upc,g.first_cate_id,g.second_cate_id,g.third_cate_id,g.neighbor_goods_id,g.price,p.name,COUNT(DISTINCT p.shop_id) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '2019-11-20' and p.create_time < '2019-12-20' and p.shop_id in (3955,3779,1925,4076,1924) group by g.upc order by sum(p.amount) desc"

cursor.execute(sql)
data = cursor.fetchall()
temp = []
for i in data:
    temp.append(i[5])

print(temp)




