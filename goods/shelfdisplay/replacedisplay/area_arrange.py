"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""


class AreaManager:
    def __init__(self, raw_shelf, levelid_to_displaygoods_list, choose_goods_list):
        self.raw_shelf = raw_shelf
        self.levelid_to_displaygoods_list = levelid_to_displaygoods_list
        self.choose_goods_list = choose_goods_list
        self.area_list = None
        self.levelid_to_remain_width = self._calculate_level_remain_width()

    def calculate_candidate_shelf(self):

        self._first_born_areas()
        self._second_combine_areas()
        self._arrange_areas()
        candidate_shelf_list = self._calculate_all_area_candidate()
        return candidate_shelf_list

    def _calculate_level_remain_width(self):
        levelid_to_remain_width = {}
        for level_id in self.levelid_to_displaygoods_list:
            goods_width = 0
            for display_goods in self.levelid_to_displaygoods_list[level_id]:
                goods_width += display_goods.goods_data.width * display_goods.face_num

            levelid_to_remain_width[level_id] = self.raw_shelf.width - goods_width

        return levelid_to_remain_width

    def _first_born_areas(self):
        """
        创建区域
        按照三级分类对货架空间进行分区
        """
        self.area_list = []

        area = Area(self)
        self.area_list.append(area)
        area_category3 = None
        one_displaygoods_list = []

        # 确保从底层开始计算
        sorted_levelids = list(self.levelid_to_displaygoods_list.keys())
        sorted_levelids.sort()
        for levelid in sorted_levelids:
            displaygoods_list = self.levelid_to_displaygoods_list[levelid]
            for displaygoods in displaygoods_list:
                if area_category3 is None:
                    area_category3 = displaygoods.goods_data.category3
                    one_displaygoods_list.append(displaygoods)
                else:
                    if area_category3 == displaygoods.goods_data.category3:
                        one_displaygoods_list.append(displaygoods)
                    else:
                        area.add_child_area_in_one_category3(levelid, one_displaygoods_list)
                        area_category3 = displaygoods.goods_data.category3
                        one_displaygoods_list = [displaygoods]
                        area = Area(self)
                        self.area_list.append(area)

            area.add_child_area_in_one_category3(levelid, one_displaygoods_list)
            one_displaygoods_list = []

    def _second_combine_areas(self):
        """
        如两个相邻的同二级分类下的三级分类商品平均高度差小于5cm，可分为同一区
        :return:
        """
        last_area = None
        last_area_height = -1
        removed_area_list = []
        for area in self.area_list:
            avg_height = area.calculate_avg_height()
            if last_area is not None:
                if area.category2 == last_area.category2:
                    if abs(last_area_height - avg_height) < 50:
                        area.combine_area(last_area)
                        removed_area_list.append(last_area)

            last_area = area
            last_area_height = avg_height

        for removed_area in removed_area_list:
            self.area_list.remove(removed_area)

    def _prepare_area_data(self):
        for area in self.area_list:
            area.prepare_data(self.choose_goods_list)

    def _arrange_areas(self):
        """
        计算每个area的候选集
        :return:
        """
        len_area_list = len(self.area_list)
        if len_area_list <= 2:
            threshhold = 10
        elif len_area_list <= 5:
            threshhold = 5
        elif len_area_list <= 8:
            threshhold = 3
        else:
            threshhold = 2

        for area in self.area_list:
            area.calculate_candidate(threshhold)

    def _calculate_all_area_candidate(self):
        """
        组合所有的area候选集，生成shelf对象
        返回一个candidate_shelf_list
        :return:
        """
        # TODO 需要实现
        candidate_shelf_list = []
        return candidate_shelf_list


