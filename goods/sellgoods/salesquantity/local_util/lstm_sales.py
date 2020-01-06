from sklearn.preprocessing import LabelEncoder
import pandas as pd
from datetime import datetime
class Lstm_Sales:
    def load_data(self):
        data_path = "D:\\opt\\data\\linear\\lstm_sales\\sales_train.CSV"
        data = pd.read_csv(data_path, sep = ",",parse_dates=['create_date'])
        data['create_date'] = pd.to_datetime(data['create_date'],errors='coerce')
        # print (data['create_date'].dt.day.head(10))
        data = data.assign(day=data.create_date.dt.day,
                           month=data.create_date.dt.month,
                           year=data.create_date.dt.year)
        print (data.goods_name.head(10))

        cat_features = ['city', 'goods_name', 'weather_type', 'winddirect']
        encoder = LabelEncoder()

        # Apply the label encoder to each column
        encoded = data[cat_features].apply(encoder.fit_transform)
        encoded.head(10)

        data = data[['shop_id', 'goods_id', 'upc', 'goods_name', 'price', 'city',
                     'city_id', 'week_date', 'first_cate_id', 'second_cate_id', 'third_cate_id',
                     'temphigh', 'templow', 'windspeed', 'windpower', 'holiday_type', 'num', 'day', 'month',
                     'year']].join(encoded)

        data.head(10)

if __name__=='__main__':
    ls_ins = Lstm_Sales()
    ls_ins.load_data()
