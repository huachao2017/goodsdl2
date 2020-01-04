import time
import datetime
import os
import django
import main.import_django_settings
from django.db import connections
from django.db import close_old_connections
class SalesCol:
    shop_id = None
    goods_id = None
    upc = None
    goods_name = None
    price = None
    city = None
    city_id = None
    create_date = None
    week_date = None
    first_cate_id = None
    second_cate_id = None
    third_cate_id = None
    weather_type = None
    temphigh = None
    templow = None
    windspeed = None
    winddirect = None
    windpower = None
    holiday_type = None
    num = None



shop_ids = "1284,3955,3779,1925,4076,1924,3598"
days_num = 400
class SalesPredict:
    def generate_data(self):
        close_old_connections()
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        start_date = str(
            (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                days=-days_num)).strftime("%Y-%m-%d"))
        sql1 = "select T.shop_id,T.goods_id,T3.num,T3.create_date,shop.owned_city,goods.price,goods.`name`,goods.first_cate_id,goods.second_cate_id,goods.third_cate_id  from (select shop_id,goods_id from shop_goods where status = 10 and shop_id in ({}) and stock >=0 group by shop_id,goods_id) T LEFT JOIN (SELECT T2.shop_id,T2.goods_id,SUM(T2.number) as num,T2.create_date,DAYOFWEEK(DATE_FORMAT(from_unixtime(unix_timestamp(DATE_FORMAT(T2.create_date ,'%Y-%m-%d'))-24*3600),'%Y-%m-%d')) as week_date from "\
               "(select T1.shop_id,T1.goods_id,T1.number,DATE_FORMAT(T1.create_time,'%Y-%m-%d') as create_date from ( "\
               "select shop_id,goods_id,create_time,number,price from payment_detail where create_time >= '{} 00:00:00' and create_time <= '{} 23:59:59' and shop_id in ({}) and payment_id in ( "\
               "select distinct(payment.id) from payment where payment.status = 10 and shop_id in ({}) and create_time >= '{} 00:00:00' and create_time <= '{} 23:59:59' "\
               ") "\
               ") T1 "\
               ") T2 GROUP BY T2.shop_id,T2.goods_id,T2.create_date ) T3 on T.goods_id = T3.goods_id and T.shop_id = T3.shop_id left JOIN shop on T.shop_id = shop.id LEFT JOIN goods on T.goods_id = goods.id where goods.upc is not NULL"
        sql1 = sql1.format(shop_ids,start_date,end_date,shop_ids,shop_ids,start_date,end_date)
        sql2 = "select T.shop_id,T.goods_id,shop.owned_city,goods.price,goods.`name`,goods.upc,goods.first_cate_id,goods.second_cate_id,goods.third_cate_id  from (select shop_id,goods_id from shop_goods where status = 10 and shop_id in ({}) and stock >=0 group by shop_id,goods_id) T left JOIN shop on T.shop_id = shop.id LEFT JOIN goods on T.goods_id = goods.id where goods.upc is not NULL"
        sql2 = sql2.format(shop_ids)
        sql3 = "select day,type from goods_ai_holiday"
        sql4 = "select city,create_date,weather_type,temphigh,templow,windspeed,winddirect,windpower,city_id from goods_ai_weather where create_date >= '{0}' and create_date <= '{1}' order by create_date asc "
        sql4 = sql4.format(start_date, end_date)
        sql1_dict =  self.process_sql1(sql1)

        sql2_list = self.process_sql2(sql2)

        sql3_dict = self.process_sql3(sql3)

        sql4_dict = self.process_sql4(sql4)

        sc_inss = self.process_data(sql1_dict,sql2_list,sql3_dict,sql4_dict)

        with open('sales_train.CSV','w') as f:
            f.write("shop_id,goods_id,upc,goods_name,price,city,city_id,create_date,week_date,first_cate_id,second_cate_id,third_cate_id,weather_type,temphigh,templow,windspeed,winddirect,windpower,holiday_type,num")
            f.write("\n")
            for sc_ins in sc_inss:
                sc_str = ("{},{},{},{},{},{},{},{},{},{},"
                          "{},{},{},{},{},{},{},{},{},{}".format(
                    sc_ins.shop_id,
                    sc_ins.goods_id,
                    sc_ins.upc,
                    sc_ins.goods_name,
                    sc_ins.price,
                    sc_ins.city,
                    sc_ins.city_id,
                    sc_ins.create_date,
                    sc_ins.week_date,
                    sc_ins.first_cate_id,
                    sc_ins.second_cate_id,
                    sc_ins.third_cate_id,
                    sc_ins.weather_type,
                    sc_ins.temphigh,
                    sc_ins.templow,
                    sc_ins.windspeed,
                    sc_ins.winddirect,
                    sc_ins.windpower,
                    sc_ins.holiday_type,
                    sc_ins.num
                ))
                f.write(sc_str)
                f.write("\n")




    def process_data(self,sql1_dict,sql2_list,sql3_dict,sql4_dict):
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        start_date = str(
            (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                days=-days_num)).strftime("%Y-%m-%d"))
        for sc_ins in sql2_list:
            for i in range(days_num):
                create_date = str(
                (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(
                days=i)).strftime("%Y-%m-%d"))
                week_date = datetime.datetime.strptime(create_date, "%Y-%m-%d").weekday() + 1
                sc_ins.create_date = create_date
                sc_ins.week_date = week_date
                if create_date in sql3_dict.keys():
                    sc_ins.holiday_type = sql3_dict[create_date].holiday_type
                else:
                    sc_ins.holiday_type = 0

                key1 = str(sc_ins.shop_id)+"_"+str(sc_ins.goods_id)+"_"+str(sc_ins.create_date)
                if key1 in sql1_dict.keys():
                    sc_ins.num = sql1_dict[key1].num
                else:
                    sc_ins.num = 0

                key2 = str(sc_ins.city)+"_"+str(sc_ins.create_date)
                if key2 in sql4_dict.keys():
                    sc_ins.weather_type = sql4_dict[key2].weather_type
                    sc_ins.temphigh = sql4_dict[key2].temphigh
                    sc_ins.templow = sql4_dict[key2].templow
                    sc_ins.windspeed = sql4_dict[key2].windspeed
                    sc_ins.winddirect = sql4_dict[key2].winddirect
                    sc_ins.windpower = sql4_dict[key2].windpower
                    sc_ins.city_id = sql4_dict[key2].city_id
                else:
                    sc_ins.weather_type = ''
                    sc_ins.temphigh = 0
                    sc_ins.templow = 0
                    sc_ins.windspeed = 0
                    sc_ins.winddirect = ''
                    sc_ins.windpower = 0
                    sc_ins.city_id = 0
        return sql2_list
    def process_sql1(self,sql1):
        print ("sql1......")
        conn_dmstore = connections['dmstore']
        cursor_dmstore = conn_dmstore.cursor()
        cursor_dmstore.execute(sql1)
        results = cursor_dmstore.fetchall()
        sql1_dict = {}
        for row in results:
            sc_ins = SalesCol()
            shop_id = row[0]
            goods_id = row[1]
            num = row[2]
            create_date = str(row[3])
            sc_ins.shop_id = shop_id
            sc_ins.goods_id = goods_id
            sc_ins.num = num
            sc_ins.create_date = create_date
            sql1_dict[str(shop_id)+"_"+str(goods_id)+"_"+str(create_date)] = sc_ins
        cursor_dmstore.close()
        conn_dmstore.close()
        return sql1_dict

    def process_sql2(self,sql2):
        print ("sql2......")
        conn_dmstore = connections['dmstore']
        cursor_dmstore = conn_dmstore.cursor()
        cursor_dmstore.execute(sql2)
        results = cursor_dmstore.fetchall()
        sql2_list = []
        for row in results:
            sc_ins = SalesCol()
            sc_ins.shop_id = row[0]
            sc_ins.goods_id = row[1]
            sc_ins.city = row[2]
            if row[2] is not None and row[2] != '':
                if row[2]  == '天津新区':
                    row[2] = '天津'
                sc_ins.city = str(row[2]).strip("市")
            sc_ins.price = row[3]
            sc_ins.goods_name = row[4]
            sc_ins.upc = row[5]
            sc_ins.first_cate_id = row[6]
            sc_ins.second_cate_id = row[7]
            sc_ins.third_cate_id = row[8]
            sql2_list.append(sc_ins)
        cursor_dmstore.close()
        conn_dmstore.close()
        return sql2_list

    def process_sql3(self,sql3):
        print ("sql3......")
        conn_ai = connections['default']
        cursor_ai = conn_ai.cursor()
        cursor_ai.execute(sql3)
        results = cursor_ai.fetchall()
        sql3_dict = {}
        for row in results:
            sc_ins = SalesCol()
            sc_ins.create_date = row[0]
            sc_ins.holiday_type = row[1]
            sql3_dict[sc_ins.create_date] = sc_ins
        cursor_ai.close()
        conn_ai.close()
        return sql3_dict

    def process_sql4(self,sql4):
        print ("sql4......")
        conn_ai = connections['default']
        cursor_ai = conn_ai.cursor()
        cursor_ai.execute(sql4)
        results = cursor_ai.fetchall()
        sql4_dict = {}
        for row in results:
            sc_ins = SalesCol()
            sc_ins.city = row[0]
            sc_ins.create_date = row[1]
            sc_ins.weather_type = row[2]
            temphigh = row[3]
            try:
                if temphigh is None or temphigh == '' or temphigh == 'NULL':
                    temphigh = 0
                else:
                    temphigh = float(str(temphigh).strip("℃"))
            except:
                temphigh = 0
            sc_ins.temphigh = temphigh

            templow = row[4]
            try:
                if templow is None or templow == '' or templow == 'NULL':
                    templow = 0
                else:
                    templow = float(str(templow).strip("℃"))
            except:
                templow = 0
            sc_ins.templow = templow

            windspeed = row[5]
            try:
                if windspeed is None or windspeed == '' or windspeed == 'NULL':
                    windspeed = 0
                else:
                    windspeed = float(str(windspeed))
            except:
                windspeed = 0
            sc_ins.windspeed = windspeed

            sc_ins.winddirect = row[6]

            windpower = row[7]
            try:
                if windpower is None or windpower == '' or windpower == 'NULL':
                    windpower = 0
                else:
                    windpower = float(str(windspeed).strip("级"))
            except:
                windpower = 0
            sc_ins.windpower = windpower
            sc_ins.city_id = row[8]
            sql4_dict[str(sc_ins.city)+"_"+str(sc_ins.create_date)] = sc_ins
        cursor_ai.close()
        conn_ai.close()
        return sql4_dict

if __name__=='__main__':
    sp_ins = SalesPredict()
    sp_ins.generate_data()