class Area:
    def __init__(self, area_manager):
        self.area_manager = area_manager
        self.child_area_list = []
        self.category2 = None
        self.category3_list = []

        # 计算时变量
        self.choose_goods_list = None
        self.levelid_to_goods_width = {}
        self.candidate_display_goods_list_list = []

    def add_child_area_in_one_category3(self, level_id, display_goods_list):
        category2 = display_goods_list[0].goods_data.category2
        category3 = display_goods_list[0].goods_data.category3
        if self.category2 is None:
            self.category2 = category2
        else:
            if self.category2 != category2:
                raise ValueError('one area category2 is not equal')

        if category3 not in self.category3_list:
            self.category3_list.append(category3)

        self.child_area_list.append(ChildArea(level_id, display_goods_list))

    def get_category2(self):
        return self.category2

    def calculate_avg_height(self):
        total_height = 0
        total_count = 0
        for area_level in self.child_area_list:
            for display_goods in area_level.display_goods_list:
                total_count += 1
                total_height += display_goods.goods_data.height * display_goods.superimpose_num

        return int(total_height/total_count)

    def combine_area(self, last_area):
        self.child_area_list = last_area.child_area_list + self.child_area_list
        self.category3_list = last_area.category3_list + self.category3_list


    def prepare_data(self, choose_goods_list):
        """
        准备选品数据，每层商品宽度
        :param choose_goods_list:
        :return:
        """
        # 筛选choose_goods_list
        choose_goods_list_in_area = []
        for goods in choose_goods_list:
            if goods.category3 in self.category3_list:
                if goods.goods_role in (0,2,4):
                    # FIXME 下架商品必须在货架上
                    pass
                choose_goods_list_in_area.append(goods)
        self.choose_goods_list = choose_goods_list_in_area

        # 计算每一层的商品宽度
        for child_area in self.child_area_list:
            if child_area.level_id in self.levelid_to_goods_width:
                self.levelid_to_goods_width[child_area.level_id] += child_area.get_goods_width()
            else:
                self.levelid_to_goods_width[child_area.level_id] = child_area.get_goods_width()

    def calculate_candidate(self, candidate_threshhold=5):
        """
        同一分区内可能有一个或多个商品上架，也可能有0个或n个商品下架，优先挤扩面，扩面的销售产出按照psd金额/n递减计算；如需下架商品从分区内销售最差的商品开始选择
        :param candidate_threshhold:
        :return:
        """
        # 第一步：下架必下架品
        for choose_goods in self.choose_goods_list:
            if choose_goods.goods_role == 2:
                for child_area in self.child_area_list:
                    if child_area.category3 == choose_goods.category3:
                        for display_goods in child_area.display_goods_list:
                            if display_goods.goods_data.equal(choose_goods):
                                child_area.down_goods_list.append(choose_goods)

        # 第二步：上架必上品

        # 第三步：挤排面

        pass

    def __str__(self):
        ret = str(self.category3_list) + ':'
        for area_level in self.child_area_list:
            ret += str(area_level)
        return ret

class ChildArea:
    def __init__(self, level_id, display_goods_list):
        self.level_id = level_id
        self.display_goods_list = display_goods_list
        self.down_goods_list = []
        self.category3 = display_goods_list[0].goods_data.category3

    def get_goods_width(self):
        goods_width = 0
        for display_goods in self.display_goods_list:
            goods_width = display_goods.goods_data.width * display_goods.face_num
        return goods_width

    def __str__(self):
        ret = str(self.level_id) + '-' + str(self.category3) + ':['
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

    def equal(self, another_goods):
        if another_goods is not None:
            return self.goods_name == another_goods.goods_name
        return False

    def __str__(self):
        return self.goods_name


