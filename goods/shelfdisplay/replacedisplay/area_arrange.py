"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""

class AreaManager():
    def __init__(self, taizhang_display):
        self.taizhang_display = taizhang_display
        self.area_list = None

    def calculate_candidate_shelf(self):

        self._born_areas()
        self._arrange_areas()
        candidate_shelf_list = self._combine_area()
        return candidate_shelf_list


    def _born_areas(self):
        """
        创建区域
        按照三级分类对货架空间进行分区，如两个相邻的同二级分类下的三级分类商品平均高度差小于5cm，可分为同一区
        """
        self.area_list = []
        # TODO 需要实现

    def _arrange_areas(self):
        """
        计算每个area的候选集
        :return:
        """
        for area in self.area_list:
            area.calculate_candidate()

    def _combine_area(self):
        """
        组合所有的area候选集，生成shelf对象
        返回一个candidate_shelf_list
        :return:
        """
        # TODO 需要实现
        candidate_shelf_list = []
        return candidate_shelf_list


class Area():
    def __init__(self, shelf, choose_goods_list, category3_list):
        self.shelf = shelf
        self.choose_goods_list = choose_goods_list
        self.category3_list = category3_list
        self.candidate_display_goods_list_list = []

    def calculate_candidate(self, candidate_threshhold = 5):
        """
        同一分区内可能有一个或多个商品上架，也可能有0个或n个商品下架，优先挤扩面，扩面的销售产出按照psd金额/n递减计算；如需下架商品从分区内销售最差的商品开始选择
        :param candidate_threshhold:
        :return:
        """
        pass
        # TODO 需要实现