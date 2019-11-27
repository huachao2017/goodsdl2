import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from keras.callbacks import ModelCheckpoint
from keras import regularizers
from set_config import config
from keras.models import load_model
from goods.sellgoods.salesquantity.local_util import sales2_loaddata

import time
keras_model_path = config.shellgoods_params['regressor_model_path']['keras_regress']
keras_day_sales_model_1 = config.shellgoods_params['keras_day_sales_model_1']
class KRegress:
    # exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    def train(self):
        loaddata_ins = sales2_loaddata.Sales2LoadData()
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        model = self.get_model()
        for i in [0,2,3,4,5,6]:
            checkpoint = ModelCheckpoint(keras_model_path +end_date+ "_"+str(i)+".h5",
                                         monitor='val_loss',
                                         save_weights_only=True, save_best_only=True, period=1)
            model.fit_generator(generator = loaddata_ins.load_all_data(data_split=0.7,n=i),steps_per_epoch=39,epochs=50,validation_data=loaddata_ins.load_all_data(data_split=0.3,n=i),validation_steps=39,verbose=1 ,callbacks=[checkpoint])


    def load_model(self,filepath):
        return self.get_model().load_weights(filepath)

    def get_model(self):
        model = Sequential()
        model.add(Dense(50,input_dim=129,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(1,activation='linear'))
        model.compile(loss='mse',optimizer='adam')
        return model

    def predict(self,dateweek_one=None):
        model = self.load_model(keras_day_sales_model_1)
        loaddata_ins = sales2_loaddata.Sales2LoadData()
        X, Y, X_p, Y_p, ss_X, ss_Y, mm_X, mm_Y = loaddata_ins.load_predict_data(dateweek_one)
        print (X_p)
        X_pridect = model.predict(X_p)
        X_pridect = ss_Y.inverse_transform(X_pridect)
        X_pridect = mm_Y.inverse_transform(X_pridect)
        return X_pridect,X,Y

    def save_file(self,X_pridect,X,Y):
        with open("1.txt","a+") as f:
            for x_pre,x_t,y_t in zip(X_pridect,X,Y):
                line = str(str(x_t[0])+","+str(x_t[1])+","+str(x_pre[0])+","+str(y_t))
                f.write(line+"\n")


if __name__=='__main__':
    kr_ins = KRegress()
    kr_ins.train()

