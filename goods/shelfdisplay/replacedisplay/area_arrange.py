"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""
def born_areas(taizhang_display):
    """
    创建区域
    :param shelf:
    :return:
    """
    area_list = []
    return area_list

def display_areas(area_list):
    for area in area_list:
        area.calculate_candidate()

def combine_area(area_list):
    """
    返回一个candidate_shelf
    :param area_list:
    :return:
    """
    # TODO
    candidate_shelf_list = []
    return candidate_shelf_list


def goods_replace_score(candidate_shelf_list):
    """
    :param candidate_shelf_list:
    :return: 分数最低的shelf
    """

    min_badcase_value = 100000
    best_candidate_shelf = None
    # TODO
    return best_candidate_shelf

class Area():
    def __init__(self, shelf, category3_list):
        self.shelf = shelf
        self.category3_list = category3_list
        self.candidate_display_goods_list_list = []

    def calculate_candidate(self, candidate_threshhold = 5):
        pass