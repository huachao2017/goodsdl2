# # -*- coding: utf-8 -*-


import jieba.posseg as pseg
import pymysql
from gensim.models import word2vec
# from redis import *
import re,time
import pymysql
import pandas as pd


def train_model(data):
    # 分词前的文本数据设为r
    r = """
    """

    # 分词后的文本设为rr
    rr = """
    """

    # 用for循环将简历数据加到一块
    for i in data:
        # r += i[0]
        # jd = re.sub(r"<[^>]*>|&nbsp;|\n", "", i[0])
        r += i[1]
        r += i[2]
    r = re.sub(re.compile(r'[\sA-Za-z～()（）【】%*#+-\\:=：_,，。、;；“”"''’‘？?！!<《》>^&{}|…]'), '', r)
    # r = "昨天下午，一艘货轮行驶至武汉白沙洲洲尾时，遭遇突如其来的狂风，船上28个装满鞭炮等货品、重约60吨的集装箱落入长江。海事部门紧急搜救两小时，除一个集装箱由于箱体进水沉入江底外，其余27个被打捞上岸。,第十二届cctv青年歌手电视大奖赛军队获奖选手赴部队慰问演出活动启动,由解放军总政治部宣传部组织的“第十二届cctv青年歌手大奖赛军队获奖选手赴部队慰问演出活动”日前在北京启动。获奖选手们冒着30多度的高温，用激情洋溢的演唱，为基层官兵送来了一首首动人的歌曲。在刚刚结束的第十二届cctv青年歌手大奖赛中，军队各代表队和参赛选手，共夺得4个金奖、5个银奖、12个铜奖，取得了军队参加该项赛事以来的最好成绩。获奖选手还将于近日组成三个小分队，赴边防、海岛等一线部队慰问演出。,刘振民说中国政府对驻黎维和人员受伤表示严重关切,中国常驻联合国副代表刘振民６号在联合国总部表示，中国政府对中国驻黎巴嫩维和人员在黎以冲突中受伤表示强烈不满和严重关切。当天上午，中国常驻联合国代表团奉政府的指示与黎以冲突有关各方进行了交涉，还特别与联合国负责维和事务的副秘书长盖埃诺进行了紧急约谈，提出了严正交涉，要求联合国方面采取一切必要措施，确保包括中国士兵在内的所有联合国维和人员的安全，避免再次发生此类事件 。,国际简讯,——伊朗称将继续并扩大铀浓缩活动"

    document_cut = pseg.cut(r)  # 把所有数据进行分词

    # 以下是将分完词的数据加到一块
    for j in document_cut:
        j = str(j)
        j = j.split('/')[0]
        rr += j
        rr += ' '

    # 将数据存到haha文件里
    with open('goods/choose_goods/lianghua/resource/data_words.txt', 'w', encoding='utf-8') as f2:
        f2.write(rr)

    sentences = word2vec.LineSentence('goods/choose_goods/lianghua/resource/data_words.txt')  # 把目标文本读出来
    # model = word2vec.Word2Vec(sentences, hs=1,min_count=1,window=6,size=128)     # 初始训练模型

    model = word2vec.Word2Vec.load("goods/choose_goods/lianghua/resource/data_words_jieba.model")  # 加载模型
    model.build_vocab(sentences, update=True)  # 更新词汇表
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)  # 增量训练模型

    model.save("goods/choose_goods/lianghua/resource/data_words_jieba.model")  # 保存模型

    # # 以下是将某词最相近的5的词打印出来
    # req_count = 5
    # for key in model.wv.similar_by_word('主席', topn=100):
    #     if len(key[0]) == 3:
    #         req_count -= 1
    #         print(key[0], key[1])
    #         if req_count == 0:
    #             break

def mian():

    conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)

    # conn = connections['default']
    cursor = conn.cursor()

    data_num = 500   # 一次取多少数据
    sub = 0
    while True:

        print(sub)

        search_sql = 'select date,title,content from cctv_news where id<%s and id >= %s'%(str(int(sub)+data_num),str(int(sub)))
        # print(search_sql)
        cursor.execute(search_sql)
        data = cursor.fetchall()
        if data:
            train_model(data)
        else:
            print('end')
            break
        sub = int(sub) + int(data_num)


class TrainWord2Vec:
    """
    训练得到一个Word2Vec模型
    @author:xiaozhu
    @time:2018年10月12日
    """
    def __init__(self, data, stopword, num_features=100, min_word_count=1, context=4, incremental=False,old_path):
        """
        定义变量
        :param data: 用于训练胡语料
        :param stopword: 停用词表
        :param num_features:  返回的向量长度
        :param min_word_count:  最低词频
        :param context: 滑动窗口大小
        :param incremental: 是否进行增量训练
        :param old_path: 若进行增量训练，原始模型路径
        """
        self.data = data
        self.stopword = stopword
        self.num_features = num_features
        self.min_word_count = min_word_count
        self.context = context
        self.incremental = incremental
        self.old_path = old_path

    def clean_text(self):
        """
        采用结巴分词函数分词
        :param corpus: 待分词的Series序列
        :return: 分词结果，list
        """
        # 去除无用字符
        pattern = re.compile(r'[\sA-Za-z～()（）【】%*#+-\.\\\/:=：__,，。、;；“”""''’‘？?！!<《》>^&{}|=……]')
        corpus_ = self.data.apply(lambda s: re.sub(pattern, '', s))
        # 分词
        text = corpus_.apply(jieba.lcut)
        # 过滤通用词
        text = text.apply(lambda cut_words: [word for word in cut_words if word not in self.stopword])
        return text

    def get_model(self, text):
        """
        从头训练word2vec模型
        :param text: 经过清洗之后的语料数据
        :return: word2vec模型
        """
        model = Word2Vec(text, size=self.num_features, min_count=self.min_word_count, window=self.context)
        return model

    def update_model(self, text):
        """
        增量训练word2vec模型
        :param text: 经过清洗之后的新的语料数据
        :return: word2vec模型
        """
        model = Word2Vec.load(self.old_path)  # 加载旧模型
        model.build_vocab(text, update=True)  # 更新词汇表
        model.train(text, total_examples=model.corpus_count, epochs=model.iter)  # epoch=iter语料库的迭代次数；（默认为5）  total_examples:句子数。
        return model

    def main(self):
        """
        主函数，保存模型
        """
        # 加入自定义分析词库
        jieba.load_userdict("add_word.txt")
        text = self.clean_text()
        if self.incremental:
            model = self.update_model(text)
        else:
            model = self.get_model(text)
        # 保存模型
        model.save("word2vec.model")


# if __name__ == '__main__':
#     corpus = pd.read_csv("corpus.csv", encoding='gbk')
#     stop_word = pd.read_csv("stopword.csv", encoding='gbk')
#     trainmodel = TrainWord2Vec(data=corpus, stopword=stop_word)
#     trainmodel.main()


if __name__ == '__main__':
    mian()
    # train_model(['123','123','123'])