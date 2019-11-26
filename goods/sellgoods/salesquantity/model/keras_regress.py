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
class KRegress:
    # exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    def train(self):
        loaddata_ins = sales2_loaddata.Sales2LoadData()
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        model = self.get_model()
        checkpoint = ModelCheckpoint(keras_model_path +end_date+ "_1.h5",
                                     monitor='val_loss',
                                     save_weights_only=True, save_best_only=True, period=1)
        model.fit_generator(generator = loaddata_ins.load_all_data(0.7),steps_per_epoch=39,epochs=50,validation_data=loaddata_ins.load_all_data(0.3),validation_steps=39,verbose=1 ,callbacks=[checkpoint])


    def load_model(self,filepath):
       return load_model(filepath)

    def get_model(self):
        model = Sequential()
        model.add(Dense(50,input_dim=129,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(1,activation='linear'))
        model.compile(loss='mse',optimizer='adam')
        return model

    def predict(self):
        load_model()

if __name__=='__main__':
    kr_ins = KRegress()
    kr_ins.train()