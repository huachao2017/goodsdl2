from goods.sellgoods.salesquantity.bean import ai_sales_old
from goods.sellgoods.salesquantity.local_util import sales2_save
from set_config import config
from goods.sellgoods.salesquantity.local_util import sales_predict_util

import os
sales2_old_traindata = config.shellgoods_params['sales2_old_traindata']
class Sales2LoadData:
    file_operator = 'tmp_sales_week.txt_'

    def load_all_data(self):
        filenames = os.listdir(sales2_old_traindata)
        for i in range(1,40):
            y_dates = sales_predict_util.SalesPredict().get_date(i)
            x_dates = sales_predict_util.SalesPredict().get_date(i+1)
            flag = False
            for filename in filenames:
                if x_dates[0] in filename:
                    flag = True
                    break
            X,Y = self.load_data(x_dates[0],y_dates[0])
            return X,Y

    def load_data(self,train_x_date=None,train_y_date=None):
        salesold_inss_x = {}
        salesold_inss_y = {}
        if train_x_date != None:
            salesold_inss_x = self.load_from_localfile(train_x_date)
        if train_y_date != None:
            salesold_inss_y = self.load_from_localfile(train_y_date)

        if len(list(salesold_inss_x.keys())) > 0 :
            X,Y = self.train_data(self.get_train_data(salesold_inss_x,salesold_inss_y))
            return X,Y

    def get_train_data (self,salesold_inss_x,salesold_inss_y):
        for key1 in salesold_inss_x:
            if key1 in salesold_inss_y.keys():
                salesold_inss_x[key1].y_labels = salesold_inss_y[key1].y_labels
            else:
                salesold_inss_x[key1].y_labels = [0,0,0,0,0,0,0]
        return salesold_inss_x


    def train_data(self,salesold_inss_x):
        X = []
        Y = []
        for key in salesold_inss_x:
            salesold_ins = salesold_inss_x[key]
            data_x = [
            salesold_ins.shop_id,
            salesold_ins.upc,
            salesold_ins.first_cate_id,
            salesold_ins.second_cate_id,
            salesold_ins.third_cate_id,
            salesold_ins.price,
            # 销量数据维度
            salesold_ins.sale_1,
            salesold_ins.sale_2,
            salesold_ins.sale_3,
            salesold_ins.sale_4,
            salesold_ins.sale_5,
            salesold_ins.sale_6,
            salesold_ins.sale_7,

            salesold_ins.sale_1_2_avg,
            salesold_ins.sale_2_2_avg,
            salesold_ins.sale_3_2_avg,
            salesold_ins.sale_4_2_avg,
            salesold_ins.sale_5_2_avg,
            salesold_ins.sale_6_2_avg,
            salesold_ins.sale_7_2_avg,

            salesold_ins.sale_1_4_avg,
            salesold_ins.sale_2_4_avg,
            salesold_ins.sale_3_4_avg,
            salesold_ins.sale_4_4_avg,
            salesold_ins.sale_5_4_avg,
            salesold_ins.sale_6_4_avg,
            salesold_ins.sale_7_4_avg,

            salesold_ins.sale_1_8_avg,
            salesold_ins.sale_2_8_avg,
            salesold_ins.sale_3_8_avg,
            salesold_ins.sale_4_8_avg,
            salesold_ins.sale_5_8_avg ,
            salesold_ins.sale_6_8_avg,
            salesold_ins.sale_7_8_avg,

            salesold_ins.sale_1_12_avg,
            salesold_ins.sale_2_12_avg,
            salesold_ins.sale_3_12_avg,
            salesold_ins.sale_4_12_avg,
            salesold_ins.sale_5_12_avg,
            salesold_ins.sale_6_12_avg,
            salesold_ins.sale_7_12_avg,

            salesold_ins.sale_1week_avg_in,
            salesold_ins.sale_1week_avg_out,
            salesold_ins.sale_2week_avg_in,
            salesold_ins.sale_2week_avg_out,
            salesold_ins.sale_4week_avg_in,
            salesold_ins.sale_4week_avg_out,
            salesold_ins.sale_8week_avg_in,
            salesold_ins.sale_8week_avg_out,
            salesold_ins.sale_12week_avg_in,
            salesold_ins.sale_12week_avg_out,

            # 天气维度
            salesold_ins.templow_1,
            salesold_ins.temphigh_1,
            salesold_ins.weather_type_1,
            salesold_ins.windpower_1,
            salesold_ins.winddirect_1,
            salesold_ins.windspeed_1,

            salesold_ins.templow_2,
            salesold_ins.temphigh_2,
            salesold_ins.weather_type_2,
            salesold_ins.windpower_2,
            salesold_ins.winddirect_2,
            salesold_ins.windspeed_2,

            salesold_ins.templow_3,
            salesold_ins.temphigh_3 ,
            salesold_ins.weather_type_3 ,
            salesold_ins.windpower_3,
            salesold_ins.winddirect_3,
            salesold_ins.windspeed_3,

            salesold_ins.templow_4,
            salesold_ins.temphigh_4,
            salesold_ins.weather_type_4 ,
            salesold_ins.windpower_4,
            salesold_ins.winddirect_4 ,
            salesold_ins.windspeed_4 ,

            salesold_ins.templow_5 ,
            salesold_ins.temphigh_5 ,
            salesold_ins.weather_type_5,
            salesold_ins.windpower_5,
            salesold_ins.winddirect_5 ,
            salesold_ins.windspeed_5,

            salesold_ins.templow_6,
            salesold_ins.temphigh_6 ,
            salesold_ins.weather_type_6 ,
            salesold_ins.windpower_6,
            salesold_ins.winddirect_6 ,
            salesold_ins.windspeed_6,

            salesold_ins.templow_7 ,
            salesold_ins.temphigh_7,
            salesold_ins.weather_type_7 ,
            salesold_ins.windpower_7 ,
            salesold_ins.winddirect_7,
            salesold_ins.windspeed_7,

            # 时间维度
            salesold_ins.week_i_1,
            salesold_ins.season_1,
            salesold_ins.week_type_1 ,
            salesold_ins.month_1 ,
            salesold_ins.holiday_type_1,

            salesold_ins.week_i_2,
            salesold_ins.season_2,
            salesold_ins.week_type_2 ,
            salesold_ins.month_2 ,
            salesold_ins.holiday_type_2 ,

            salesold_ins.week_i_3 ,
            salesold_ins.season_3,
            salesold_ins.week_type_3 ,
            salesold_ins.month_3,
            salesold_ins.holiday_type_3 ,

            salesold_ins.week_i_4,
            salesold_ins.season_4 ,
            salesold_ins.week_type_4 ,
            salesold_ins.month_4 ,
            salesold_ins.holiday_type_4 ,

            salesold_ins.week_i_5 ,
            salesold_ins.season_5 ,
            salesold_ins.week_type_5,
            salesold_ins.month_5,
            salesold_ins.holiday_type_5,

            salesold_ins.week_i_6 ,
            salesold_ins.season_6,
            salesold_ins.week_type_6 ,
            salesold_ins.month_6,
            salesold_ins.holiday_type_6 ,

            salesold_ins.week_i_7,
            salesold_ins.season_7,
            salesold_ins.week_type_7 ,
            salesold_ins.month_7 ,
            salesold_ins.holiday_type_7 ,
            # 地域维度
            salesold_ins.city_id ,

            ]

            data_y = salesold_ins.y_labels
            X.append(data_x)
            Y.append(data_y)

        return X,Y


    def load_from_localfile(self,train_x_date):
        xfile = self.file_operator+str(train_x_date)
        xfile = os.path.join(sales2_old_traindata,xfile)
        salesold_inss_dict  = {}
        with open(xfile,'r') as f :
            lines = f.readlines()
            for line in lines:
                words = line.split(",")
                salesold_ins = self.words2bean(words)
                salesold_ins.y_labels = [
                    salesold_ins.sale_1,salesold_ins.sale_2,salesold_ins.sale_3,salesold_ins.sale_4,salesold_ins.sale_5,salesold_ins.sale_6,salesold_ins.sale_7
                ]
                if int(salesold_ins.shop_id) != 0 and int(salesold_ins.upc) != 0 :
                    salesold_inss_dict[str(int(salesold_ins.shop_id)) + "_" + str(int(salesold_ins.upc))] = salesold_ins
        return salesold_inss_dict


    def words2bean(self,words):
        salesold_ins = ai_sales_old.SalesOld()
        salesold_ins.shop_id = words[0]
        salesold_ins.upc = words[1]
        salesold_ins.goods_id = words[1]
        salesold_ins.first_cate_id = words[1]
        salesold_ins.second_cate_id = words[1]
        salesold_ins.third_cate_id = words[1]
        salesold_ins.goods_name = words[1]
        salesold_ins.price = words[1]
        salesold_ins.city = words[1]

        # 销量数据维度
        salesold_ins.sale_1 = words[1]
        salesold_ins.sale_2 = words[1]
        salesold_ins.sale_3 = words[1]
        salesold_ins.sale_4 = words[1]
        salesold_ins.sale_5 = words[1]
        salesold_ins.sale_6 = words[1]
        salesold_ins.sale_7 = words[1]

        salesold_ins.sale_1_2_avg = words[1]
        salesold_ins.sale_2_2_avg = words[1]
        salesold_ins.sale_3_2_avg = words[1]
        salesold_ins.sale_4_2_avg = words[1]
        salesold_ins.sale_5_2_avg = words[1]
        salesold_ins.sale_6_2_avg = words[1]
        salesold_ins.sale_7_2_avg = words[1]

        salesold_ins.sale_1_4_avg = words[1]
        salesold_ins.sale_2_4_avg = words[1]
        salesold_ins.sale_3_4_avg = words[1]
        salesold_ins.sale_4_4_avg = words[1]
        salesold_ins.sale_5_4_avg = words[1]
        salesold_ins.sale_6_4_avg = words[1]
        salesold_ins.sale_7_4_avg = words[1]

        salesold_ins.sale_1_8_avg = words[1]
        salesold_ins.sale_2_8_avg = words[1]
        salesold_ins.sale_3_8_avg = words[1]
        salesold_ins.sale_4_8_avg = words[1]
        salesold_ins.sale_5_8_avg = words[1]
        salesold_ins.sale_6_8_avg = words[1]
        salesold_ins.sale_7_8_avg = words[1]

        salesold_ins.sale_1_12_avg = words[1]
        salesold_ins.sale_2_12_avg = words[1]
        salesold_ins.sale_3_12_avg = words[1]
        salesold_ins.sale_4_12_avg = words[1]
        salesold_ins.sale_5_12_avg = words[1]
        salesold_ins.sale_6_12_avg = words[1]
        salesold_ins.sale_7_12_avg = words[1]

        salesold_ins.sale_1week_avg_in = words[1]
        salesold_ins.sale_1week_avg_out = words[1]
        salesold_ins.sale_2week_avg_in = words[1]
        salesold_ins.sale_2week_avg_out = words[1]
        salesold_ins.sale_4week_avg_in = words[1]
        salesold_ins.sale_4week_avg_out = words[1]
        salesold_ins.sale_8week_avg_in = words[1]
        salesold_ins.sale_8week_avg_out = words[1]
        salesold_ins.sale_12week_avg_in = words[1]
        salesold_ins.sale_12week_avg_out = words[1]

        # 天气维度
        salesold_ins.templow_1 = words[1]
        salesold_ins.temphigh_1 = words[1]
        salesold_ins.weather_type_1 = words[1]
        salesold_ins.windpower_1 = words[1]
        salesold_ins.winddirect_1 = words[1]
        salesold_ins.windspeed_1 = words[1]

        salesold_ins.templow_2 = words[1]
        salesold_ins.temphigh_2 = words[1]
        salesold_ins.weather_type_2 = words[1]
        salesold_ins.windpower_2 = words[1]
        salesold_ins.winddirect_2 = words[1]
        salesold_ins.windspeed_2 = words[1]

        salesold_ins.templow_3 = words[1]
        salesold_ins.temphigh_3 = words[1]
        salesold_ins.weather_type_3 = words[1]
        salesold_ins.windpower_3 = words[1]
        salesold_ins.winddirect_3 = words[1]
        salesold_ins.windspeed_3 = words[1]

        salesold_ins.templow_4 = words[1]
        salesold_ins.temphigh_4 = words[1]
        salesold_ins.weather_type_4 = words[1]
        salesold_ins.windpower_4 = words[1]
        salesold_ins.winddirect_4 = words[1]
        salesold_ins.windspeed_4 = words[1]

        salesold_ins.templow_5 = words[1]
        salesold_ins.temphigh_5 = words[1]
        salesold_ins.weather_type_5 = words[1]
        salesold_ins.windpower_5 = words[1]
        salesold_ins.winddirect_5 = words[1]
        salesold_ins.windspeed_5 = words[1]

        salesold_ins.templow_6 = words[1]
        salesold_ins.temphigh_6 = words[1]
        salesold_ins.weather_type_6 = words[1]
        salesold_ins.windpower_6 = words[1]
        salesold_ins.winddirect_6 = words[1]
        salesold_ins.windspeed_6 = words[1]

        salesold_ins.templow_7 = words[1]
        salesold_ins.temphigh_7 = words[1]
        salesold_ins.weather_type_7 = words[1]
        salesold_ins.windpower_7 = words[1]
        salesold_ins.winddirect_7 = words[1]
        salesold_ins.windspeed_7 = words[1]

        # 时间维度
        salesold_ins.week_i_1 = words[1]
        salesold_ins.season_1 = words[1]
        salesold_ins.week_type_1 = words[1]
        salesold_ins.month_1 = words[1]
        salesold_ins.holiday_type_1 = words[1]

        salesold_ins.week_i_2 = words[1]
        salesold_ins.season_2 = words[1]
        salesold_ins.week_type_2 = words[1]
        salesold_ins.month_2 = words[1]
        salesold_ins.holiday_type_2 = words[1]

        salesold_ins.week_i_3 = words[1]
        salesold_ins.season_3 = words[1]
        salesold_ins.week_type_3 = words[1]
        salesold_ins.month_3 = words[1]
        salesold_ins.holiday_type_3 = words[1]

        salesold_ins.week_i_4 = words[1]
        salesold_ins.season_4 = words[1]
        salesold_ins.week_type_4 = words[1]
        salesold_ins.month_4 = words[1]
        salesold_ins.holiday_type_4 = words[1]

        salesold_ins.week_i_5 = words[1]
        salesold_ins.season_5 = words[1]
        salesold_ins.week_type_5 = words[1]
        salesold_ins.month_5 = words[1]
        salesold_ins.holiday_type_5 = words[1]

        salesold_ins.week_i_6 = words[1]
        salesold_ins.season_6 = words[1]
        salesold_ins.week_type_6 = words[1]
        salesold_ins.month_6 = words[1]
        salesold_ins.holiday_type_6 = words[1]

        salesold_ins.week_i_7 = words[1]
        salesold_ins.season_7 = words[1]
        salesold_ins.week_type_7 = words[1]
        salesold_ins.month_7 = words[1]
        salesold_ins.holiday_type_7 = words[1]
        # 地域维度
        salesold_ins.city_id = words[1]
        salesold_ins.week_i_1_date = words[1]
        salesold_ins = sales2_save.data_check(salesold_ins)
        return salesold_ins