if __name__ == '__main__':
    from goods.shelfdisplay.replacedisplay.display_taizhang import Shelf, DisplayGoods

    raw_shelf = Shelf(1, 1800, 800, 300)
    levelid_to_displaygoods_list = {
        0: [DisplayGoods(TestGoods('c2_1', 'c3_1', '1', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '2', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '3', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_1', '4', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_2', '5', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_2', '6', 200, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '7', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '8', 150, 80, 0, 0))],
        1: [DisplayGoods(TestGoods('c2_1', 'c3_3', '11', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '12', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '13', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '14', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '15', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '16', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '17', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '18', 150, 80, 0, 0))],
        2: [DisplayGoods(TestGoods('c2_1', 'c3_3', '21', 150, 80, 0, 0)),
            DisplayGoods(TestGoods('c2_1', 'c3_3', '22', 150, 80, 0, 0)),
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
            DisplayGoods(TestGoods('c2_2', 'c3_8', '48', 100, 80, 0, 0))],
    }

    choose_goods_list = [
        TestGoods('c2_1', 'c3_1', '101', 100, 80, 1, 0), # 上架
        TestGoods('c2_1', 'c3_1', '102', 100, 80, 1, 0),  # 上架
        TestGoods('c2_1', 'c3_1', '4', 100, 80, 2, 0),  # 下架
        TestGoods('c2_1', 'c3_1', '5', 100, 80, 2, 0),  # 下架
    ]

    area_manager = AreaManager(raw_shelf, levelid_to_displaygoods_list, choose_goods_list)

    area_manager._first_born_areas()

    assert len(area_manager.area_list) == 8

    assert len(area_manager.area_list[0].child_area_list)==1
    assert area_manager.area_list[0].child_area_list[0].level_id==0
    assert len(area_manager.area_list[0].child_area_list[0].display_goods_list)==4

    assert len(area_manager.area_list[1].child_area_list)==1
    assert area_manager.area_list[1].child_area_list[0].level_id==0
    assert len(area_manager.area_list[1].child_area_list[0].display_goods_list)==2

    assert len(area_manager.area_list[2].child_area_list)==3
    assert area_manager.area_list[2].child_area_list[0].level_id==0
    assert len(area_manager.area_list[2].child_area_list[0].display_goods_list)==2
    assert area_manager.area_list[2].child_area_list[1].level_id==1
    assert len(area_manager.area_list[2].child_area_list[1].display_goods_list)==8
    assert area_manager.area_list[2].child_area_list[2].level_id==2
    assert len(area_manager.area_list[2].child_area_list[2].display_goods_list)==2

    assert len(area_manager.area_list[3].child_area_list)==1
    assert area_manager.area_list[3].child_area_list[0].level_id==2
    assert len(area_manager.area_list[3].child_area_list[0].display_goods_list)==4

    assert len(area_manager.area_list[4].child_area_list)==2
    assert area_manager.area_list[4].child_area_list[0].level_id==2
    assert len(area_manager.area_list[4].child_area_list[0].display_goods_list)==2
    assert area_manager.area_list[4].child_area_list[1].level_id==3
    assert len(area_manager.area_list[4].child_area_list[1].display_goods_list)==2

    assert len(area_manager.area_list[5].child_area_list)==2
    assert area_manager.area_list[5].child_area_list[0].level_id==3
    assert len(area_manager.area_list[5].child_area_list[0].display_goods_list)==6
    assert area_manager.area_list[5].child_area_list[1].level_id==4
    assert len(area_manager.area_list[5].child_area_list[1].display_goods_list)==2

    assert len(area_manager.area_list[6].child_area_list)==1
    assert area_manager.area_list[6].child_area_list[0].level_id==4
    assert len(area_manager.area_list[6].child_area_list[0].display_goods_list)==5

    assert len(area_manager.area_list[7].child_area_list)==1
    assert area_manager.area_list[7].child_area_list[0].level_id==4
    assert len(area_manager.area_list[7].child_area_list[0].display_goods_list)==1

    for area in area_manager.area_list:
        print(area)

    area_manager._second_combine_areas()
    assert len(area_manager.area_list) == 4

    assert len(area_manager.area_list[0].child_area_list)==2
    assert len(area_manager.area_list[0].child_area_list[0].display_goods_list)==4
    assert len(area_manager.area_list[0].child_area_list[1].display_goods_list)==2

    assert len(area_manager.area_list[1].child_area_list)==3
    assert len(area_manager.area_list[1].child_area_list[0].display_goods_list)==2
    assert len(area_manager.area_list[1].child_area_list[1].display_goods_list)==8
    assert len(area_manager.area_list[1].child_area_list[2].display_goods_list)==2

    assert len(area_manager.area_list[2].child_area_list)==3
    assert len(area_manager.area_list[2].child_area_list[0].display_goods_list)==4
    assert len(area_manager.area_list[2].child_area_list[1].display_goods_list)==2
    assert len(area_manager.area_list[2].child_area_list[2].display_goods_list)==2

    assert len(area_manager.area_list[3].child_area_list)==4
    assert len(area_manager.area_list[3].child_area_list[0].display_goods_list)==6
    assert len(area_manager.area_list[3].child_area_list[1].display_goods_list)==2
    assert len(area_manager.area_list[3].child_area_list[2].display_goods_list)==5
    assert len(area_manager.area_list[3].child_area_list[3].display_goods_list)==1

    print('\n')
    for area in area_manager.area_list:
        print(area)

    area_manager._prepare_area_data()
    assert len(area_manager.area_list[0].choose_goods_list)==4
    assert len(area_manager.area_list[1].choose_goods_list)==0
    assert len(area_manager.area_list[2].choose_goods_list)==0
    assert len(area_manager.area_list[3].choose_goods_list)==0

    print('\n')
    for area in area_manager.area_list:
        print(area)
    area_manager._arrange_areas()
    candidate_shelf_list = area_manager._calculate_all_area_candidate()
