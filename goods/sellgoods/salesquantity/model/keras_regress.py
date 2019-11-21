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
    def train(self,X,Y,X_test,Y_test,exe_time):
        train_samples = len(Y)
        # test_samples = len(Y_test)
        Y = np.array(Y)
        X = np.array(X)
        # X_test = np.array(X_test)
        # Y_test = np.array(Y_test)
        # 数据归一化
        mm_X = MinMaxScaler()
        X = mm_X.fit_transform(X)
        mm_Y = MinMaxScaler()
        Y = mm_Y.fit_transform(Y.reshape(train_samples,1))
        # Y = mm_Y.inverse_transform(Y)  归一化还原
        # X_test = mm_X.transform(X_test)
        # Y_test = mm_Y.transform(Y_test.reshape(test_samples,1))

        # 数据标准化
        ss_X = StandardScaler()
        X = ss_X.fit_transform(X)
        # origin_data = ss.inverse_transform(std_data)  标准化还原
        ss_Y = StandardScaler()
        Y = ss_Y.fit_transform(Y)
        # X_test = ss_X.transform(X_test)
        # Y_test = ss_Y.transform(Y_test)
        # sample_num = len(Y)
        # scalarX,scalarY = MinMaxScaler(),MinMaxScaler()
        #
        #
        # scalarX.fit(X)
        # scalarY.fit(Y.reshape(sample_num,1))
        # X = scalarX.transform(X)
        # Y = scalarY.transform(Y.reshape(sample_num,1))
        model = self.get_model()
        checkpoint = ModelCheckpoint(keras_model_path +exe_time+ ".h5",
                                     monitor='val_loss',
                                     save_weights_only=True, save_best_only=True, period=1)
        model.fit(X,Y,epochs=500,batch_size = 2000,verbose=1,validation_split = 0.3 ,callbacks=[checkpoint])
        # score = model.evaluate(X_test, Y_test, verbose=1)
        # print('Test score:', str(score))
        # X_pridect = model.predict(X_test)
        # X_pridect = ss_Y.inverse_transform(X_pridect)
        # X_pridect =  mm_Y.inverse_transform(X_pridect)
        # return X_pridect

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

