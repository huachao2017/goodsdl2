from goods.sellgoods.salesquantity.model import keras_regress
if __name__=='__main__':
    kr_ins = keras_regress.KRegress()
    # kr_ins.train()
    X_pridect, X, Y, ss_Y, mm_Y = kr_ins.predict('2019-11-25')
    kr_ins.save_file(X_pridect, X, Y, ss_Y, mm_Y)