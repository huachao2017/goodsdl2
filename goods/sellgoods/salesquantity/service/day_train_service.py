from goods.sellgoods.salesquantity.model import regressor
from goods.sellgoods.salesquantity.utils import salves_volume
import os
import shutil
from set_config import config
import time
import datetime
from goods.sellgoods.salesquantity.service import generate_order_2saler_add,generate_order_2saler_add_day
from goods.sellgoods.salesquantity.local_util import file_util
from goods.sellgoods.salesquantity.local_util import save_mysql_sales
regressor_model_path = config.shellgoods_params['regressor_model_path']
test_data_save_path = config.shellgoods_params['test_data_save_path']
predict_shop_ids = config.shellgoods_params['predict_shop_ids']
day_order_time_weekday = config.shellgoods_params['day_order_time_weekday']
salves_ins = salves_volume.Salves()
regressor_ins = regressor.Regressor()
from set_config import config
import datetime
def train_regressor(model_time):
    model_t = datetime.datetime.strptime(model_time, "%Y-%m-%d")
    test_time = str((model_t + datetime.timedelta(days=-1)).strftime("%Y-%m-%d"))
    mon_1 = str((datetime.datetime.strptime(test_time, "%Y-%m-%d")+ datetime.timedelta(days=-30)).strftime("%Y-%m-%d"))
    # end_d = str((datetime.datetime.strptime(test_time, "%Y-%m-%d")+ datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
    train_features,test_features,test_d,MeanEncoder = salves_ins.generate_features_predict(mon_1,test_time,model_t,predict_shop_ids)
    sc = salves_ins.sc
    sqlsc = salves_ins.sqlsc
    # # 决策树回归模型
    dt_model = regressor_ins.decision_tree_train(train_features)
    print("dt:" + str(dt_model))
    rmse,r2,result = regressor_ins.evaluate(train_features, dt_model)
    print("dt test rootMeanSquaredError:" + str(rmse))
    print("dt test r2::" + str(r2))
    test_path =  test_data_save_path+test_time
    model_path = regressor_model_path['decision_tree']+model_time
    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
    regressor_ins.save_model(model_path, dt_model)
    result = dt_model.transform(test_features)
    result = result.select('prediction')
    test_d = test_d.select("shop_id","upc","ai_weekday","ai_day","ai_next_day","ai_day_nums")
    save_mysql_sales.save_df(test_d,result,dt_model,MeanEncoder,sqlsc)
    # file_util.save_test_dataRdd(test_d, result, test_path)
    generate_order_2saler_add.generate()
    if datetime.datetime.now().weekday()+1 in day_order_time_weekday:
        generate_order_2saler_add_day.generate()
    print("###########################################################")


def train(n):
    exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    for i in range(n):
        model_time = str((datetime.datetime.strptime(exe_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        print (model_time)
        train_regressor(model_time)



if __name__=='__main__':
    train(1)