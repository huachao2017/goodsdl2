"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""


class AreaManager:
    def __init__(self, raw_shelf, levelid_to_displaygoods_list, choose_goods_list):
        self.raw_shelf = raw_shelf
        self.levelid_to_displaygoods_list = levelid_to_displaygoods_list
        self.choose_goods_list = choose_goods_list
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

        # 第一轮，先把三级分类分到区域
        area = Area()
        self.area_list.append(area)
        area_category3 = None
        one_displaygoods_list = []
        for levelid in self.levelid_to_displaygoods_list.keys():
            displaygoods_list = self.levelid_to_displaygoods_list[levelid]
            for displaygoods in displaygoods_list:
                if area_category3 is None:
                    area_category3 = displaygoods.goods_data.category3
                    one_displaygoods_list.append(displaygoods)
                else:
                    if area_category3 == displaygoods.goods_data.category3:
                        one_displaygoods_list.append(displaygoods)
                    else:
                        area.add_level_area(levelid, one_displaygoods_list)
                        area_category3 = displaygoods.goods_data.category3
                        one_displaygoods_list = [displaygoods]
                        area = Area()
                        self.area_list.append(area)

            area.add_level_area(levelid, one_displaygoods_list)
            one_displaygoods_list = []

            # 第二轮，合并三级分类的区域

    def _arrange_areas(self):
        """
        计算每个area的候选集
        :return:
        """
        for area in self.area_list:
            area.calculate_candidate(self.choose_goods_list)

    def _combine_area(self):
        """
        组合所有的area候选集，生成shelf对象
        返回一个candidate_shelf_list
        :return:
        """
        # TODO 需要实现
        candidate_shelf_list = []
        return candidate_shelf_list


class Area:
    def __init__(self):
        self.area_level_list = []
        self.candidate_display_goods_list_list = []

    def add_level_area(self, level_id, display_goods_list):
        self.area_level_list.append(AreaLevel(level_id, display_goods_list))

    def calculate_candidate(self, choose_goods_list, candidate_threshhold=5):
        """
        同一分区内可能有一个或多个商品上架，也可能有0个或n个商品下架，优先挤扩面，扩面的销售产出按照psd金额/n递减计算；如需下架商品从分区内销售最差的商品开始选择
        :param candidate_threshhold:
        :return:
        """

        # TODO 计算包含的category3_list

        # TODO 筛选choose_goods_list

        # TODO 计算候选

        pass

    def __str__(self):
        ret = ''
        for area_level in self.area_level_list:
            ret += str(area_level)
        return ret

class AreaLevel:
    def __init__(self, id, display_goods_list):
        self.id = id
        self.display_goods_list = display_goods_list

    def __str__(self):
        ret = str(self.id) + ':['
        for display_goods in self.display_goods_list:
            ret += str(display_goods.goods_data)
            ret += ','
        ret += '], '
        return ret


class TestGoods:
    def __init__(self, category2, category3, goods_name, height, width, goods_role, ranking):
        self.category2 = category2
        self.category3 = category3
        self.goods_name = goods_name
        self.height = height
        self.width = width
        self.goods_role = goods_role
        self.ranking = ranking

    def __str__(self):
        return self.goods_name


if __name__ == '__main__':
    from goods.shelfdisplay.replacedisplay.display_taizhang import Shelf, DisplayGoods

    raw_shelf = Shelf(1, 1800, 800, 300)
    levelid_to_displaygoods_list = {
        0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 100, 80, 0, 0))],
        1: [DisplayGoods(TestGoods('c2_1', 'c3_3', '11', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '12', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '13', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '14', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '15', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '16', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '17', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '18', 100, 80, 0, 0))],
        2: [DisplayGoods(TestGoods('c2_1', 'c3_3', '21', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '22', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_4', '23', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_4', '24', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_4', '25', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_4', '26', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_5', '27', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_5', '28', 100, 80, 0, 0))],
        3: [DisplayGoods(TestGoods('c2_1', 'c3_5', '31', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_5', '32', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '33', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '34', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '35', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '36', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '37', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '38', 100, 80, 0, 0))],
        4: [DisplayGoods(TestGoods('c2_2', 'c3_6', '41', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_6', '42', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '43', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '44', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '45', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '46', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '47', 100, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_2', 'c3_7', '48', 100, 80, 0, 0))],
    }

    choose_goods_list = [
        TestGoods('c2_1', 'c3_1', '101', 100, 80, 1, 0), # 上架
        TestGoods('c2_1', 'c3_1', '102', 100, 80, 1, 0),  # 上架
        TestGoods('c2_1', 'c3_1', '4', 100, 80, 2, 0),  # 下架
        TestGoods('c2_1', 'c3_1', '5', 100, 80, 2, 0),  # 下架
    ]

    area_manager = AreaManager(raw_shelf, levelid_to_displaygoods_list, choose_goods_list)

    area_manager.calculate_candidate_shelf()

    for area in area_manager.area_list:
        print(area)
