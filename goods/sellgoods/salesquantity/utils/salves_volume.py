# 销量预测模型   特征处理
from goods.sellgoods.salesquantity.utils import sparkdb
from goods.sellgoods.sql import sales_quantity
from pyspark.ml.feature import VectorAssembler
from goods.sellgoods.salesquantity.utils import mean_enchder
from sklearn.preprocessing import OneHotEncoder
from pyspark.sql import SparkSession
import pandas as pd
from set_config import config
sdb = sparkdb.SparkDb()
class Salves:
    sc = None
    sqlsc = None
    ss = None
    def __init__(self):
        self.sc = sdb.get_spark_context()
        self.sqlsc = sdb.get_sparksql_context(self.sc)
        self.ss =SparkSession(self.sqlsc)

    def get_data_from_mysql(self,sql):
        sql_dataf =  sdb.get_data_frame(sql,self.sqlsc,config.erp)
        return sql_dataf

    # time1  2019-07-31 2019-08-31   2019-07-31 2019-08-31
    # time2  2019-08-31 2019-09-02   2019-08-31 2019-09-02
    # 用于upc的特征训练  经过平均编码
    def generate_features(self,start_time,end_time1,end_time2):
        MeanEncoder = mean_enchder.MeanEncoder(["shop_id", "upc"], n_splits=5, target_type='regression',
                                               prior_weight_func=None)
        train_feature, MeanEncoder = self.get_train_feature(MeanEncoder, start_time, end_time1)
        predict_feature, predict_df = self.get_test_feature(MeanEncoder, end_time1, end_time2)
        return train_feature,predict_feature,predict_df

        # 用于upc的特征训练  经过平均编码

    def generate_features_predict(self, start_time, end_time1, end_time2,shop_ids = None):
        MeanEncoder = mean_enchder.MeanEncoder(["shop_id", "upc"], n_splits=5, target_type='regression',
                                               prior_weight_func=None)
        train_feature, MeanEncoder = self.get_train_feature(MeanEncoder, start_time, end_time1)
        predict_feature, predict_df = self.get_predict_feature(MeanEncoder, end_time1, end_time2,shop_ids)
        return train_feature, predict_feature, predict_df,MeanEncoder

    def get_test_feature(self,MeanEncoder,end_time1,end_time2):
        print ("get_test_feature")
        sql = sales_quantity.sql_params['upc_data_sql_test'].format(end_time1, end_time2, end_time1, end_time2)
        sql_dataf = self.get_data_from_mysql(sql)
        sql_dataf.show(10)
        sql_dataf.registerTempTable('salves_volume_day_test')
        sql_dataf = self.sqlsc.sql(
            "select * from (select T4.ai_nums as ai_day_nums,T5.ai_nums as ai_next_nums,T4.ai_shop_id as shop_id,T4.ai_upc as upc ,T4.ai_create_date as ai_day,T5.ai_create_date as ai_nextday,T5.ai_week_date as ai_weekday from salves_volume_day_test T4 left join salves_volume_day_test T5 on T4.ai_shop_id  = T5.ai_shop_id  and T4.ai_upc = T5.ai_upc and T4.ai_next_date = T5.ai_create_date ) T6 where T6.ai_day_nums is not null and T6.ai_next_nums is not null and T6.shop_id is not null and T6.ai_day is not null and T6.ai_nextday is not null and T6.upc != '' and T6.ai_weekday is not null and T6.ai_day_nums < 100 and T6.ai_next_nums < 100 ")
        sql_dataf.show(10)
        df = sql_dataf.select(sql_dataf.shop_id.cast("double"),
                                     sql_dataf.ai_day_nums.cast("double"), sql_dataf.ai_next_nums.cast("double"),
                                     sql_dataf.upc.cast("double"), sql_dataf.ai_weekday.cast("int"),sql_dataf.ai_day.cast("string"),sql_dataf.ai_nextday.cast("string"))
        sql_dataf = df.select('shop_id', 'upc','ai_day_nums','ai_weekday','ai_next_nums')
        sql_dataf.show(10)
        sql_dataf = sql_dataf.toPandas()
        sql_dataf = MeanEncoder.transform(sql_dataf)
        value = sql_dataf.values.tolist()
        column = list(sql_dataf.columns)
        sql_dataf = self.sqlsc.createDataFrame(value, column)
        assembler = VectorAssembler(inputCols=["ai_day_nums", "shop_id_pred", "upc_pred", "ai_weekday"],
                                    outputCol="features")
        output = assembler.transform(sql_dataf)
        test_feature = output.select("features", "ai_next_nums").toDF('features', 'label')
        feature = output.select("features")
        print(feature.show(10))
        return test_feature, df

    def get_predict_feature(self,MeanEncoder,end_time1,end_time2,shop_ids=None):
        print ("get_predict_feature")
        if shop_ids is not None:
            sql = sales_quantity.sql_params['upc_data_sql_predict'].format(end_time1,end_time2,end_time1,end_time2)
        else:
            sql = sales_quantity.sql_params['upc_data_sql_test'].format(end_time1, end_time2, end_time1, end_time2)
        sql_dataf = self.get_data_from_mysql(sql)
        sql_dataf.show(10)
        sql_dataf.registerTempTable('salves_volume_day_predict')
        sql_dataf = self.sqlsc.sql(
            "select ai_nums as ai_day_nums,ai_shop_id as shop_id,ai_upc as upc ,ai_create_date as ai_day,ai_next_date as ai_next_day,ai_week_date as ai_weekday from salves_volume_day_predict  where ai_nums is not null and ai_shop_id is not null and ai_create_date is not null and ai_next_date is not null and ai_upc != '' and ai_week_date is not null and ai_nums < 100 ")
        sql_dataf.show(10)
        df = sql_dataf.select(sql_dataf.shop_id.cast("double"),
                                     sql_dataf.ai_day_nums.cast("double"),
                                     sql_dataf.upc.cast("double"), sql_dataf.ai_weekday.cast("int"),sql_dataf.ai_day.cast("string"),sql_dataf.ai_next_day.cast("string"))
        sql_dataf = df.select('shop_id', 'upc','ai_day_nums','ai_weekday')
        sql_dataf.show(10)
        sql_dataf = sql_dataf.toPandas()
        sql_dataf = MeanEncoder.transform(sql_dataf)
        value = sql_dataf.values.tolist()
        column = list(sql_dataf.columns)
        sql_dataf = self.sqlsc.createDataFrame(value, column)
        assembler = VectorAssembler(inputCols=["ai_day_nums", "shop_id_pred", "upc_pred", "ai_weekday"],
                                    outputCol="features")
        output = assembler.transform(sql_dataf)
        predict_feature = output.select("features").toDF('features')
        feature = output.select("features")
        print(feature.show(10))
        return predict_feature, df

    def get_mean_encode(self,start_time,end_time1):
        print("get_mean_code")
        MeanEncoder = mean_enchder.MeanEncoder(["shop_id", "upc"], n_splits=5, target_type='regression',
                                               prior_weight_func=None)
        sql = sales_quantity.sql_params['upc_data_sql'].format(start_time, end_time1, start_time, end_time1)
        sql_dataf = self.get_data_from_mysql(sql)
        sql_dataf.show(10)
        print(sql_dataf.count())
        sql_dataf.registerTempTable('salves_volume_day')
        sql_dataf = self.sqlsc.sql(
            "select * from (select T4.ai_nums as ai_day_nums,T5.ai_nums as ai_next_nums,T4.ai_shop_id as shop_id,T4.ai_upc as upc ,T4.ai_create_date as ai_day,T5.ai_create_date as ai_nextday,T5.ai_week_date as ai_weekday from salves_volume_day T4 left join salves_volume_day T5 on T4.ai_shop_id  = T5.ai_shop_id  and T4.ai_upc = T5.ai_upc and T4.ai_next_date = T5.ai_create_date ) T6 where T6.ai_day_nums is not null and T6.ai_next_nums is not null and T6.shop_id is not null and T6.ai_day is not null and T6.ai_nextday is not null and T6.upc != '' and T6.ai_weekday is not null and T6.ai_day_nums < 100 and T6.ai_next_nums < 100 ")
        sql_dataf.show(10)
        # enc = OneHotEncoder(categorical_features="ai_weekday")
        # MeanEncoder = mean_enchder.MeanEncoder(["shop_id", "upc"], n_splits=5, target_type='regression',
        #                                        prior_weight_func=None)
        sql_dataf = sql_dataf.select(sql_dataf.shop_id.cast("double"),
                                     sql_dataf.ai_day_nums.cast("double"), sql_dataf.ai_next_nums.cast("double"),
                                     sql_dataf.upc.cast("double"), sql_dataf.ai_weekday.cast("int"))
        # y_dataf = sql_dataf.select("ai_next_nums")
        sql_dataf = sql_dataf.toPandas()
        # y_dataf = y_dataf.toPandas()
        # sql_dataf = enc.fit(pd.Series(sql_dataf['ai_weekday']).values.reshape(-1,1))
        sql_dataf = MeanEncoder.fit_transform(sql_dataf, sql_dataf['ai_next_nums'])
        return MeanEncoder


    def get_train_feature(self,MeanEncoder,start_time,end_time1):
        print("get_train_feature")
        sql = sales_quantity.sql_params['upc_data_sql'].format(start_time,end_time1,start_time,end_time1)
        sql_dataf = self.get_data_from_mysql(sql)
        sql_dataf.show(10)
        print(sql_dataf.count())
        sql_dataf.registerTempTable('salves_volume_day')
        sql_dataf = self.sqlsc.sql(
            "select * from (select T4.ai_nums as ai_day_nums,T5.ai_nums as ai_next_nums,T4.ai_shop_id as shop_id,T4.ai_upc as upc ,T4.ai_create_date as ai_day,T5.ai_create_date as ai_nextday,T5.ai_week_date as ai_weekday from salves_volume_day T4 left join salves_volume_day T5 on T4.ai_shop_id  = T5.ai_shop_id  and T4.ai_upc = T5.ai_upc and T4.ai_next_date = T5.ai_create_date ) T6 where T6.ai_day_nums is not null and T6.ai_next_nums is not null and T6.shop_id is not null and T6.ai_day is not null and T6.ai_nextday is not null and T6.upc != '' and T6.ai_weekday is not null and T6.ai_day_nums < 100 and T6.ai_next_nums < 100 ")
        sql_dataf.show(10)
        # enc = OneHotEncoder(categorical_features="ai_weekday")
        # MeanEncoder = mean_enchder.MeanEncoder(["shop_id", "upc"], n_splits=5, target_type='regression',
        #                                        prior_weight_func=None)
        sql_dataf = sql_dataf.select(sql_dataf.shop_id.cast("double"),
                                     sql_dataf.ai_day_nums.cast("double"), sql_dataf.ai_next_nums.cast("double"),
                                     sql_dataf.upc.cast("double"), sql_dataf.ai_weekday.cast("int"))
        # y_dataf = sql_dataf.select("ai_next_nums")
        sql_dataf = sql_dataf.toPandas()
        # y_dataf = y_dataf.toPandas()
        # sql_dataf = enc.fit(pd.Series(sql_dataf['ai_weekday']).values.reshape(-1,1))
        sql_dataf = MeanEncoder.fit_transform(sql_dataf, sql_dataf['ai_next_nums'])
        value = sql_dataf.values.tolist()
        column = list(sql_dataf.columns)
        sql_dataf = self.sqlsc.createDataFrame(value, column)
        sql_dataf.show(10)
        assembler = VectorAssembler(inputCols=["ai_day_nums", "shop_id_pred", "upc_pred", "ai_weekday"],
                                    outputCol="features")
        output = assembler.transform(sql_dataf)
        train_feature = output.select("features", "ai_next_nums").toDF('features', 'label')
        print(train_feature.show(10))
        return train_feature, MeanEncoder


