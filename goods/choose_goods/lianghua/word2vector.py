# -*- coding: utf-8 -*-

import pymysql,json
import jieba.posseg as pseg
from gensim.models import word2vec
import numpy as np
import pandas as pd
# from redis import *
# from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import OneHotEncoder
# from scipy import sparse
import jieba.analyse
import pickle
import datetime,time

def word_vec():
    conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl', charset="utf8",port=3306, use_unicode=True)
    # conn = connections['default']
    cursor = conn.cursor()
    model = word2vec.Word2Vec.load("goods/choose_goods/lianghua/resource/data_words_jieba.model")
    # print(r'\u626c\u5dde'.encode().decode('unicode-escape'))
    jieba.analyse.set_stop_words('goods/choose_goods/lianghua/resource/stop_words.txt')

    begin = datetime.date(2009, 6, 15)
    end = datetime.date(2020, 2, 22)
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        print(d.strftime("%Y%m%d"))
        date_str = str(d.strftime("%Y%m%d"))
        search_sql = 'select date,title,content from cctv_news where date="{}" '.format(date_str)
        cursor.execute(search_sql)
        data = cursor.fetchone()
        # data = [1,'昨天下午，一艘货轮行驶至武汉白沙洲洲','遭遇突如其来的狂风，船上28个装满鞭炮等货']
        arr = np.zeros(128)
        keywords = jieba.analyse.extract_tags(data[1]+data[2], topK=30, withWeight=True)
        for w in keywords:
            vec = np.array(model[w[0]]).reshape(1, 128)  # 原本是128x1的数组
            arr = np.vstack((arr, vec))

        vv = arr[1:]
        v = vv.reshape(1,-1)
        print(str(np.matrix.tolist(v)))

        insert_sql = "insert into cctv_news(vec) values ('{}')".format(str(np.matrix.tolist(v)))
        cursor.execute(insert_sql)
        conn.commit()

        d += delta

if __name__ == '__main__':
    word_vec()




