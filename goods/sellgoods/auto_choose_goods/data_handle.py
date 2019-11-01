# -*- coding: utf-8 -*-
import pymysql,json
import numpy as np
import pandas as pd
# from redis import *
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from scipy import sparse
import pickle
from goods.sellgoods.salesquantity.utils import sparkdb
from goods.sellgoods.sql import sales_quantity
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.regression import LabeledPoint,Vectors
from goods.sellgoods.salesquantity.utils import mean_enchder
from sklearn.preprocessing import OneHotEncoder
from pyspark.sql import SparkSession
import pandas as pd
import os
import pymysql
# os.environ['JAVA_HOME']='C:\Program Files\Java\jdk1.8.0_211'
sdb = sparkdb.SparkDb()



class Sales:
    """
    利用spark进行数据的读取
    """
    sc = None
    sqlsc = None
    ss = None
    def __init__(self):
        self.sc = sdb.get_spark_context()
        self.sqlsc = sdb.get_sparksql_context(self.sc)
        self.ss =SparkSession(self.sqlsc)

        # lines = self.sc.textFile('README.md')
        # lines.conut()
    def get_data_from_mysql(self,sql):
        sql_dataf =  sdb.get_data_frame(sql,self.sqlsc)
        return sql_dataf



class HandleData():

    sql = "select p.shop_id,g.upc,sum(p.amount) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '2019-10-16 00:00:00' group by g.upc,p.shop_id order by sum(p.amount) desc limit 30;"
    conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',
                           charset="utf8", port=3300, use_unicode=True)

    def __init__(self):
        self.cursor = self.conn.cursor()
    def get_data(self):

        # self.cursor.execute(self.sql)
        # results = self.cursor.fetchall()
        # print(results)
        # data = []
        # for result in results:
        #     data.append(result)
        # return data[:500]

        data_df = pd.read_sql(self.sql, self.conn)
        data_df.to_csv("user_item_rate.csv",header=False,index=False)
        # pickle.dump(data_df, open("item_user_rate_time.txt", "wb"))

        return data_df

# conn = pymysql.connect('123.103.16.19', 'readonly ', 'fxiSHEhui2018@)@)', 'dmstore', charset="utf8", use_unicode=True)
# cursor = conn.cursor()
# # search_sql = 'select resume_id,resume_text from ald_resume_text where id<1000 and id >0 and `resume_text` not REGEXP "^[{]" '
# search_sql = 'SELECT b.id,c.resume_text,a.work_years,a.max_degree,d.salary_low,d.salary_high FROM ald_personal_info AS a LEFT JOIN ald_resume AS b ON a.id = b.person_id LEFT JOIN ald_resume_text AS c ON c.resume_id = b.id LEFT JOIN ald_desired_position as d on d.resume_id = b.id where c.resume_text not REGEXP "^[{]" and d.salary_mode="元/月" limit 10000'
# # cursor.execute(search_sql)
# # data_ori = cursor.fetchall()
#
def word_vec(data_df):
    model = word2vec.Word2Vec.load("../resource/data_words_jieba.model")
    # print(r'\u626c\u5dde'.encode().decode('unicode-escape'))
    arr = np.zeros(100)
    print(type(data_df))
    for index,row in data_df.iterrows():

        jieba.analyse.set_stop_words('../resource/stop_words.txt')
        keywords = jieba.analyse.extract_tags(row['resume_text'], topK=50, withWeight=True,
                                              allowPOS=('j', 'l', 'n', 'nt', 'nz', 'vn', 'eng'))  #这几个性质的词比较有用

        vecs = np.zeros((1, 100))
        weights = 0
        for w in keywords:
            try:
                vec = np.array(model[w[0]]).reshape(1, 100)   #原本是100x1的数组
                weight = w[1]       # TF-IDF值
                vecs += vec * weight
                weights += weight
            except:
                continue

        vector = vecs / weights


        arr = np.vstack((arr,vector))
        # b = np.savetxt('a.csv', d[i[0]].reshape(-1,100), fmt='%f', delimiter=None)
    print(arr)

    # dd = pd.DataFrame(arr[1:], index=[r['id'] for i,r in data_df.iterrows()])
    dd = pd.DataFrame(arr[1:])
    print(dd)
    return dd

