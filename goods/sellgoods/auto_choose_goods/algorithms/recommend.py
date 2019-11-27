import os
from surprise import SVD
from surprise import SVDpp
from surprise import Dataset
from surprise import accuracy
from surprise.model_selection import train_test_split
from surprise import KNNBasic
from surprise import BaselineOnly
from surprise import Reader
from surprise.model_selection import KFold
from surprise.model_selection import cross_validate
from surprise.model_selection import GridSearchCV


def train_model():
    file_path = os.path.expanduser('user_item_rate.csv')
    reader = Reader(line_format='user item rating', sep=',')
    surprise_data = Dataset.load_from_file(file_path, reader=reader)

    all_trainset = surprise_data.build_full_trainset()
    algo = KNNBasic(k=40,min_k=3,sim_options={'user_based': True}) # sim_options={'name': 'cosine','user_based': True} cosine/msd/pearson/pearson_baseline
    algo.fit(all_trainset)
    return algo

def getSimilarUsers(algo,top_k,u_id):
    user_inner_id = algo.trainset.to_inner_uid(u_id)
    user_neighbors = algo.get_neighbors(user_inner_id, k=top_k)
    user_neighbors = (algo.trainset.to_raw_uid(inner_id) for inner_id in user_neighbors)
    return user_neighbors


class ItemCF():

    def __init__(self):
        file_path = os.path.expanduser('user_item_rate.csv')
        reader = Reader(line_format='user item rating', sep=',')
        surprise_data = Dataset.load_from_file(file_path, reader=reader)
        all_trainset = surprise_data.build_full_trainset()

        # 训练模型：基于项目相似度
        self.item_algo = KNNBasic(k=10, min_k=3, sim_options={'user_based': False})
        # sim_options={'name': 'cosine','user_based': True} cosine/msd/pearson/pearson_baseline
        self.item_algo.fit(all_trainset)


    def get_similar_items(self,top_k, item_id):
        """
        相似项目
        Args:
            top_k(int): 相似项目数量
            item_id(str): 项目id

        Returns:
            list generator
        """
        item_inner_id = self.item_algo.trainset.to_inner_iid(item_id)
        item_neighbors = self.item_algo.get_neighbors(item_inner_id, k=top_k)
        item_neighbor_ids = (self.item_algo.trainset.to_raw_iid(inner_id) for inner_id in item_neighbors)
        return item_neighbor_ids
        # 原文链接：https://blog.csdn.net/mouday/article/details/88181713

if __name__ == '__main__':
    # model = train_model()
    # r= getSimilarUsers(model,5,'1833')
    # print(list(r))

    itemcf = ItemCF()
    r= itemcf.get_similar_items(5,'6901028075022')
    print(list(r))