from itertools import product

from goods.shelfdisplay.db_data import NullGoodsData
from goods.shelfdisplay.replacedisplay.area_father import Area
from goods.shelfdisplay.replacedisplay.display_object import DisplayGoods

def is_left_to_right(level_id):
    if level_id % 2 == 0:
        return True
    else:
        return False


class AreaManager:

    def __init__(self, shelf, levelid_to_displaygoods_list, choose_goods_list):
        self.shelf = shelf
        self.levelid_to_displaygoods_list = levelid_to_displaygoods_list
        self.choose_goods_list = choose_goods_list
        self.area_list = None
        self.levelid_to_remain_width = self._calculate_level_remain_width()
        self.down_display_goods_list = []
        self.up_choose_goods_list = []

    def calculate_candidate_shelf(self):

        self._first_born_areas()
        self._second_combine_areas()
        self._prepare_area_base_data()
        self._prepare_area_calculate_data()

        self._print_choose_goods_info()

        self._arrange_areas()
        return self.arrange_goods()

    def _calculate_level_remain_width(self):
        sorted_level_ids = list(self.levelid_to_displaygoods_list.keys())
        sorted_level_ids.sort()

        max_sorted_level_id = sorted_level_ids[-1]

        # 处理空层
        for level_id in range(max_sorted_level_id+1):
            if level_id not in sorted_level_ids:
                # 处理空层
                self.levelid_to_displaygoods_list[level_id] = [DisplayGoods(NullGoodsData(self.shelf.width))]

        levelid_to_remain_width = {}
        for level_id in self.levelid_to_displaygoods_list:
            goods_width = 0
            for display_goods in self.levelid_to_displaygoods_list[level_id]:
                goods_width += display_goods.goods_data.width * display_goods.face_num

            levelid_to_remain_width[level_id] = self.shelf.width - goods_width

        return levelid_to_remain_width

    def _first_born_areas(self):
        """
        创建区域
        按照三级分类对货架空间进行分区
        """
        self.area_list = []

        area = None
        cur_area_category3 = None
        child_area_display_goods_list = []

        # 确保从底层开始计算
        sorted_level_ids = list(self.levelid_to_displaygoods_list.keys())
        sorted_level_ids.sort()

        # 对displaygoods_list做逆序处理
        for level_id in sorted_level_ids:
            display_goods_list = self.levelid_to_displaygoods_list[level_id]
            if len(display_goods_list) > 0:
                # 回行流动的处理
                if not is_left_to_right(level_id):
                    display_goods_list.reverse()

        for level_id in sorted_level_ids:
            start_width = 0
            display_goods_list = self.levelid_to_displaygoods_list[level_id]
            if len(display_goods_list) > 0:

                for display_goods in display_goods_list:
                    if cur_area_category3 is not None and cur_area_category3 == display_goods.goods_data.category3:
                        cur_area_category3 = display_goods.goods_data.category3
                        child_area_display_goods_list.append(display_goods)
                        start_width += display_goods.goods_data.width * display_goods.face_num
                    else:
                        # 结束上一个child_area, 开始一个新的child_area
                        if len(child_area_display_goods_list)>0:
                            area.add_child_area_in_one_category3(level_id, start_width, child_area_display_goods_list)
                        # 开始一个新的area
                        area = Area(self, level_id, start_width)
                        self.area_list.append(area)
                        child_area_display_goods_list = [display_goods]
                        cur_area_category3 = display_goods.goods_data.category3

                # 结束上一个child_area, 开始一个新的child_area
                area.add_child_area_in_one_category3(level_id, start_width, child_area_display_goods_list)
                child_area_display_goods_list = []

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

    def _prepare_area_base_data(self):

        for area in self.area_list:
            area.calculate_width()

        # 筛选各个area的choose_goods_list
        for goods in self.choose_goods_list:
            if goods.goods_role == 1:
                area_list = []
                for area in self.area_list:
                    if goods.category3 in area.category3_list:
                        area_list.append(area)

                if len(area_list)>0:
                    max_width = 0
                    max_width_area = None
                    for area in area_list:
                        if area.total_width > max_width:
                            max_width = area.total_width
                            max_width_area = area
                    max_width_area.choose_goods_list.append(goods)
            else:
                for area in self.area_list:
                    if goods.category3 in area.category3_list:
                        area.choose_goods_list.append(goods)


        for area in self.area_list:
            area.prepare_goods_data()

    def _prepare_area_calculate_data(self):
        for area in self.area_list:
            area.prepare_calculate_data()

    def _print_choose_goods_info(self):
        """
        area.up_choose_goods_list = []
        area.down_display_goods_list = []
        self.levelid_to_goods_width = {}
        self.levelid_to_remain_width = {}

        area.display_goods_to_reduce_face_num = {}
        area.second_down_display_goods_list = []

        :return:
        """

        print('\n区域分解：')
        for area in self.area_list:
            print(area)

        up_info = '\n必须上架商品：'
        for area in self.area_list:
            for choose_goods in area.up_choose_goods_list:
                up_info += str(choose_goods)
                up_info += ','

        print(up_info)

        down_info = '\n必须下架商品：'
        for area in self.area_list:
            for display_goods in area.down_display_goods_list:
                down_info += str(display_goods.goods_data)
                down_info += ','
        print(down_info)

        second_up_info = '\n二次上架商品：'
        for area in self.area_list:
            for choose_goods in area.second_up_choose_goods_list:
                second_up_info += str(choose_goods)
                second_up_info += ','
        print(second_up_info)

        reduce_info = '\n减扩面商品：'
        for area in self.area_list:
            for display_goods in area.display_goods_to_reduce_face_num:
                reduce_info += str(display_goods.goods_data) + '(' + str(area.display_goods_to_reduce_face_num[display_goods])
                reduce_info += '),'
        print(reduce_info)

        second_down_info = '\n二次下架商品：'
        for area in self.area_list:
            for display_goods in area.second_down_display_goods_list:
                second_down_info += str(display_goods.goods_data)
                second_down_info += ','
        print(second_down_info)

    def _arrange_areas(self):
        """
        计算每个area的最佳摆放
        :return:
        """

        for area in self.area_list:
            area.calculate_best_display_goods()

    def arrange_goods(self):
        candidate_shelf = self.shelf.copy_raw()
        cur_level_index = 0
        cur_level_goods_width = 0
        for area in self.area_list:
            one_area_display_goods_list = area.best_display_goods_list
            area_total_goods_width = 0
            for display_goods in one_area_display_goods_list:
                goods_width = display_goods.goods_data.width * display_goods.face_num
                cur_level = candidate_shelf.levels[cur_level_index]
                if cur_level_goods_width + goods_width > candidate_shelf.width + 10:  # 加10的容差
                    remain_level_width = min(candidate_shelf.width - cur_level_goods_width, area.total_width - area_total_goods_width)
                    cur_level_index += 1
                    if cur_level_index >= len(candidate_shelf.levels):
                        print("陈列商品超出货架，陈列到此结束:{}".format(cur_level_index))
                        return candidate_shelf
                    cur_level = candidate_shelf.levels[cur_level_index]
                    cur_level.add_display_goods(display_goods)
                    cur_level_goods_width = goods_width
                    area_total_goods_width += remain_level_width + goods_width
                else:
                    cur_level.add_display_goods(display_goods)
                    cur_level_goods_width += goods_width
                    area_total_goods_width += goods_width

        return candidate_shelf