def to_one(data_df):
    enc = OneHotEncoder()
    ss = StandardScaler()
    # data_df[['work_years','max_degree','salary_low','salary_high','salary_ave']] = ss.fit_transform(data_df[['work_years','max_degree','salary_low','salary_high','salary_ave']])
    # arr = ss.fit_transform(data_df[['100', '101', '102']])
    arr = ss.fit_transform(data_df)

    # trainx = data_df[['id', 'person_age', 'work_years']]
    # for feature in ['person_sex', 'max_degree']:
    #     enc.fit(data_df[feature].values.reshape(-1, 1))
    #     kkk1 = enc.transform(data_df[feature].values.reshape(-1, 1))
    #     print(trainx.shape)
    #     print(kkk1.shape)
    #     trainx = sparse.hstack((trainx, kkk1))
    # print(trainx.toarray())
    # return data_df[['work_years','max_degree','salary_low','salary_high','salary_ave']]
    # return pd.DataFrame(arr, index=[i for i,r in data_df.iterrows()])
    return pd.DataFrame(arr)

def salary_ave(data_df):
    low = data_df['salary_low'].apply(pd.to_numeric,errors='ignore')
    high = data_df['salary_high'].apply(pd.to_numeric,errors='ignore')
    print(type(low))
    print(low)
    print(low.shape)
    arr = (low + high) / 2
    data_df['salary_ave'] = arr
    # arr1 = np.array(data_df[['work_years','max_degree','salary_low','salary_high','salary_ave']])
    arr1 = np.array(data_df[['salary_ave','work_years','max_degree']])
    # data_df = pd.DataFrame(arr1,columns=['100', '101', '102'], index=[r['id'] for i, r in data_df.iterrows()])
    data_df = pd.DataFrame(arr1,columns=['100', '101', '102'])
    print(data_df)
    return data_df

def degree2num(data_df):
    # data_df.replace(to_replace='博士后', value=7, inplace=True)
    data_df.replace(to_replace='博士', value=6, inplace=True)
    data_df.replace(to_replace='硕士', value=5, inplace=True)
    data_df.replace(to_replace='MBA', value=5, inplace=True)
    data_df.replace(to_replace='本科', value=4, inplace=True)
    data_df.replace(to_replace='大专', value=3, inplace=True)
    data_df.replace(to_replace='高中', value=2, inplace=True)
    data_df.replace(to_replace='中专', value=2, inplace=True)
    data_df.replace(to_replace='中技', value=2, inplace=True)
    data_df.replace(to_replace='初中', value=1, inplace=True)
    return data_df

def lose_del(search_sql,conn):
    """
    处理缺失值和空字符串
    """
    data_df=pd.read_sql(search_sql,conn)
    data_df.replace(to_replace='', value=np.nan, inplace=True)
    # data_df.replace(to_replace='#', value=1000000, inplace=True)
    data_df = data_df.dropna(how='any', axis=0)
    print(data_df)
    d = dict()
    n = 0
    for i, r in data_df.iterrows():  # 这个i不是连续值，所以用n
        d[n]=r['id']
        n += 1
    print(d)
    pickle.dump(d, open("../resource/resume_id.txt", "wb"))

    return data_df

if __name__ == '__main__':
    # data = lose_del(search_sql,conn)
    # data1 = word_vec(data)
    # d = degree2num(data)
    # data2 = salary_ave(d)
    # data3 = pd.concat([data1, data2],axis=1)
    # data4 = to_one(data3)
    # # print(data4.loc['SSG190111vig2941'])
    # data4.to_csv('../resource/resume_vec.csv')
    #
    # d = pickle.load(open("../resource/resume_id.txt", "rb"))
    # print(d)
    # print(d[0])
    # sales = Sales()
    # sql = "select sum(p.amount),g.upc from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '2019-10-8 00:00:00' and p.shop_id=3598 group by g.upc order by sum(p.amount) desc;"
    # data = sales.get_data_from_mysql(sql)
    # print(data)
    data = HandleData()
    d=data.get_data()
    print(d)