if __name__=='__main__':
    sql = "(SELECT  count(1) FROM   ( SELECT sum(T2.t1_nums) AS ai_nums,  T2.t1_shop_id AS ai_shop_id,T3.upc AS ai_upc, T2.t1_create_date AS ai_create_date, DATE_FORMAT(  from_unixtime(  unix_timestamp(   DATE_FORMAT(  T2.t1_create_date,'%Y-%m-%d' )  ) + 24 * 3600 ), '%Y-%m-%d'          ) AS ai_next_date       FROM            (               SELECT                  sum(T1.nums) AS t1_nums,                    T1.shop_id AS t1_shop_id,                   T1.goods_id,                    T1.create_date AS t1_create_date                FROM                    (                       SELECT                          number nums,                            shop_id,                            goods_id,                           DATE_FORMAT(create_time, '%Y-%m-%d') create_date                        FROM                            payment_detail                      WHERE                           shop_id IS NOT NULL                         AND goods_id IS NOT NULL                        AND number > 0                      AND create_time > '2019-06-01 00:00:00'                         AND create_time < '2019-09-01 00:00:00'                         AND payment_id IN (                             SELECT DISTINCT                                 (payment.id)                            FROM                                payment                             WHERE                               payment.type != 50                          AND create_time > '2019-06-01 00:00:00'                             AND create_time < '2019-09-01 00:00:00'                         )                   ) T1                GROUP BY                    T1.shop_id,                     T1.goods_id,                    T1.create_date          ) T2        LEFT JOIN shop_goods T3 ON T2.t1_shop_id = T3.shop_id       AND T2.goods_id = T3.goods_id       WHERE           T3.upc != ''        GROUP BY            T2.t1_create_date,          T2.t1_shop_id,          T3.upc  ) T8) tmp "
    salves_ins = Salves()
    sql_dataf = salves_ins.get_data_from_mysql(sql)
    sql_dataf.show(10)