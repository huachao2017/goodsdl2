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


import time
keras_model_path = config.shellgoods_params['regressor_model_path']['keras_regress']
class KRegress:
    # exe_time = str(time.strftime('%Y-%m-%d', time.localtime()))
    def train(self,X,Y,exe_time):
        train_samples = len(Y)
        Y = np.array(Y)
        X = np.array(X)
        mm_X = MinMaxScaler()
        X = mm_X.fit_transform(X)
        mm_Y = MinMaxScaler()
        Y = mm_Y.fit_transform(Y.reshape(train_samples,1))
        # 数据标准化
        ss_X = StandardScaler()
        X = ss_X.fit_transform(X)
        ss_Y = StandardScaler()
        Y = ss_Y.fit_transform(Y)
        model = self.get_model()
        checkpoint = ModelCheckpoint(keras_model_path +exe_time+ ".h5",
                                     monitor='val_loss',
                                     save_weights_only=True, save_best_only=True, period=1)
        model.fit(X,Y,epochs=500,batch_size = 2000,verbose=1,validation_split = 0.3 ,callbacks=[checkpoint])


    def load_model(self,path,exe_time):
       return load_model(path+exe_time+".h5")

    def get_model(self):
        model = Sequential()
        model.add(Dense(50,input_dim=129,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50,activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(50, activation='relu',kernel_regularizer=regularizers.l2(0.01),use_bias=True))
        model.add(Dense(1,activation='linear'))
        model.compile(loss='mse',optimizer='adam')
        return model

