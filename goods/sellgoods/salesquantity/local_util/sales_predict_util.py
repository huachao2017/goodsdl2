import time
import datetime
from goods.sellgoods.salesquantity.utils import mysql_util
from set_config import config
ai = config.ai
erp = config.erp

from goods.sellgoods.salesquantity.bean import goods_ai_weather,ai_sales_old,sales_old_tmp
class SalesPredict:
    def generate_data(self,all_data=False):
        sql1 = "select T3.shop_id,T3.goods_id,T3.num,shop.owned_city,T3.create_date,goods.upc,goods.`name`,goods.price,goods.first_cate_id,goods.second_cate_id,goods.third_cate_id from ( " \
               "SELECT T2.shop_id,T2.goods_id,SUM(T2.number) as num,T2.create_date from " \
               "(select T1.shop_id,T1.goods_id,T1.number,DATE_FORMAT(T1.create_time,'%Y-%m-%d') as create_date from ( " \
               "select shop_id,goods_id,create_time,number,price from payment_detail where shop_id = 1284 and create_time >= '{0} 00:00:00' and create_time <= '{1} 23:59:59' and payment_id in ( " \
               "select distinct(payment.id) from payment where shop_id = 1284 and payment.type != 50  and create_time >= '{2} 00:00:00' and create_time <= '{3} 23:59:59' " \
               ") " \
               ") T1 " \
               ") T2 GROUP BY T2.shop_id,T2.goods_id,T2.create_date " \
               ") T3 LEFT JOIN shop on T3.shop_id = shop.id LEFT JOIN goods on goods.id = T3.goods_id where T3.shop_id is not NUlL and goods.upc is not NULL "

        salesold_inss = []

        if all_data:
            end_time2 = '2019-03-04'
            for i in range(1,70):
                week_days1 = self.get_date(i)
                week_days2 = self.get_date(11+i)
                if end_time2 in week_days1:
                    return
                else:
                    results = self.get_weeks_results(sql1)
                    salesold_inss = self.get_data_week(results, week_days1, week_days2)

        else:
            week_days1 = self.get_date(1)
            week_days2 = self.get_date(4)
            results = self.get_weeks_results(sql1)
            salesold_inss = self.get_data_week(results,week_days1,week_days2)
        return salesold_inss


    def get_weeks_results(self,sql1):
        mysql_ins = mysql_util.MysqlUtil(erp)
        resultss = []
        for i in range(1,13):
            week_days1 = self.get_date(i)
            start_time = week_days1[0]
            end_time = week_days1[-1]
            sql1 = sql1.format(start_time, end_time, start_time, end_time)
            results = mysql_ins.selectAll(sql1)
            resultss.extend(list(results))
        return resultss


    def get_weather(self,week_days1,results1,results2):
        mysql_ins = mysql_util.MysqlUtil(ai)

        # if city is None or city == '':
        #     return None
        #
        # if city == '天津新区':
        #     city = '天津'
        # city = str(city).strip("市")
        sql2 = "select * from goods_ai_weather where create_date >= '{0}' and create_date <= '{1}' order by create_date asc "
        sql2 = sql2.format(week_days1[0],week_days1[-1])
        results = mysql_ins.selectAll(sql2)
        weather_week = {}
        for row in list(results):
            weather_ins = goods_ai_weather.GoodsAiWeather()
            weather_ins.city = row[1]
            weather_ins.weather_type = row[2]
            weather_ins.temphigh = row[3]
            weather_ins.templow = row[4]
            weather_ins.windspeed = row[5]
            weather_ins.winddirect = row[6]
            weather_ins.windpower = row[7]
            weather_ins.city_id = row[8]
            if weather_ins.weather_type is None or  weather_ins.weather_type == '':
                weather_ins.weather_type = 0
            else:
                weather_ins.weather_type = list(results1).index( weather_ins.weather_type)

            if weather_ins.temphigh is None or weather_ins.temphigh == '':
                weather_ins.temphigh = 0
            else:
                weather_ins.temphigh = str(weather_ins.temphigh).strip("℃")

            if weather_ins.templow is None or weather_ins.templow == '':
                weather_ins.templow = 0
            else:
                weather_ins.templow = str(weather_ins.templow).strip("℃")

            if weather_ins.windspeed is None or weather_ins.windspeed == '':
                weather_ins.windspeed = 0
            else:
                weather_ins.windspeed = float(weather_ins.windspeed)

            if weather_ins.winddirect is None or weather_ins.winddirect == '':
                weather_ins.winddirect = 0
            else:
                weather_ins.winddirect =list(results2).index(weather_ins.winddirect)

            if weather_ins.windpower is None or weather_ins.windpower == '':
                weather_ins.windpower = 0
            else:
                weather_ins.windpower = str(weather_ins.windpower).strip("级")
            weather_week[weather_ins.city+"_"+weather_ins.create_date] = weather_ins
        return weather_week


    def get_data_week(self,results,week_days1,week_days2):
        """
        获取某段时间内的销量数据
        :param results:
        :return:
        """
        salesold_inss = []
        sales_old_tmp_dict = {}
        for row in list(results):
            self.weekdata_row_2_salesoldtmp(sales_old_tmp_dict,row)

        mysql_ins = mysql_util.MysqlUtil(ai)
        sql3 = "select distinct(weather_type) from goods_ai_weather"
        results1 = mysql_ins.selectAll(sql3)

        sql4 = "select distinct(winddirect) from goods_ai_weather"
        results2 = mysql_ins.selectAll(sql4)

        sql5 = "select day,type from goods_ai_holiday"
        results3 = mysql_ins.selectAll(sql5)


        for key in sales_old_tmp_dict:
            sales_old_ins = ai_sales_old.SalesOld()
            # 添加基础维度 和 地域维度
            self.add_baseinfo(sales_old_ins,sales_old_tmp_dict[key])
            # 添加天气维度
            self.add_weather(sales_old_ins,week_days1,results1,results2)
            # 添加时间维度
            self.add_time(sales_old_ins, week_days1,results3)
            # 添加销量统计维度
            self.add_sales_count(sales_old_ins,sales_old_tmp_dict[key],week_days1)
            salesold_inss.append(sales_old_ins)
        return salesold_inss
    def add_sales_count(self,sales_old_ins,sales_old_tmp_ins,week_days1):
        self.add_week_i_sales(sales_old_ins,sales_old_tmp_ins,week_days1)
        self.add_week_i_avg(sales_old_ins,sales_old_tmp_ins,week_days1)
        self.add_week_avg_in_out(sales_old_ins, sales_old_tmp_ins)


    def add_week_avg_in_out(self,sales_old_ins,sales_old_tmp_ins):
        week_dates = []
        for i in range(1, 13):
            wd = self.get_date(i)
            week_dates.extend(wd)
        week_1 = week_dates[0:1 * 7]
        week_2 = week_dates[0:2 * 7]
        week_4 = week_dates[0:4 * 7]
        week_8 = week_dates[0:8 * 7]
        week_12 = week_dates[0:12 * 7]
        for day in sales_old_tmp_ins.date_nums.keys():
            if day in week_1 :
                if sales_old_tmp_ins.date_nums[day].week_type == 0:
                    sales_old_ins.sale_1week_avg_in = sales_old_ins.sale_1week_avg_in + sales_old_tmp_ins.date_nums[day].num
                else:
                    sales_old_ins.sale_1week_avg_out = sales_old_ins.sale_1week_avg_out + \
                                                      sales_old_tmp_ins.date_nums[day].num
            if day in week_2 :
                if sales_old_tmp_ins.date_nums[day].week_type == 0:
                    sales_old_ins.sale_2week_avg_in = sales_old_ins.sale_2week_avg_in + sales_old_tmp_ins.date_nums[day].num
                else:
                    sales_old_ins.sale_2week_avg_out = sales_old_ins.sale_2week_avg_out + \
                                                      sales_old_tmp_ins.date_nums[day].num

            if day in week_4 :
                if sales_old_tmp_ins.date_nums[day].week_type == 0:
                    sales_old_ins.sale_4week_avg_in = sales_old_ins.sale_4week_avg_in + sales_old_tmp_ins.date_nums[day].num
                else:
                    sales_old_ins.sale_4week_avg_out = sales_old_ins.sale_4week_avg_out + \
                                                      sales_old_tmp_ins.date_nums[day].num

            if day in week_8 :
                if sales_old_tmp_ins.date_nums[day].week_type == 0:
                    sales_old_ins.sale_8week_avg_in = sales_old_ins.sale_8week_avg_in + sales_old_tmp_ins.date_nums[day].num
                else:
                    sales_old_ins.sale_8week_avg_out = sales_old_ins.sale_8week_avg_out + \
                                                      sales_old_tmp_ins.date_nums[day].num

            if day in week_12 :
                if sales_old_tmp_ins.date_nums[day].week_type == 0:
                    sales_old_ins.sale_12week_avg_in = sales_old_ins.sale_12week_avg_in + sales_old_tmp_ins.date_nums[day].num
                else:
                    sales_old_ins.sale_12week_avg_out = sales_old_ins.sale_12week_avg_out + \
                                                      sales_old_tmp_ins.date_nums[day].num

        sales_old_ins.sale_1week_avg_in = float(sales_old_ins.sale_1week_avg_in / 5.0)
        sales_old_ins.sale_1week_avg_out =  float(sales_old_ins.sale_1week_avg_out / 2.0)
        sales_old_ins.sale_2week_avg_in = float(sales_old_ins.sale_2week_avg_in / 10.0)
        sales_old_ins.sale_2week_avg_out = float(sales_old_ins.sale_2week_avg_out / 4.0)
        sales_old_ins.sale_4week_avg_in = float(sales_old_ins.sale_4week_avg_in / 20.0)
        sales_old_ins.sale_4week_avg_out = float(sales_old_ins.sale_4week_avg_out / 8.0)
        sales_old_ins.sale_8week_avg_in = float(sales_old_ins.sale_8week_avg_in / 40.0)
        sales_old_ins.sale_8week_avg_out = float(sales_old_ins.sale_8week_avg_out / 16.0)
        sales_old_ins.sale_12week_avg_in = float(sales_old_ins.sale_12week_avg_in / 60.0)
        sales_old_ins.sale_12week_avg_out = float(sales_old_ins.sale_12week_avg_out / 24.0)


    def add_week_i_sales(self,sales_old_ins,sales_old_tmp_ins,week_days1):
        for day,i in zip(week_days1,range(len(week_days1))):
            if day in sales_old_tmp_ins.date_nums.keys():
                if i == 0:
                    sales_old_ins.sale_1 = sales_old_tmp_ins.date_nums[day].num
                if i == 1:
                    sales_old_ins.sale_2 = sales_old_tmp_ins.date_nums[day].num
                if i == 2:
                    sales_old_ins.sale_3 = sales_old_tmp_ins.date_nums[day].num
                if i == 3:
                    sales_old_ins.sale_4 = sales_old_tmp_ins.date_nums[day].num
                if i == 4:
                    sales_old_ins.sale_5 = sales_old_tmp_ins.date_nums[day].num
                if i == 5:
                    sales_old_ins.sale_6 = sales_old_tmp_ins.date_nums[day].num
                if i == 6:
                    sales_old_ins.sale_7 = sales_old_tmp_ins.date_nums[day].num


    def add_week_i_avg(self,sales_old_ins,sales_old_tmp_ins,week_days1):
        week_dates = []
        for i in range(1, 13):
            wd = self.get_date(i)
            week_dates.extend(wd)
        week_1 = week_dates[0:1*7]
        week_2 = week_dates[0:2*7]
        week_4 = week_dates[0:4*7]
        week_8 = week_dates[0:8*7]
        week_12 = week_dates[0:12*7]
        for day, i in zip(week_days1, range(len(week_days1))):
            if day in sales_old_tmp_ins.date_nums.keys():
                for create_date in sales_old_tmp_ins.date_nums.keys():
                    j = datetime.datetime.strptime(create_date, "%Y-%m-%d").weekday()+1
                    if i == 0 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_1_2_avg = sales_old_ins.sale_1_2_avg + sales_old_tmp_ins.date_nums[create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_1_4_avg = sales_old_ins.sale_1_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_1_8_avg = sales_old_ins.sale_1_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_1_12_avg = sales_old_ins.sale_1_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num

                    if i == 1 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_2_2_avg = sales_old_ins.sale_2_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_2_4_avg = sales_old_ins.sale_2_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_2_8_avg = sales_old_ins.sale_2_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_2_12_avg = sales_old_ins.sale_2_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                    if i == 2 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_3_2_avg = sales_old_ins.sale_3_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_3_4_avg = sales_old_ins.sale_3_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_3_8_avg = sales_old_ins.sale_3_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_3_12_avg = sales_old_ins.sale_3_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                    if i == 3 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_4_2_avg = sales_old_ins.sale_4_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_4_4_avg = sales_old_ins.sale_4_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_4_8_avg = sales_old_ins.sale_4_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_4_12_avg = sales_old_ins.sale_4_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                    if i == 4 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_5_2_avg = sales_old_ins.sale_5_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_5_4_avg = sales_old_ins.sale_5_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_5_8_avg = sales_old_ins.sale_5_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_5_12_avg = sales_old_ins.sale_5_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                    if i == 5 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_6_2_avg = sales_old_ins.sale_6_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_6_4_avg = sales_old_ins.sale_6_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_6_8_avg = sales_old_ins.sale_6_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_6_12_avg = sales_old_ins.sale_6_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                    if i == 6 and j-1 == i:
                        if create_date in week_2:
                            sales_old_ins.sale_7_2_avg = sales_old_ins.sale_7_2_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_4:
                            sales_old_ins.sale_7_4_avg = sales_old_ins.sale_7_4_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_8:
                            sales_old_ins.sale_7_8_avg = sales_old_ins.sale_7_8_avg + sales_old_tmp_ins.date_nums[
                                create_date].num
                        if create_date in week_12:
                            sales_old_ins.sale_7_12_avg = sales_old_ins.sale_7_12_avg + sales_old_tmp_ins.date_nums[
                                create_date].num

        sales_old_ins.sale_1_2_avg = float(sales_old_ins.sale_1_2_avg / 2.0)
        sales_old_ins.sale_1_4_avg = float(sales_old_ins.sale_1_4_avg / 4.0)
        sales_old_ins.sale_1_8_avg = float(sales_old_ins.sale_1_4_avg / 8.0)
        sales_old_ins.sale_1_12_avg = float(sales_old_ins.sale_1_4_avg / 12.0)

        sales_old_ins.sale_2_2_avg = float(sales_old_ins.sale_2_2_avg / 2.0)
        sales_old_ins.sale_2_4_avg = float(sales_old_ins.sale_2_4_avg / 4.0)
        sales_old_ins.sale_2_8_avg = float(sales_old_ins.sale_2_8_avg / 8.0)
        sales_old_ins.sale_2_12_avg = float(sales_old_ins.sale_2_12_avg / 12.0)

        sales_old_ins.sale_3_2_avg = float(sales_old_ins.sale_3_2_avg / 2.0)
        sales_old_ins.sale_3_4_avg = float(sales_old_ins.sale_3_4_avg / 4.0)
        sales_old_ins.sale_3_8_avg = float(sales_old_ins.sale_3_8_avg / 8.0)
        sales_old_ins.sale_3_12_avg = float(sales_old_ins.sale_3_12_avg / 12.0)

        sales_old_ins.sale_4_2_avg = float(sales_old_ins.sale_4_2_avg / 2.0)
        sales_old_ins.sale_4_4_avg = float(sales_old_ins.sale_4_4_avg / 4.0)
        sales_old_ins.sale_4_8_avg = float(sales_old_ins.sale_4_8_avg / 8.0)
        sales_old_ins.sale_4_12_avg = float(sales_old_ins.sale_4_12_avg / 12.0)

        sales_old_ins.sale_5_2_avg = float(sales_old_ins.sale_5_2_avg / 2.0)
        sales_old_ins.sale_5_4_avg = float(sales_old_ins.sale_5_4_avg / 4.0)
        sales_old_ins.sale_5_8_avg = float(sales_old_ins.sale_5_8_avg / 8.0)
        sales_old_ins.sale_5_12_avg = float(sales_old_ins.sale_5_12_avg / 12.0)

        sales_old_ins.sale_6_2_avg = float(sales_old_ins.sale_6_2_avg / 2.0)
        sales_old_ins.sale_6_4_avg = float(sales_old_ins.sale_6_4_avg / 4.0)
        sales_old_ins.sale_6_8_avg = float(sales_old_ins.sale_6_8_avg / 8.0)
        sales_old_ins.sale_6_12_avg = float(sales_old_ins.sale_6_12_avg / 12.0)

        sales_old_ins.sale_7_2_avg = float(sales_old_ins.sale_7_2_avg / 2.0)
        sales_old_ins.sale_7_4_avg = float(sales_old_ins.sale_7_4_avg / 4.0)
        sales_old_ins.sale_7_8_avg = float(sales_old_ins.sale_7_8_avg / 8.0)
        sales_old_ins.sale_7_12_avg = float(sales_old_ins.sale_7_12_avg / 12.0)


    # TODO  改变sql 把good_id  聚合的维度信息 去掉 。 改为只基于upc 聚合的指标 。  price  goods_name 等信息 就会没有  待做.......

    def weekdata_row_2_salesoldtmp(self,sales_old_tmp_dict,row):
        shop_id = int(row[0])
        num = int(row[2])
        create_date = row[4]
        upc = row[5]
        if len(sales_old_tmp_dict.keys()) == 0:
            self.add_sales_old_tmp(row,sales_old_tmp_dict)
        else:
            if str(shop_id)+"_"+str(upc) in sales_old_tmp_dict.keys():
                if create_date in sales_old_tmp_dict[str(shop_id)+"_"+str(upc)].date_nums.keys():
                    sales_old_tmp_dict[str(shop_id) + "_" + str(upc)].date_nums[create_date].num = sales_old_tmp_dict[str(shop_id) + "_" + str(upc)].date_nums[create_date].num + num
                else:
                    datenum_ins = sales_old_tmp.DateNum()
                    datenum_ins.create_date = create_date
                    datenum_ins.num = num
                    datenum_ins.week_i = datetime.datetime.strptime(create_date, "%Y-%m-%d").weekday() + 1
                    if datenum_ins.week_i <= 5:
                        datenum_ins.week_type = 0
                    else:
                        datenum_ins.week_type = 1
                    sales_old_tmp_dict[str(shop_id) + "_" + str(upc)].date_nums[create_date] = datenum_ins
            else:
                self.add_sales_old_tmp(row, sales_old_tmp_dict)

    def add_sales_old_tmp(self,row,sales_old_tmp_dict):
        shop_id = 0
        if row[0] is not None and row[0] != '':
            shop_id = int(row[0])
        goods_id = 0
        if row[1] is not None and row[1] != '':
            goods_id = int(row[1])
        num = int(row[2])
        city = 0
        if row[3] is not None and row[3] != '':
            city = row[3]
        create_date = row[4]
        upc = 0
        if row[5] is not None and row[5] != '':
            upc = row[5]
        goods_name = row[6]
        price = 0.0
        if row[7] is not None and row[7] != '':
            price = float(row[7])
        first_cate_id = 0
        if row[8] is not None and row[8] != '':
            first_cate_id = int(row[8])
            second_cate_id = 0
        if row[9] is not None and row[9] != '':
            second_cate_id = int(row[9])
        third_cate_id = 0
        if row[10] is not None and row[10] != '':
            third_cate_id = int(row[10])
        sales_tmp_ins = sales_old_tmp.SalesOldTmp()
        sales_tmp_ins.shop_id = shop_id
        sales_tmp_ins.upc = upc
        sales_tmp_ins.goods_id = goods_id
        sales_tmp_ins.first_cate_id = first_cate_id
        sales_tmp_ins.second_cate_id = second_cate_id
        sales_tmp_ins.third_cate_id = third_cate_id
        sales_tmp_ins.goods_name = goods_name
        sales_tmp_ins.price = price
        sales_tmp_ins.city = city
        date_nums = {}
        datenum_ins = sales_old_tmp.DateNum()
        datenum_ins.create_date = create_date
        datenum_ins.num = num
        datenum_ins.week_i = datetime.datetime.strptime(create_date, "%Y-%m-%d").weekday() + 1
        if datenum_ins.week_i <= 5:
            datenum_ins.week_type = 0
        else:
            datenum_ins.week_type = 1
        date_nums[create_date] = datenum_ins
        sales_tmp_ins.date_nums = date_nums
        sales_old_tmp_dict[str(shop_id) + "_" + str(upc)] = sales_tmp_ins







    def add_time(self,sales_old_ins,week_days1,results3):
        day_types= {}
        for row in results3:
            day_types[row[0]] = row[1]

        for day in week_days1:
            crt = datetime.datetime.strptime(day, "%Y-%m-%d")
            sales_old_ins.week_i.append(crt.weekday()+1)
            sales_old_ins.month.append(crt.month)
            if crt.month >= 1 and crt.month <= 3:
                sales_old_ins.season.append(1)
            elif crt.month >=4 and crt.month <= 6:
                sales_old_ins.season.append(2)
            elif crt.month >=7 and crt.month <= 9:
                sales_old_ins.season.append(3)
            else:
                sales_old_ins.season.append(4)
            ind = week_days1.index(day)
            if ind <=4:
                sales_old_ins.week_type.append(0)
            else:
                sales_old_ins.week_type.append(1)
            if day in day_types.keys():
                sales_old_ins.holiday_type.append(day_types[day])

        sales_old_ins.week_i_1 = sales_old_ins.week_i[0]
        sales_old_ins.season_1 = sales_old_ins.season[0]
        sales_old_ins.week_type_1 = sales_old_ins.week_type[0]
        sales_old_ins.month_1 = sales_old_ins.month[0]
        sales_old_ins.holiday_type_1 = sales_old_ins.holiday_type[0]

        sales_old_ins.week_i_2 = sales_old_ins.week_i[1]
        sales_old_ins.season_2 = sales_old_ins.season[1]
        sales_old_ins.week_type_2 = sales_old_ins.week_type[1]
        sales_old_ins.month_2 = sales_old_ins.month[1]
        sales_old_ins.holiday_type_2 = sales_old_ins.holiday_type[1]

        sales_old_ins.week_i_3 = sales_old_ins.week_i[2]
        sales_old_ins.season_3 = sales_old_ins.season[2]
        sales_old_ins.week_type_3 = sales_old_ins.week_type[2]
        sales_old_ins.month_3 = sales_old_ins.month[2]
        sales_old_ins.holiday_type_3 = sales_old_ins.holiday_type[2]

        sales_old_ins.week_i_4 = sales_old_ins.week_i[3]
        sales_old_ins.season_4 = sales_old_ins.season[3]
        sales_old_ins.week_type_4 = sales_old_ins.week_type[3]
        sales_old_ins.month_4 = sales_old_ins.month[3]
        sales_old_ins.holiday_type_4 = sales_old_ins.holiday_type[3]

        sales_old_ins.week_i_5 = sales_old_ins.week_i[4]
        sales_old_ins.season_5 = sales_old_ins.season[4]
        sales_old_ins.week_type_5 = sales_old_ins.week_type[4]
        sales_old_ins.month_5 = sales_old_ins.month[4]
        sales_old_ins.holiday_type_5 = sales_old_ins.holiday_type[4]

        sales_old_ins.week_i_6 = sales_old_ins.week_i[5]
        sales_old_ins.season_6 = sales_old_ins.season[5]
        sales_old_ins.week_type_6 = sales_old_ins.week_type[5]
        sales_old_ins.month_6 = sales_old_ins.month[5]
        sales_old_ins.holiday_type_6 = sales_old_ins.holiday_type[5]

        sales_old_ins.week_i_7 = sales_old_ins.week_i[6]
        sales_old_ins.season_7 = sales_old_ins.season[6]
        sales_old_ins.week_type_7 = sales_old_ins.week_type[6]
        sales_old_ins.month_7 = sales_old_ins.month[6]
        sales_old_ins.holiday_type_7 = sales_old_ins.holiday_type[6]



    def add_weather(self,sales_old_ins,week_days1,results1,results2):

        if sales_old_ins.city is not None and sales_old_ins.city == '':
            if sales_old_ins.city == '天津新区':
                sales_old_ins.city = '天津'
            sales_old_ins.city = str(sales_old_ins.city).strip("市")
            week_weather = self.get_weather(week_days1,results1,results2)

            for day,i in zip(week_days1,range(len(week_days1))):
                key_weather = sales_old_ins.city + "_" + day
                if key_weather in week_weather.keys():
                    weather_ins = week_weather[key_weather]
                    sales_old_ins.city_id = weather_ins.city_id
                    if i==0:
                        sales_old_ins.templow_1 = weather_ins.templow
                        sales_old_ins.temphigh_1 = weather_ins.temphigh
                        sales_old_ins.weather_type_1 = weather_ins.weather_type
                        sales_old_ins.windpower_1 = weather_ins.windpower
                        sales_old_ins.winddirect_1 = weather_ins.winddirect
                        sales_old_ins.windspeed_1 = weather_ins.windspeed
                    if i == 1:
                        sales_old_ins.templow_2 = weather_ins.templow
                        sales_old_ins.temphigh_2 = weather_ins.temphigh
                        sales_old_ins.weather_type_2 = weather_ins.weather_type
                        sales_old_ins.windpower_2 = weather_ins.windpower
                        sales_old_ins.winddirect_2 =  weather_ins.winddirect
                        sales_old_ins.windspeed_2 =  weather_ins.windspeed
                    if i == 2:
                        sales_old_ins.templow_3 = weather_ins.templow
                        sales_old_ins.temphigh_3 = weather_ins.temphigh
                        sales_old_ins.weather_type_3 =  weather_ins.weather_type
                        sales_old_ins.windpower_3 = weather_ins.windpower
                        sales_old_ins.winddirect_3 = weather_ins.winddirect
                        sales_old_ins.windspeed_3 =  weather_ins.windspeed
                    if i == 3:
                        sales_old_ins.templow_4 = weather_ins.templow
                        sales_old_ins.temphigh_4 = weather_ins.temphigh
                        sales_old_ins.weather_type_4 =  weather_ins.weather_type
                        sales_old_ins.windpower_4 = weather_ins.windpower
                        sales_old_ins.winddirect_4 = weather_ins.winddirect
                        sales_old_ins.windspeed_4 =  weather_ins.windspeed
                    if i == 4:
                        sales_old_ins.templow_5 = weather_ins.templow
                        sales_old_ins.temphigh_5 = weather_ins.temphigh
                        sales_old_ins.weather_type_5 =  weather_ins.weather_type
                        sales_old_ins.windpower_5 = weather_ins.windpower
                        sales_old_ins.winddirect_5 = weather_ins.winddirect
                        sales_old_ins.windspeed_5 =  weather_ins.windspeed
                    if i == 5:
                        sales_old_ins.templow_6 = weather_ins.templow
                        sales_old_ins.temphigh_6 = weather_ins.temphigh
                        sales_old_ins.weather_type_6 =  weather_ins.weather_type
                        sales_old_ins.windpower_6 = weather_ins.windpower
                        sales_old_ins.winddirect_6 = weather_ins.winddirect
                        sales_old_ins.windspeed_6 =  weather_ins.windspeed
                    if i == 6:
                        sales_old_ins.templow_7 = weather_ins.templow
                        sales_old_ins.temphigh_7 = weather_ins.temphigh
                        sales_old_ins.weather_type_7 =  weather_ins.weather_type
                        sales_old_ins.windpower_7 = weather_ins.windpower
                        sales_old_ins.winddirect_7 = weather_ins.winddirect
                        sales_old_ins.windspeed_7 =  weather_ins.windspeed

    def add_baseinfo(self,sales_old_ins,sales_old_tmp_ins):
        sales_old_ins.shop_id = int(sales_old_tmp_ins.shop_id)
        sales_old_ins.goods_id = int(sales_old_tmp_ins.goods_id)
        sales_old_ins.city = sales_old_tmp_ins.city
        sales_old_ins.upc = sales_old_tmp_ins.upc
        sales_old_ins.goods_name = sales_old_tmp_ins.goods_name
        sales_old_ins.price = float(sales_old_tmp_ins.price)
        sales_old_ins.first_cate_id = int(sales_old_tmp_ins.first_cate_id)
        sales_old_ins.second_cate_id = int(sales_old_tmp_ins.second_cate_id)
        sales_old_ins.third_cate_id = int(sales_old_tmp_ins.third_cate_id)


    def get_date(self,n):
        """
        获取多少周之前 周一到周日的时间
        :param n:  多少周
        :return:
        """
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        wd = datetime.datetime.now().weekday() + 1
        #当前周一的时间
        week_one_date = str(
            (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                days=-(wd-1))).strftime("%Y-%m-%d"))
        #获取n周以前的周一时间
        start_date =  str(
            (datetime.datetime.strptime(week_one_date, "%Y-%m-%d") + datetime.timedelta(
                days=-n*7)).strftime("%Y-%m-%d"))
        week_days = []
        #获取周一到周日的时间
        for i in range(7):
            start_date_i = str(
                (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(
                    days = i)).strftime("%Y-%m-%d"))
            week_days.append(start_date_i)
        return week_days

