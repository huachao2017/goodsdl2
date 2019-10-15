from goods.sellgoods.salesquantity.model import regressor
from goods.sellgoods.salesquantity.utils import salves_volume
import os
import shutil
from set_config import config
from goods.sellgoods.salesquantity.utils import file_util
regressor_model_path = config.shellgoods_params['regressor_model_path']
test_data_save_path = config.shellgoods_params['test_data_save_path']
salves_ins = salves_volume.Salves()
regressor_ins = regressor.Regressor()
import datetime
def train_regressor(model_time):
    # model_time = '2019-08-15'
    # test_time = '2019-08-31 '
    model_t = datetime.datetime.strptime(model_time, "%Y-%m-%d")
    test_time = str((model_t + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    print (test_time)
    mon_1 = str((datetime.datetime.strptime(test_time, "%Y-%m-%d")+ datetime.timedelta(days=-30)).strftime("%Y-%m-%d"))
    print (mon_1)
    end_d = str((datetime.datetime.strptime(test_time, "%Y-%m-%d")+ datetime.timedelta(days=2)).strftime("%Y-%m-%d"))
    print (end_d)
    train_features,test_features,test_d = salves_ins.generate_features5(mon_1,test_time,end_d)
    sc = salves_ins.sc
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
    # result = result.select("prediction")
    test_d = test_d.select("shop_id","upc","ai_weekday","ai_day","ai_nextday","ai_day_nums","ai_next_nums")
    file_util.save_test_dataRdd(test_d,result,test_path)
    print("###########################################################")


def train(n):
    train_model_time = '2019-08-15'
    for i in range(n):
        model_time = str((datetime.datetime.strptime(train_model_time, "%Y-%m-%d") + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        print (model_time)
        train_regressor(model_time)



if __name__=='__main__':
    train(15)