import math
import datetime
from pyspark.ml.feature import VectorAssembler
from set_config import config
from goods.sellgoods.salesquantity.utils import mysql_util
import time
ai = config.ai
predict_ext_days = config.shellgoods_params['predict_ext_days']
def save_df(data_frame,label,model,mean_encode_ins,sqlsc):
    data = []
    shop_ids = []
    upcs=[]
    ai_weekdays=[]
    ai_days= []
    ai_day_numss = []
    ai_nextdays=[]
    predict_next_days = []
    for feature,label in zip(data_frame.collect(),label.collect()):
        shop_id = int(feature[0])
        upc = int(feature[1])
        ai_weekday = int (feature[2])
        ai_day = str(feature[3])
        ai_nextday = str(feature[4])
        ai_day_nums = float(feature[5])
        predict = int(math.floor(label[0]))
        shop_ids.append(shop_id)
        upcs.append(upc)
        ai_weekdays.append(ai_weekday)
        ai_days.append(ai_day)
        ai_day_numss.append(int(ai_day_nums))
        ai_nextdays.append(ai_nextday)
        predict_next_days.append(predict)
    predicts_info = {}
    predict_next_days_copy = predict_next_days.copy()
    for i in range(0,predict_ext_days):
        ai_nextday = ai_nextdays[0]
        ai_nextday = str((datetime.datetime.strptime(ai_nextday, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        predicts = get_ext_predict_day(shop_ids,upcs,ai_nextday,model,mean_encode_ins,predict_next_days_copy,sqlsc)
        predict_next_days_copy = predicts
        predicts_info[i] = predict_next_days_copy
    predicts_ext = []
    for i in range(len(upcs)):
        predicts_e = []
        for key in predicts_info:
             predicts_e.append(predicts_info[key][i])
        predicts_ext.append(predicts_e)
    exe_time1 = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    for shop_id,upc,ai_weekday,ai_day,ai_day_nums,ai_nextday,predict,predicts1 in zip(shop_ids,upcs,ai_weekdays,ai_days,ai_day_numss,ai_nextdays,predict_next_days,predicts_ext):
        data.append((shop_id,upc,ai_weekday,ai_day,ai_day_nums,ai_nextday,predict,str(predicts1),str(exe_time1)))
    mysql_ins = mysql_util.MysqlUtil(ai)
    del_sql = "delete from goods_ai_sales_goods where next_day = {0}"
    del_sql = del_sql.format("'"+data[0][5]+"'")
    sql = "insert into goods_ai_sales_goods (shopid,upc,day_week,day,day_sales,next_day,nextday_predict_sales,nextdays_predict_sales,create_time) value(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    print(sql)
    print (data[0])
    mysql_ins.delete_sql(del_sql)
    print ("delete predict sales sucess")
    print (del_sql)
    mysql_ins.insert_many_sql(data,sql)
    print ("insert predict sales sucess")
    mysql_ins.cursor.close()
    mysql_ins.conn.close()

def get_ext_predict_day(shop_ids,upcs,ai_nextday,model,mean_encode_ins,predicts,sqlsc):
    print("get_ext_predict_day")
    features = []
    columns = ['shop_id', 'upc', 'ai_day_nums', 'ai_weekday']
    for shop_id,upc,predict in zip(shop_ids,upcs,predicts):
        ai_day = ai_nextday
        ai_day_nums = predict
        ai_weekday = int(datetime.datetime.strptime(ai_day, '%Y-%m-%d').strftime("%w"))
        features.append([shop_id,upc,ai_day_nums,ai_weekday])
    sql_dataf = sqlsc.createDataFrame(features, columns)
    sql_dataf.show(10)
    sql_dataf = sql_dataf.toPandas()
    sql_dataf = mean_encode_ins.transform(sql_dataf)
    value = sql_dataf.values.tolist()
    column = list(sql_dataf.columns)
    sql_dataf = sqlsc.createDataFrame(value, column)
    assembler = VectorAssembler(inputCols=["ai_day_nums", "shop_id_pred", "upc_pred", "ai_weekday"],
                                outputCol="features")
    output = assembler.transform(sql_dataf)
    predict_feature = output.select("features").toDF('features')
    result = model.transform(predict_feature)
    result = result.select('prediction')
    predict1s = []
    result.show(10)
    for label in result.collect():
        predict1 = int(math.floor(label[0]))
        predict1s.append(predict1)
    return predict1s



def  save_oreder(shop_upc_ordersales):
    exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    exe_time1 = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    data = []
    for shop_id in shop_upc_ordersales:
        upc_ordersales = shop_upc_ordersales[shop_id]
        for upc in upc_ordersales:
            (order_sale, predict_sale, min_stock, max_stock, stock) = upc_ordersales[upc]
            data.append((shop_id,upc,order_sale, predict_sale, min_stock, max_stock, stock,exe_time,exe_time1))
    mysql_ins = mysql_util.MysqlUtil(ai)

    del_sql = "delete from goods_ai_sales_order where create_date = {0}"
    del_sql = del_sql.format("'"+exe_time+"'")
    sql = "insert into goods_ai_sales_order (shopid,upc,order_sale, predict_sale, min_stock, max_stock, stock,create_date,create_time) value(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    print(sql)
    print(data[0])
    mysql_ins.delete_sql(del_sql)
    print ("delete goods_ai_sales_order sucess")
    print (del_sql)
    mysql_ins.insert_many_sql(data, sql)
    print ("insert into goods_ai_sales_order sucess")
    mysql_ins.cursor.close()
    mysql_ins.conn.close()