if __name__=='__main__':
    sp_ins = SalesPredict()
    # dates = sp_ins.get_date(1)
    # print (dates)
    salesold_inss = sp_ins.generate_data(all_data=False)
    for salesold_ins in salesold_inss:
        # 103
        pristr = ("%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s" ) % (
        str(salesold_ins.shop_id),
        str(salesold_ins.upc),
        str(salesold_ins.goods_id),
        str(salesold_ins.first_cate_id),
        str(salesold_ins.second_cate_id),
        str(salesold_ins.third_cate_id),
        str(salesold_ins.goods_name),
        str(salesold_ins.price),
        str(salesold_ins.city),
        # 冗余维度字段
        str(salesold_ins.create_date),
        str(salesold_ins.num),

        # 销量数据维度
        str( salesold_ins.sale_1), # 周一
        str(salesold_ins.sale_2), # 周二
        str(salesold_ins.sale_3),
        str(salesold_ins.sale_4),
        str(salesold_ins.sale_5),
        str(salesold_ins.sale_6),
        str(salesold_ins.sale_7),

        str(salesold_ins.sale_1_2_avg), # 两个周1 平均销量
        str(salesold_ins.sale_2_2_avg ),  #
        str(salesold_ins.sale_3_2_avg ),  #
        str(salesold_ins.sale_4_2_avg ),  #
        str( salesold_ins.sale_5_2_avg),  #
        str(salesold_ins.sale_6_2_avg),  #
        str(salesold_ins.sale_7_2_avg ),  #

        str(salesold_ins.sale_1_4_avg), # 4个周1 平均销量
        str( salesold_ins.sale_2_4_avg),  #
        str(salesold_ins.sale_3_4_avg),  #
        str(salesold_ins.sale_4_4_avg),  #
        str( salesold_ins.sale_5_4_avg),  #
        str( salesold_ins.sale_6_4_avg),  #
        str(salesold_ins.sale_7_4_avg),  #

        str(salesold_ins.sale_1_8_avg), # 8个周1 平均销量
        str(salesold_ins.sale_2_8_avg),  #
        str( salesold_ins.sale_3_8_avg),  #
        str( salesold_ins.sale_4_8_avg ),  #
        str( salesold_ins.sale_5_8_avg),  #
        str(salesold_ins.sale_6_8_avg),  #
        str(salesold_ins.sale_7_8_avg), #

        str( salesold_ins.sale_1_12_avg), # 12个周1 平均销量
        str( salesold_ins.sale_2_12_avg),  #
        str(salesold_ins.sale_3_12_avg),  #
        str( salesold_ins.sale_4_12_avg),  #
        str( salesold_ins.sale_5_12_avg),  #
        str(salesold_ins.sale_6_12_avg),  #
        str(salesold_ins.sale_7_12_avg),  #

        str(salesold_ins.sale_1week_avg_in), # 1周 周中平均销量
        str( salesold_ins.sale_1week_avg_out),  #1周 周末平均销量
        str(salesold_ins.sale_2week_avg_in),  # 2周 周中平均销量
        str(salesold_ins.sale_2week_avg_out), # 2周 周末平均销量
        str( salesold_ins.sale_4week_avg_in),  # 4周 周中平均销量
        str( salesold_ins.sale_4week_avg_out),  # 4周 周末平均销量
        str( salesold_ins.sale_8week_avg_in),  # 8周 周中平均销量
        str(salesold_ins.sale_8week_avg_out),  # 8周 周末平均销量
        str(salesold_ins.sale_12week_avg_in),  # 12周 周中平均销量
        str(salesold_ins.sale_12week_avg_out),  # 12周 周末平均销量

        # 天气维度
        str(salesold_ins.templow_1),
        str( salesold_ins.temphigh_1),
        str( salesold_ins.weather_type_1),
        str( salesold_ins.windpower_1),
        str( salesold_ins.winddirect_1),
        str( salesold_ins.windspeed_1),

        str(salesold_ins.templow_2),
        str(salesold_ins.temphigh_2),
        str( salesold_ins.weather_type_2),
        str( salesold_ins.windpower_2),
        str(salesold_ins.winddirect_2),
        str(salesold_ins.windspeed_2),

        str( salesold_ins.templow_3),
        str( salesold_ins.temphigh_3),
        str( salesold_ins.weather_type_3),
        str(salesold_ins.windpower_3 ),
        str( salesold_ins.winddirect_3),
        str(salesold_ins.windspeed_3),

        str( salesold_ins.templow_4),
        str(salesold_ins.temphigh_4),
        str( salesold_ins.weather_type_4),
        str( salesold_ins.windpower_4),
        str( salesold_ins.winddirect_4),
        str(salesold_ins.windspeed_4),

        str(salesold_ins.templow_5),
        str( salesold_ins.temphigh_5),
        str( salesold_ins.weather_type_5),
        str( salesold_ins.windpower_5),
        str( salesold_ins.winddirect_5),
        str(salesold_ins.windspeed_5),

        str( salesold_ins.templow_6 ),
        str( salesold_ins.temphigh_6 ),
        str( salesold_ins.weather_type_6 ),
        str( salesold_ins.windpower_6 ),
        str( salesold_ins.winddirect_6 ),
        str(salesold_ins.windspeed_6 ),

        str( salesold_ins.templow_7 ),
        str( salesold_ins.temphigh_7 ),
        str( salesold_ins.weather_type_7 ),
        str(salesold_ins.windpower_7 ),
        str( salesold_ins.winddirect_7 ),
        str(salesold_ins.windspeed_7 ),

    # 时间维度
        str(salesold_ins.week_i_1 ),
        str( salesold_ins.season_1 ),
        str(salesold_ins.week_type_1 ),
        str(salesold_ins.month_1),
        str(salesold_ins.holiday_type_1),

            str(salesold_ins.week_i_2),
            str(salesold_ins.season_2),
            str(salesold_ins.week_type_2),
            str(salesold_ins.month_2),
            str(salesold_ins.holiday_type_2),

            str(salesold_ins.week_i_3),
            str(salesold_ins.season_3),
            str(salesold_ins.week_type_3),
            str(salesold_ins.month_3),
            str(salesold_ins.holiday_type_3),

            str(salesold_ins.week_i_4),
            str(salesold_ins.season_4),
            str(salesold_ins.week_type_4),
            str(salesold_ins.month_4),
            str(salesold_ins.holiday_type_4),

            str(salesold_ins.week_i_5),
            str(salesold_ins.season_5),
            str(salesold_ins.week_type_5),
            str(salesold_ins.month_5),
            str(salesold_ins.holiday_type_5),

            str(salesold_ins.week_i_6),
            str(salesold_ins.season_6),
            str(salesold_ins.week_type_6),
            str(salesold_ins.month_6),
            str(salesold_ins.holiday_type_6),

            str(salesold_ins.week_i_7),
            str(salesold_ins.season_7),
            str(salesold_ins.week_type_7),
            str(salesold_ins.month_7),
            str(salesold_ins.holiday_type_7),
    # 地域维度
        str(salesold_ins.city_id),
        )

        with open ("tmp_sales_week.txt",'a') as f:
            f.write(pristr+"\n")
