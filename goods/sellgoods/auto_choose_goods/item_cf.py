# coding = utf-8

# 基于项目的协同过滤推荐算法实现
import random

import math
from operator import itemgetter


class ItemBasedCF():
    # 初始化参数
    def __init__(self):
        # 找到相似的20部商品，为目标用户推荐10部商品
        self.n_sim_goods = 20
        self.n_rec_goods = 10

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 用户相似度矩阵
        self.goods_sim_matrix = {}
        self.goods_popular = {}
        self.goods_count = 0

        print('Similar goods number = %d' % self.n_sim_goods)
        print('Recommneded goods number = %d' % self.n_rec_goods)


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


        print(self.goods_sim_matrix)
        print(self.goods_sim_matrix['6901028075022'])


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


if __name__ == '__main__':
    rating_file = 'user_item_rate.csv'
    itemCF = ItemBasedCF()
    itemCF.get_dataset(rating_file)
    itemCF.calc_goods_sim()
    # itemCF.evaluate()