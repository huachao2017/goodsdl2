from goods.sellgoods.salesquantity.bean import ai_sales_old
from goods.sellgoods.salesquantity.local_util import sales2_save
from set_config import config
from goods.sellgoods.salesquantity.local_util import sales_predict_util
from goods.sellgoods.salesquantity.model import keras_regress
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import time
import os
sales2_old_traindata = config.shellgoods_params['sales2_old_traindata']
class Sales2LoadData:
    file_operator = 'tmp_sales_week.txt_'
    def load_all_data(self,data_split=0.3,n=0):
        filenames = os.listdir(sales2_old_traindata)
        while 1:
            for i in range(1,40):
                y_dates = sales_predict_util.SalesPredict().get_date(i,'2019-11-18')
                x_dates = sales_predict_util.SalesPredict().get_date(i+1,'2019-11-18')
                flag = False
                for filename in filenames:
                    if x_dates[0] in filename:
                        flag = True
                        break
                if flag:
                    X,Y = self.load_data(x_dates[0],y_dates[0])
                    if  X!= None and Y!= None:
                        X=np.array(X)
                        Y=np.array(Y)
                        X,Y,ss_X,ss_Y,mm_X,mm_Y =  self.process_data(Y[:,n],X)
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, Y, test_size=data_split, random_state=20)
                        yield X_train,y_train
                    else:
                        X = []
                        Y = []
                else:
                    X=[]
                    Y=[]

    def load_predict_data(self,week_one_day=None):
        filenames = os.listdir(sales2_old_traindata)
        y_dates = sales_predict_util.SalesPredict().get_date(1, week_one_day)
        x_dates = sales_predict_util.SalesPredict().get_date(2, week_one_day)
        flag = False
        for filename in filenames:
            if x_dates[0] in filename:
                flag = True
                break
        if flag:
            X, Y = self.load_data(x_dates[0], y_dates[0])
            if X != None and Y != None:
                X = np.array(X)
                Y = np.array(Y)
                X_p, Y_p,ss_X,ss_Y,mm_X,mm_Y = self.process_data(Y[:, 1], X)
                return X,Y,X_p, Y_p,ss_X,ss_Y,mm_X,mm_Y
        else:
            return None,None,None,None,None,None,None,None

    def process_data(self,Y,X):
        train_samples = len(Y)
        Y = np.array(Y)
        X = np.array(X)
        mm_X = MinMaxScaler()
        X = mm_X.fit_transform(X)
        mm_Y = MinMaxScaler()
        Y = mm_Y.fit_transform(Y.reshape(train_samples, 1))
        # 数据标准化
        ss_X = StandardScaler()
        X = ss_X.fit_transform(X)
        ss_Y = StandardScaler()
        Y = ss_Y.fit_transform(Y)
        return X,Y,ss_X,ss_Y,mm_X,mm_Y


    def load_data(self,train_x_date=None,train_y_date=None):
        salesold_inss_x = {}
        salesold_inss_y = {}
        if train_x_date != None:
            salesold_inss_x,salesold_inss_shop_dict_x = self.load_from_localfile(train_x_date)
        if train_y_date != None:
            salesold_inss_y,salesold_inss_shop_dict_y = self.load_from_localfile(train_y_date)

        if len(list(salesold_inss_x.keys())) > 0 :
            X,Y = self.train_data(self.get_train_data(salesold_inss_x,salesold_inss_y,salesold_inss_shop_dict_x,salesold_inss_shop_dict_y))
            return X,Y

    def get_train_data (self,salesold_inss_x,salesold_inss_y,salesold_inss_shop_dict_x,salesold_inss_shop_dict_y):
        for key1 in salesold_inss_x:
            if key1 in salesold_inss_y.keys():
                salesold_inss_x[key1].y_labels = salesold_inss_y[key1].y_labels
            else: #
                salesold_inss_x[key1].y_labels = [0,0,0,0,0,0,0]
        # 把 下周该门店有销量的数据也加入到训练数据中去
        for key2 in salesold_inss_y :
            salesold_ins_y = salesold_inss_y[key2]
            if key2 not in salesold_inss_x:
                salesold_ins_y = self.add_alter_trainweekdata(salesold_ins_y,salesold_inss_x,key2,salesold_inss_shop_dict_x)
                if salesold_ins_y != None:
                    salesold_inss_x[key2] = salesold_ins_y

        return salesold_inss_x

    def add_alter_trainweekdata(self,salesold_ins_y,salesold_inss_x,key_y,salesold_inss_shop_dict_x):
        salesold_ins_x = None
        shop_id = int(str(key_y).split("_")[0])
        if shop_id in list(salesold_inss_shop_dict_x.keys()):
            salesold_ins_x = salesold_inss_shop_dict_x[shop_id]
        # 替换天气维度 时间 地点等
        if salesold_ins_x != None:
            salesold_ins_y.templow_1 = salesold_ins_x.templow_1
            salesold_ins_y.temphigh_1 = salesold_ins_x.temphigh_1
            salesold_ins_y.weather_type_1=  salesold_ins_x.weather_type_1,
            salesold_ins_y.windpower_1 =  salesold_ins_x.windpower_1
            salesold_ins_y.winddirect_1 =salesold_ins_x.winddirect_1
            salesold_ins_y.windspeed_1 =salesold_ins_x.windspeed_1

            salesold_ins_y.templow_2 = salesold_ins_x.templow_2
            salesold_ins_y.temphigh_2 = salesold_ins_x.temphigh_2
            salesold_ins_y.weather_type_2 =salesold_ins_x.weather_type_2
            salesold_ins_y.windpower_2= salesold_ins_x.windpower_2
            salesold_ins_y.winddirect_2 = salesold_ins_x.winddirect_2
            salesold_ins_y.windspeed_2 = salesold_ins_x.windspeed_2

            salesold_ins_y.templow_3 = salesold_ins_x.templow_3
            salesold_ins_y.temphigh_3 = salesold_ins_x.temphigh_3
            salesold_ins_y.weather_type_3 = salesold_ins_x.weather_type_3
            salesold_ins_y.windpower_3 = salesold_ins_x.windpower_3
            salesold_ins_y.winddirect_3=salesold_ins_x.winddirect_3
            salesold_ins_y.windspeed_3= salesold_ins_x.windspeed_3

            salesold_ins_y.templow_4= salesold_ins_x.templow_4
            salesold_ins_y.temphigh_4= salesold_ins_x.temphigh_4
            salesold_ins_y.weather_type_4= salesold_ins_x.weather_type_4
            salesold_ins_y.windpower_4= salesold_ins_x.windpower_4
            salesold_ins_y.winddirect_4= salesold_ins_x.winddirect_4
            salesold_ins_y.windspeed_4= salesold_ins_x.windspeed_4

            salesold_ins_y.templow_5= salesold_ins_x.templow_5
            salesold_ins_y.temphigh_5= salesold_ins_x.temphigh_5
            salesold_ins_y.weather_type_5= salesold_ins_x.weather_type_5
            salesold_ins_y.windpower_5= salesold_ins_x.windpower_5
            salesold_ins_y.winddirect_5= salesold_ins_x.winddirect_5
            salesold_ins_y.windspeed_5= salesold_ins_x.windspeed_5

            salesold_ins_y.templow_6= salesold_ins_x.templow_6
            salesold_ins_y.temphigh_6= salesold_ins_x.temphigh_6
            salesold_ins_y.weather_type_6= salesold_ins_x.weather_type_6
            salesold_ins_y.windpower_6= salesold_ins_x.windpower_6
            salesold_ins_y.winddirect_6= salesold_ins_x.winddirect_6
            salesold_ins_y.windspeed_6= salesold_ins_x.windspeed_6

            salesold_ins_y.templow_7= salesold_ins_x.templow_7
            salesold_ins_y.temphigh_7= salesold_ins_x.temphigh_7
            salesold_ins_y.weather_type_7= salesold_ins_x.weather_type_7
            salesold_ins_y.windpower_7= salesold_ins_x.windpower_7
            salesold_ins_y.winddirect_7= salesold_ins_x.winddirect_7
            salesold_ins_y.windspeed_7= salesold_ins_x.windspeed_7

            # 时间维度
            salesold_ins_y.week_i_1= salesold_ins_x.week_i_1
            salesold_ins_y.season_1= salesold_ins_x.season_1
            salesold_ins_y.week_type_1= salesold_ins_x.week_type_1
            salesold_ins_y.month_1= salesold_ins_x.month_1
            salesold_ins_y.holiday_type_1= salesold_ins_x.holiday_type_1

            salesold_ins_y.week_i_2= salesold_ins_x.week_i_2
            salesold_ins_y.season_2= salesold_ins_x.season_2
            salesold_ins_y.week_type_2 = salesold_ins_x.week_type_2
            salesold_ins_y.month_2= salesold_ins_x.month_2
            salesold_ins_y.holiday_type_2=salesold_ins_x.holiday_type_2

            salesold_ins_y.week_i_3= salesold_ins_x.week_i_3
            salesold_ins_y.season_3= salesold_ins_x.season_3
            salesold_ins_y.week_type_3= salesold_ins_x.week_type_3
            salesold_ins_y.month_3= salesold_ins_x.month_3
            salesold_ins_y.holiday_type_3= salesold_ins_x.holiday_type_3

            salesold_ins_y.week_i_4= salesold_ins_x.week_i_4
            salesold_ins_y.season_4= salesold_ins_x.season_4
            salesold_ins_y.week_type_4= salesold_ins_x.week_type_4
            salesold_ins_y.month_4= salesold_ins_x.month_4
            salesold_ins_y.holiday_type_4= salesold_ins_x.holiday_type_4

            salesold_ins_y.week_i_5= salesold_ins_x.week_i_5
            salesold_ins_y.season_5= salesold_ins_x.season_5
            salesold_ins_y.week_type_5= salesold_ins_x.week_type_5
            salesold_ins_y.month_5= salesold_ins_x.month_5
            salesold_ins_y.holiday_type_5= salesold_ins_x.holiday_type_5

            salesold_ins_y.week_i_6= salesold_ins_x.week_i_6
            salesold_ins_y.season_6= salesold_ins_x.season_6
            salesold_ins_y.week_type_6= salesold_ins_x.week_type_6
            salesold_ins_y.month_6= salesold_ins_x.month_6
            salesold_ins_y.holiday_type_6= salesold_ins_x.holiday_type_6

            salesold_ins_y.week_i_7= salesold_ins_x.week_i_7
            salesold_ins_y.season_7= salesold_ins_x.season_7
            salesold_ins_y.week_type_7= salesold_ins_x.week_type_7
            salesold_ins_y.month_7= salesold_ins_x.month_7
            salesold_ins_y.holiday_type_7= salesold_ins_x.holiday_type_7
            return salesold_ins_y
        else:
            return salesold_ins_x
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
        salesold_inss_shop_dict = {}

        with open(xfile,'r',encoding='UTF-8') as f :
            lines = f.readlines()
            for line in lines:
                if "," in line:
                    words = line.split(",")
                    # print (len(words))
                    salesold_ins = self.words2bean(words)
                    if salesold_ins != None:
                        salesold_ins.y_labels = [
                            salesold_ins.sale_1,salesold_ins.sale_2,salesold_ins.sale_3,salesold_ins.sale_4,salesold_ins.sale_5,salesold_ins.sale_6,salesold_ins.sale_7
                        ]
                        if int(salesold_ins.shop_id) != 0 and int(salesold_ins.upc) != 0 :
                            salesold_inss_dict[str(int(salesold_ins.shop_id)) + "_" + str(int(salesold_ins.upc))] = salesold_ins
                            salesold_inss_shop_dict[str(int(salesold_ins.shop_id))] = salesold_ins
        return salesold_inss_dict,salesold_inss_shop_dict


    def words2bean(self,words):
        if len(words) == 133:
            salesold_ins = ai_sales_old.SalesOld()
            salesold_ins.shop_id = words[0]
            salesold_ins.upc = words[1]
            salesold_ins.goods_id = words[2]
            salesold_ins.first_cate_id = words[3]
            salesold_ins.second_cate_id = words[4]
            salesold_ins.third_cate_id = words[5]
            salesold_ins.goods_name = words[6]
            salesold_ins.price = words[7]
            salesold_ins.city = words[8]

            # 销量数据维度
            salesold_ins.sale_1 = words[9]
            salesold_ins.sale_2 = words[10]
            salesold_ins.sale_3 = words[11]
            salesold_ins.sale_4 = words[12]
            salesold_ins.sale_5 = words[13]
            salesold_ins.sale_6 = words[14]
            salesold_ins.sale_7 = words[15]

            salesold_ins.sale_1_2_avg = words[16]
            salesold_ins.sale_2_2_avg = words[17]
            salesold_ins.sale_3_2_avg = words[18]
            salesold_ins.sale_4_2_avg = words[19]
            salesold_ins.sale_5_2_avg = words[20]
            salesold_ins.sale_6_2_avg = words[21]
            salesold_ins.sale_7_2_avg = words[22]

            salesold_ins.sale_1_4_avg = words[23]
            salesold_ins.sale_2_4_avg = words[24]
            salesold_ins.sale_3_4_avg = words[25]
            salesold_ins.sale_4_4_avg = words[26]
            salesold_ins.sale_5_4_avg = words[27]
            salesold_ins.sale_6_4_avg = words[28]
            salesold_ins.sale_7_4_avg = words[29]

            salesold_ins.sale_1_8_avg = words[30]
            salesold_ins.sale_2_8_avg = words[31]
            salesold_ins.sale_3_8_avg = words[32]
            salesold_ins.sale_4_8_avg = words[33]
            salesold_ins.sale_5_8_avg = words[34]
            salesold_ins.sale_6_8_avg = words[35]
            salesold_ins.sale_7_8_avg = words[36]

            salesold_ins.sale_1_12_avg = words[37]
            salesold_ins.sale_2_12_avg = words[38]
            salesold_ins.sale_3_12_avg = words[39]
            salesold_ins.sale_4_12_avg = words[40]
            salesold_ins.sale_5_12_avg = words[41]
            salesold_ins.sale_6_12_avg = words[42]
            salesold_ins.sale_7_12_avg = words[43]

            salesold_ins.sale_1week_avg_in = words[44]
            salesold_ins.sale_1week_avg_out = words[45]
            salesold_ins.sale_2week_avg_in = words[46]
            salesold_ins.sale_2week_avg_out = words[47]
            salesold_ins.sale_4week_avg_in = words[48]
            salesold_ins.sale_4week_avg_out = words[49]
            salesold_ins.sale_8week_avg_in = words[50]
            salesold_ins.sale_8week_avg_out = words[51]
            salesold_ins.sale_12week_avg_in = words[52]
            salesold_ins.sale_12week_avg_out = words[53]

            # 天气维度
            salesold_ins.templow_1 = words[54]
            salesold_ins.temphigh_1 = words[55]
            salesold_ins.weather_type_1 = words[56]
            salesold_ins.windpower_1 = words[57]
            salesold_ins.winddirect_1 = words[58]
            salesold_ins.windspeed_1 = words[59]

            salesold_ins.templow_2 = words[60]
            salesold_ins.temphigh_2 = words[61]
            salesold_ins.weather_type_2 = words[62]
            salesold_ins.windpower_2 = words[63]
            salesold_ins.winddirect_2 = words[64]
            salesold_ins.windspeed_2 = words[65]

            salesold_ins.templow_3 = words[66]
            salesold_ins.temphigh_3 = words[67]
            salesold_ins.weather_type_3 = words[68]
            salesold_ins.windpower_3 = words[69]
            salesold_ins.winddirect_3 = words[70]
            salesold_ins.windspeed_3 = words[71]

            salesold_ins.templow_4 = words[72]
            salesold_ins.temphigh_4 = words[73]
            salesold_ins.weather_type_4 = words[74]
            salesold_ins.windpower_4 = words[75]
            salesold_ins.winddirect_4 = words[76]
            salesold_ins.windspeed_4 = words[77]

            salesold_ins.templow_5 = words[78]
            salesold_ins.temphigh_5 = words[79]
            salesold_ins.weather_type_5 = words[80]
            salesold_ins.windpower_5 = words[81]
            salesold_ins.winddirect_5 = words[82]
            salesold_ins.windspeed_5 = words[83]

            salesold_ins.templow_6 = words[84]
            salesold_ins.temphigh_6 = words[85]
            salesold_ins.weather_type_6 = words[86]
            salesold_ins.windpower_6 = words[87]
            salesold_ins.winddirect_6 = words[88]
            salesold_ins.windspeed_6 = words[89]

            salesold_ins.templow_7 = words[90]
            salesold_ins.temphigh_7 = words[91]
            salesold_ins.weather_type_7 = words[92]
            salesold_ins.windpower_7 = words[93]
            salesold_ins.winddirect_7 = words[94]
            salesold_ins.windspeed_7 = words[95]

            # 时间维度
            salesold_ins.week_i_1 = words[96]
            salesold_ins.season_1 = words[97]
            salesold_ins.week_type_1 = words[98]
            salesold_ins.month_1 = words[99]
            salesold_ins.holiday_type_1 = words[100]

            salesold_ins.week_i_2 = words[101]
            salesold_ins.season_2 = words[102]
            salesold_ins.week_type_2 = words[103]
            salesold_ins.month_2 = words[104]
            salesold_ins.holiday_type_2 = words[105]

            salesold_ins.week_i_3 = words[106]
            salesold_ins.season_3 = words[107]
            salesold_ins.week_type_3 = words[108]
            salesold_ins.month_3 = words[109]
            salesold_ins.holiday_type_3 = words[110]

            salesold_ins.week_i_4 = words[111]
            salesold_ins.season_4 = words[112]
            salesold_ins.week_type_4 = words[113]
            salesold_ins.month_4 = words[114]
            salesold_ins.holiday_type_4 = words[115]

            salesold_ins.week_i_5 = words[116]
            salesold_ins.season_5 = words[117]
            salesold_ins.week_type_5 = words[118]
            salesold_ins.month_5 = words[119]
            salesold_ins.holiday_type_5 = words[120]

            salesold_ins.week_i_6 = words[121]
            salesold_ins.season_6 = words[122]
            salesold_ins.week_type_6 = words[123]
            salesold_ins.month_6 = words[124]
            salesold_ins.holiday_type_6 = words[125]

            salesold_ins.week_i_7 = words[126]
            salesold_ins.season_7 = words[127]
            salesold_ins.week_type_7 = words[128]
            salesold_ins.month_7 = words[129]
            salesold_ins.holiday_type_7 = words[130]
            # 地域维度
            salesold_ins.city_id = words[131]
            salesold_ins.week_i_1_date = words[132]
            salesold_ins = sales2_save.data_check(salesold_ins)
            return salesold_ins

if __name__=='__main__':
    loaddata_ins = Sales2LoadData()
    X,Y = loaddata_ins.load_all_data()
    Y = np.array(Y)
    X = np.array(X)
    for i in range(len(Y[0])):
        Y = Y[:,i]
        kg_ins = keras_regress.KRegress()
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        kg_ins.train(X,Y,end_date+"_"+str(i))