from goods.sellgoods.salesquantity.utils import salves_volume
import datetime
import math
from goods.sellgoods.salesquantity.model import regressor
from set_config import config
from goods.sellgoods.salesquantity.local_util import save_mysql_sales
from pyspark.ml.feature import VectorAssembler
regressor_model_path = config.shellgoods_params['regressor_model_path']
online_model_name = config.shellgoods_params['online_model_name']
predict_ext_days = config.shellgoods_params['predict_ext_days']
import time
def get_nextday_sales(shop_ids,upcs,day,days_sales,salves_ins,MeanEncoder,days=None):
    if salves_ins is None:
        salves_ins = salves_volume.Salves()
        sqlsc = salves_ins.sqlsc
    sqlsc = salves_ins.sqlsc
    exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    start_time = str((datetime.datetime.strptime(day, "%Y-%m-%d")+ datetime.timedelta(days=-30)).strftime("%Y-%m-%d"))
    end_time = str((datetime.datetime.strptime(day, "%Y-%m-%d")+ datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    if MeanEncoder is None:
        MeanEncoder = salves_ins.get_mean_encode(start_time,end_time)
    mean_encode_ins = MeanEncoder
    regressor_ins = regressor.Regressor()
    dt_model = regressor_ins.load_model(regressor_model_path[online_model_name]+str(exe_time))
    predict_tmps = None
    predicts_info_ext = {}
    if days is None:
        days = predict_ext_days
    for i in range(1, days+1):
        predict_tmps = days_sales
        ai_nextday = str(
            (datetime.datetime.strptime(day, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        predicts = save_mysql_sales.get_ext_predict_day(shop_ids, upcs, ai_nextday, dt_model, mean_encode_ins, predict_tmps, sqlsc)
        predict_tmps = predicts
        predicts_info_ext[i]=predict_tmps
    predicts_ext = []
    for i in range(len(upcs)):
        predicts_e = []
        for key in predicts_info_ext:
            predicts_e.append(predicts_info_ext[key][i])
        predicts_ext.append(predicts_e)
    predicts_info = []
    for shop_id,upc,predicts in zip(shop_ids,upcs,predicts_ext):
        predict_info = {}
        predict_info['shop_id'] = shop_id
        predict_info['upc'] = upc
        predict_info['predict_day_sales'] = predicts
        predicts_info.append(predict_info)
    return predicts_info


