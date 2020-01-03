# coding = utf-8

# 基于项目的协同过滤推荐算法实现
import random
import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections
import math
from operator import itemgetter


class ItemBasedCF():
    # 初始化参数
    def __init__(self,pos_shop_id,n_sim_goods,n_rec_goods):

        self.pos_shop_id = pos_shop_id
        self.days = 28
        self.supplier_id_list = []  # 供应商id，可以多个
        self.can_order_mch_list = []
        self.dmstore_cursor = connections['dmstore'].cursor()

        # 找到相似的多少个商品，为门店推荐多少个商品
        self.n_sim_goods = n_sim_goods
        self.n_rec_goods = n_rec_goods

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 用户相似度矩阵
        self.goods_sim_matrix = {}
        self.goods_popular = {}
        self.goods_count = 0

        self.shop_psd_number_dict = {}     # 本店销售量的字典

        print('Similar goods number = %d' % self.n_sim_goods)
        print('Recommneded goods number = %d' % self.n_rec_goods)
    def __del__(self):
        self.dmstore_cursor.close()
        # self.cursor_ucenter.close()

    # 读取数据库得到"订单-商品"数据
    def get_data(self):
        can_order_mch_list, _ = self.get_can_order_dict()
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select p.payment_id,GROUP_CONCAT(g.neighbor_goods_id) n from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and g.neighbor_goods_id in ({}) GROUP BY p.payment_id having COUNT(g.neighbor_goods_id) >1"
        self.dmstore_cursor.execute(sql.format(week_ago, now_date,','.join(can_order_mch_list)))
        all_data = self.dmstore_cursor.fetchall()
        print(len(all_data))
        for data in all_data:
            for goods in data[1].split(","):
                self.trainSet.setdefault(data[0], {})
                self.trainSet[data[0]][goods] = 1

    # 读文件得到“用户-商品”数据
    def get_dataset(self, filename, pivot=0.9999999):
        trainSet_len = 0
        testSet_len = 0
        for line in self.load_file(filename):
            user, goods, rating = line.split(',')
            if(random.random() < pivot):
                self.trainSet.setdefault(user, {})
                self.trainSet[user][goods] = rating
                trainSet_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][goods] = rating
                testSet_len += 1
        print('Split trainingSet and testSet success!')
        print('TrainSet = %s' % trainSet_len)
        print('TestSet = %s' % testSet_len)


    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)


    # 计算商品之间的相似度
    def calc_goods_sim(self):
        for user, goodss in self.trainSet.items():
            for goods in goodss:
                if goods not in self.goods_popular:
                    self.goods_popular[goods] = 0
                self.goods_popular[goods] += 1

        self.goods_count = len(self.goods_popular)
        print("Total goods number = %d" % self.goods_count)

        for user, goodss in self.trainSet.items():
            for m1 in goodss:
                for m2 in goodss:
                    if m1 == m2:
                        continue
                    self.goods_sim_matrix.setdefault(m1, {})
                    self.goods_sim_matrix[m1].setdefault(m2, 0)
                    self.goods_sim_matrix[m1][m2] += 1
        print("Build co-rated users matrix success!")

        # 计算商品之间的相似性
        print("Calculating goods similarity matrix ...")
        for m1, related_goodss in self.goods_sim_matrix.items():
            for m2, count in related_goodss.items():
                # 注意0向量的处理，即某商品的用户数为0
                if self.goods_popular[m1] == 0 or self.goods_popular[m2] == 0:
                    self.goods_sim_matrix[m1][m2] = 0
                else:
                    self.goods_sim_matrix[m1][m2] = count / math.sqrt(self.goods_popular[m1] * self.goods_popular[m2])
        print('Calculate goods similarity matrix success!')


        # print(self.goods_sim_matrix)
        # print(self.goods_sim_matrix['6901028075022'])


    # 针对目标用户U，找到K个相似的商品，并推荐其N个商品
    def recommend(self, user):
        K = self.n_sim_goods
        N = self.n_rec_goods
        rank = {}
        sell_goods = self.trainSet[user]    # 卖出的商品

        for goods, rating in sell_goods.items():
            for related_goods, w in sorted(self.goods_sim_matrix[goods].items(), key=itemgetter(1), reverse=True)[:K]:
                if related_goods in sell_goods:
                    continue
                rank.setdefault(related_goods, 0)
                rank[related_goods] += w * float(rating)
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]

    # 针对门店销量排名，进行推荐
    def recommend_02(self):

        self.get_data()

        self.calc_goods_sim()

        shop_sales_data = self.get_shop_sales_data(self.pos_shop_id)
        for data in shop_sales_data:
            # self.shop_psd_number_dict[str(data[3])] = data[6]      # 按照psd
            self.shop_psd_number_dict[str(data[3])] = data[0]      # 按照psd金额

        K = self.n_sim_goods
        N = self.n_rec_goods
        rank = {}
        ttt = 0
        for goods,rating in self.shop_psd_number_dict.items():
            try:    # 该商店可能有的品在大集合里没有
                for related_goods, w in sorted(self.goods_sim_matrix[goods].items(), key=itemgetter(1), reverse=True)[:K]:
                    t = rank.get(related_goods, 0)
                    t += w * float(rating)
                    rank[related_goods] = t
            except:
                ttt += 1
                print(ttt)
                continue

        return sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]



    # 产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print('Evaluating start ...')
        N = self.n_rec_goods
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_goods = set()

        for i, user in enumerate(self.trainSet):
            test_goods = self.testSet.get(user, {})
            rec_goods= self.recommend(user)
            for goods, w in rec_goods:
                if goods in test_goods:
                    hit += 1
                all_rec_goods.add(goods)
            rec_count += N
            test_count += len(test_goods)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_goods) / (1.0 * self.goods_count)
        print('precisioin=%.4f\trecall=%.4f\tcoverage=%.4f' % (precision, recall, coverage))

    def get_can_order_dict(self):
        """
        获取可订货的7位得mch_goods_code的字典，value为配送类型，k为店内码,从saas查询
        :return:
        """
        # self.dmstore_cursor.execute("SELECT erp_shop_id from erp_shop_related WHERE shop_id ={} AND erp_shop_type=0;".format(self.pos_shop_id))
        # try:
        #     erp_shop_id = self.dmstore_cursor.fetchone()[0]
        #     print("erp_shop_id",erp_shop_id)
        # except:
        #     print('erp_shop_id获取失败！')
        #     return []
        # try:
        #     ms_conn = connections["erp"]
        #     ms_cursor = ms_conn.cursor()
        #     ms_cursor.execute("SELECT authorized_shop_id FROM ms_relation WHERE is_authorized_shop_id IN (SELECT authorized_shop_id FROM	ms_relation WHERE is_authorized_shop_id = {} AND STATUS = 1) AND STATUS = 1".format(erp_shop_id))
        #     all_data = ms_cursor.fetchall()
        #     supplier_code = []
        #     for data in all_data:
        #         supplier_code.append(str(data[0]))
        # except:
        #     print('supplier_code获取失败！')
        #     return []


        # 获取商品的 可定 配送类型

        self.dmstore_cursor.execute(
            "SELECT erp_shop_id from erp_shop_related WHERE shop_id ={} AND erp_shop_type=1;".format(self.pos_shop_id))
        try:
            erp_shop_id = self.dmstore_cursor.fetchone()[0]
            print("erp_shop_id", erp_shop_id)
        except:
            print('erp_shop_id获取失败！')
            return []

        conn_ucenter = connections['ucenter']
        cursor_ucenter = conn_ucenter.cursor()
        delivery_type_dict = {}    # 店内码是key，配送类型是value
        can_order_list = []   #可订货列表
        try:
            # cursor_ucenter.execute("select id from uc_supplier where supplier_code in ({})".format(','.join(supplier_code)))
            cursor_ucenter.execute("SELECT supplier_id from uc_warehouse_supplier_shop WHERE warehouse_id={}".format(erp_shop_id))
            all_supplier_id_data = cursor_ucenter.fetchall()
            for supplier_data in all_supplier_id_data:
                self.supplier_id_list.append(str(supplier_data[0]))

            cursor_ucenter.execute(
                # "select supplier_goods_code from uc_supplier_goods where supplier_id in ({}) and order_status = 1 ".format(','.join(self.supplier_id_list)))
                # "select a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code where a.supplier_id = {} and order_status = 1".format(supplier_id))
                # 有尺寸数据
                "select DISTINCT a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code LEFT JOIN uc_merchant_goods c on a.supplier_goods_code=c.supplier_goods_code where a.supplier_id in ({}) and order_status = 1 and c.width > 0 and c.height > 0 and c.depth > 0 and c.display_third_cat_id > 0".format(','.join(self.supplier_id_list)))
            all_data = cursor_ucenter.fetchall()
            for data in all_data:
                # delivery_type_dict[data[0]] = data[1]
                can_order_list.append(data[0])
        except:
            print('pos店号是{},查询是否可订货和配送类型失败'.format(self.pos_shop_id))
        conn_ucenter.close()
        return can_order_list[:],delivery_type_dict

    def get_shop_sales_data(self, shop_id):
        """
        获取该店有销量的商品的psd金额的排序列表
        :param shop_id:
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        # 这个三级分类没用
        sql = "select sum(p.amount),g.upc,g.saas_third_catid,g.neighbor_goods_id,g.price,p.name,sum(p.number) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} group by g.upc order by sum(p.amount) desc;"
        self.dmstore_cursor.execute(sql.format(week_ago, now_date, shop_id))
        results = self.dmstore_cursor.fetchall()
        return results


if __name__ == '__main__':
    rating_file = 'user_item_rate.csv'
    itemCF = ItemBasedCF(1284,70,50)
    # itemCF.get_dataset(rating_file)
    a = itemCF.recommend_02()
    # a = itemCF.get_can_order_dict()
    print(type(a))
    print(a)
    # itemCF.evaluate()