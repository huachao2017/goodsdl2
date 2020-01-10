"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""

from itertools import product
from goods.shelfdisplay.normal_algorithm import dict_arrange
from goods.shelfdisplay.replacedisplay.display_object import Shelf, Level, DisplayGoods
from goods.shelfdisplay.db_data import NullGoodsData
import math
from goods.third_tools import dingtalk


def is_left_to_right(level_id):
    if level_id % 2 == 0:
        return True
    else:
        return False

class AreaManager:
    len_area_list_to_threshold = {
        1: 100,
        2: 50,
        3: 20,
        4: 8,
        5: 6,
        6: 4,
        7: 3,
        8: 3,
        9: 3,
        10: 2,
        100: 2}

    def __init__(self, shelf, levelid_to_displaygoods_list, choose_goods_list):
        self.shelf = shelf
        self.levelid_to_displaygoods_list = levelid_to_displaygoods_list
        self.choose_goods_list = choose_goods_list
        self.area_list = None
        self.levelid_to_remain_width = self._calculate_level_remain_width()
        self.threshold = self.len_area_list_to_threshold[100]
        self.candidate_step = 1
        self.down_display_goods_list = []
        self.up_choose_goods_list = []

    def calculate_candidate_shelf(self):

        self._first_born_areas()
        self._second_combine_areas()
        self._prepare_area_base_data()
        self._prepare_area_calculate_data()

        self._print_choose_goods_info()

        self._arrange_areas()
        candidate_shelf_list = self._generate_all_area_candidate()
        return self.calculate_best_candidate_shelf(candidate_shelf_list)

    def calculate_best_candidate_shelf(self, candidate_shelf_list):
        """
        所有商品移动步长，每一步移动做扣分
        暂不做，被挤下商品为可选下架品中预期psd金额较低商品，随金额变低做加分
        :return: 分数最低的shelf
        """

        min_badcase_value = 100000
        best_candidate_shelf = None
        i = 0
        step = max(1, int(len(candidate_shelf_list) / 10))
        for candidate_shelf in candidate_shelf_list:
            i += 1
            badcase_value = 0
            level_index = -1
            for old_level in self.shelf.levels:
                level_index += 1
                start_width = 0
                for old_display_goods in old_level.display_goods_list:
                    badcase_value += self._calculate_score(old_display_goods, start_width,
                                                           candidate_shelf.levels[level_index])
                    start_width += old_display_goods.goods_data.width * old_display_goods.face_num

            if i % step == 0:
                print('计算第{}个候选解,共{}层,value={}：'.format(i, len(candidate_shelf.levels), badcase_value))
            if badcase_value < min_badcase_value:
                min_badcase_value = badcase_value
                best_candidate_shelf = candidate_shelf
        print(min_badcase_value)

        return best_candidate_shelf

    def _calculate_score(self, old_display_goods, start_width, candidate_level):
        if old_display_goods in self.down_display_goods_list:
            return 0
        candidate_start_width = 0
        for display_goods in candidate_level.display_goods_list:
            if display_goods.goods_data.equal(old_display_goods.goods_data):
                if abs(start_width - candidate_start_width) < 10:
                    return 0
                elif abs(start_width - candidate_start_width) < old_display_goods.goods_data.width * old_display_goods.face_num:
                    return 0.1
                else:
                    return 1
            candidate_start_width += display_goods.goods_data.width * display_goods.face_num
        return 1

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
        area_category3 = None
        one_display_goods_list = []

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
            display_goods_list = self.levelid_to_displaygoods_list[level_id]
            if len(display_goods_list) > 0:

                if area_category3 != display_goods_list[0].goods_data.category3:
                    # 开始一个新的area
                    area = Area(self)
                    self.area_list.append(area)
                    area_category3 = None

                for display_goods in display_goods_list:
                    if area_category3 is None:
                        area_category3 = display_goods.goods_data.category3
                        one_display_goods_list.append(display_goods)
                    else:
                        if area_category3 == display_goods.goods_data.category3:
                            one_display_goods_list.append(display_goods)
                        else:
                            # 结束上一个child_area, 开始一个新的child_area
                            area.add_child_area_in_one_category3(level_id, one_display_goods_list)
                            one_display_goods_list = [display_goods]
                            area_category3 = display_goods.goods_data.category3
                            # 开始一个新的area
                            area = Area(self)
                            self.area_list.append(area)

                # 结束上一个child_area, 开始一个新的child_area
                area.add_child_area_in_one_category3(level_id, one_display_goods_list)
                one_display_goods_list = []

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
            area.prepare_base_data(self.choose_goods_list)

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

        print('区域分解：')
        for area in self.area_list:
            print(area)

        up_info = '必须上架商品：'
        for area in self.area_list:
            for choose_goods in area.up_choose_goods_list:
                up_info += str(choose_goods)
                up_info += ','

        print(up_info)

        down_info = '必须下架商品：'
        for area in self.area_list:
            for display_goods in area.down_display_goods_list:
                down_info += str(display_goods.goods_data)
                down_info += ','
        print(down_info)

        second_up_info = '二次上架商品：'
        for area in self.area_list:
            for choose_goods in area.second_up_choose_goods_list:
                second_up_info += str(choose_goods)
                second_up_info += ','
        print(second_up_info)

        reduce_info = '减扩面商品：'
        for area in self.area_list:
            for display_goods in area.display_goods_to_reduce_face_num:
                reduce_info += str(display_goods.goods_data) + '(' + str(area.display_goods_to_reduce_face_num[display_goods])
                reduce_info += '),'
        print(reduce_info)

        second_down_info = '二次下架商品：'
        for area in self.area_list:
            for display_goods in area.second_down_display_goods_list:
                second_down_info += str(display_goods.goods_data)
                second_down_info += ','
        print(second_down_info)

    def _arrange_areas(self):
        """
        计算每个area的候选集
        :return:
        """
        len_area_list = 0
        for area in self.area_list:
            if len(area.up_choose_goods_list) > 0:
                len_area_list += 1

        if len_area_list in self.len_area_list_to_threshold:
            self.threshold = self.len_area_list_to_threshold[len_area_list]
        else:
            self.threshold = self.len_area_list_to_threshold[100]

        for area in self.area_list:
            area.calculate_candidate(self.candidate_step, self.threshold)

    def _generate_all_area_candidate(self):
        """
        组合所有的area候选集，生成shelf对象
        返回一个candidate_shelf_list
        :return:
        """

        # 组合所有area里面的candidate_display_goods_list_list

        total_list = []
        for area in self.area_list:
            total_list.append(area.candidate_display_goods_list_list)

        candidate_shelf_list = []
        for one_candidate_list in product(*total_list):
            candidate_shelf = self.arrange_goods(one_candidate_list)
            candidate_shelf_list.append(candidate_shelf)

        return candidate_shelf_list

    def arrange_goods(self, one_candidate_list):
        candidate_shelf = self.shelf.copy_raw()
        cur_level_index = 0
        cur_level_goods_width = 0
        area_index = 0
        cur_level = None
        for one_candidate in one_candidate_list:
            area = self.area_list[area_index]
            area_index += 1
            area_total_goods_width = 0
            for display_goods in one_candidate:
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

            if area_total_goods_width < area.total_width:
                # 占位nullgoods
                remain_width = area.total_width - area_total_goods_width

                remain_width_list = []
                if remain_width < candidate_shelf.width - cur_level_goods_width + 10:
                    remain_width_list.append(remain_width)
                    cur_level_goods_width += remain_width
                else:
                    remain_width_list.append(candidate_shelf.width - cur_level_goods_width)
                    remain_width = remain_width - (candidate_shelf.width - cur_level_goods_width)

                    while True:
                        if remain_width <= candidate_shelf.width:
                            remain_width_list.append(remain_width)
                            break
                        else:
                            remain_width_list.append(remain_width - candidate_shelf.width)
                            remain_width = remain_width - candidate_shelf.width

                index = -1
                for remain_width in remain_width_list:
                    index += 1
                    display_goods = DisplayGoods(NullGoodsData(remain_width))
                    if cur_level is None:
                        cur_level = candidate_shelf.levels[cur_level_index]
                    cur_level.add_display_goods(display_goods)
                    if index < len(remain_width_list)-1:
                        cur_level = candidate_shelf.levels[cur_level_index]
                        cur_level_index += 1
                        if cur_level_index >= len(candidate_shelf.levels):
                            print("陈列商品超出货架，陈列到此结束:{}".format(cur_level_index))
                            return candidate_shelf

        return candidate_shelf


class Area:
    def __init__(self, area_manager):
        self.area_manager = area_manager
        self.child_area_list = []
        self.category2 = None
        self.category3_list = []

        # 基础计算数据
        self.choose_goods_list = None
        self.up_choose_goods_list = []
        self.down_display_goods_list = []
        self.levelid_to_goods_width = {}
        self.levelid_to_remain_width = {}
        self.total_width = 0
        self.width_tolerance = 0

        # 动态计算数据
        self.display_goods_to_reduce_face_num = {}
        self.second_up_choose_goods_list = []
        self.second_down_display_goods_list = []

        # 结果数据
        self.candidate_display_goods_list_list = []

    def add_child_area_in_one_category3(self, level_id, display_goods_list):
        category2 = display_goods_list[0].goods_data.category2
        category3 = display_goods_list[0].goods_data.category3
        if self.category2 is None:
            self.category2 = category2
        else:
            if self.category2 != category2:
                msg = '同三级分类的商品二级分类不一样：{}'.format(category3)
                print(msg)
                dingtalk.send_message(msg, 2)
                raise ValueError(msg)

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

        return int(total_height / total_count)

    def combine_area(self, last_area):
        self.child_area_list = last_area.child_area_list + self.child_area_list
        self.category3_list = last_area.category3_list + self.category3_list

    def prepare_base_data(self, choose_goods_list):
        """
        准备选品数据，每层商品宽度，下架必下架品存储到child_area里，上架必上品存储到area里
        self.choose_goods_list = None
        self.up_choose_goods_list = []
        self.down_display_goods_list = []
        self.levelid_to_goods_width = {}
        self.levelid_to_remain_width = {}
        self.total_width = 0
        self.width_tolerance = 0
        :param choose_goods_list:
        :return:
        """
        # 筛选choose_goods_list
        choose_goods_list_in_area = []
        for goods in choose_goods_list:
            if goods.category3 in self.category3_list:
                if goods.goods_role in (0, 2, 4):
                    # FIXME 下架商品必须在货架上
                    pass
                choose_goods_list_in_area.append(goods)
        self.choose_goods_list = choose_goods_list_in_area

        # 计算每一层的商品宽度self.levelid_to_goods_width
        for child_area in self.child_area_list:
            goods_width = child_area.get_goods_width()
            self.total_width += goods_width
            if child_area.level_id in self.levelid_to_goods_width:
                self.levelid_to_goods_width[child_area.level_id] += goods_width
            else:
                self.levelid_to_goods_width[child_area.level_id] = goods_width

        # 计算每一层的可用剩余self.levelid_to_remain_width
        for level_id in self.levelid_to_goods_width.keys():
            goods_width = self.levelid_to_goods_width[level_id]
            # FIXME 这里有个问题,无法知晓该层是否被该区域完全占据，如果是整层占据应该不需要分享
            # 分享货架剩余空间
            self.levelid_to_remain_width[level_id] = int(
                self.area_manager.levelid_to_remain_width[level_id] * goods_width / self.area_manager.shelf.width)
            self.total_width += self.levelid_to_remain_width[level_id]
        self.width_tolerance = int(self.total_width / 20)

        # 计算下架必下架品
        for choose_goods in self.choose_goods_list:
            if choose_goods.goods_role == 2:
                for child_area in self.child_area_list:
                    if child_area.category3 == choose_goods.category3:
                        for display_goods in child_area.display_goods_list:
                            if display_goods.goods_data.equal(choose_goods):
                                child_area.down_display_goods_list.append(display_goods)
                                self.down_display_goods_list.append(display_goods)
                                self.area_manager.down_display_goods_list.append(display_goods)

        # 计算上架必上品
        for choose_goods in self.choose_goods_list:
            if choose_goods.goods_role == 1:
                self.up_choose_goods_list.append(choose_goods)
                self.area_manager.up_choose_goods_list.append(choose_goods)

        # 上架品由低到高排序，这样保证在上架商品在一起时，会出现由高到低插入
        self.up_choose_goods_list.sort(key=lambda x: x.height)


    def prepare_calculate_data(self):
        """
        同一分区内可能有一个或多个商品上架，也可能有0个或n个商品下架，优先挤扩面，扩面的销售产出按照psd金额/n递减计算；如需下架商品从分区内销售最差的商品开始选择
        self.display_goods_to_reduce_face_num = {}
        self.second_up_choose_goods_list = []
        self.second_down_display_goods_list = []
        :param choose_goods_list:
        :return:
        """
        # 第一大步：根据总宽控制进行选品或挤扩面或下品 # TODO 没考虑可选上架
        # 第一步：计算原已用总宽和剩余总宽
        used_total_width = 0
        remain_total_width = 0
        for level_id in self.levelid_to_goods_width.keys():
            used_total_width += self.levelid_to_goods_width[level_id]
            remain_total_width += self.levelid_to_remain_width[level_id]

        # 第二步：计算上下架后每层商品总宽度
        up_total_width = 0
        for up_choose_goods in self.up_choose_goods_list:
            up_total_width += up_choose_goods.width

        down_total_width = 0
        for down_display_goods in self.down_display_goods_list:
            down_total_width += down_display_goods.goods_data.width * down_display_goods.face_num

        if up_total_width == 0 and down_total_width == 0:
            return

        need_width = up_total_width - down_total_width - remain_total_width
        if up_total_width > 0:
            need_width += self.width_tolerance

        # 第三步：如需要：挤排面
        if need_width > 0:
            reduce_width = self._reduce_face_num(need_width)

            need_width = need_width - reduce_width
            # 第四步：如需要：下架商品
            if need_width > 0:
                reduce_width = self._down_other_goods(need_width)

            if need_width > reduce_width:
                print('出现无法解决的区域：')
                print(self)
        elif need_width < -100:
            add_width = self._up_other_goods(-need_width)
            if add_width + need_width < 100:
                print('出现无法解决的区域：')
                print(self)

    def calculate_candidate(self, candidate_step=1, candidate_threshold=5):
        """
        对所有确定好的上下架商品进行最优排列
        # 基础计算数据
        self.choose_goods_list = None
        self.up_choose_goods_list = []
        self.down_display_goods_list = []
        self.levelid_to_goods_width = {}
        self.levelid_to_remain_width = {}

        # 动态计算数据
        self.display_goods_to_reduce_face_num = {}
        self.second_up_choose_goods_list = []
        self.second_down_display_goods_list = []
        :param candidate_step:
        :param candidate_threshold:
        :return:
        """

        # 重组现在所有的display_goods,并生成新的拷贝
        new_display_goods_list = []
        for child_area in self.child_area_list:
            for display_goods in child_area.display_goods_list:
                if display_goods not in self.down_display_goods_list and display_goods not in self.second_down_display_goods_list:
                    if display_goods in self.display_goods_to_reduce_face_num:
                        face_num = display_goods.face_num -self.display_goods_to_reduce_face_num[display_goods]
                    else:
                        face_num = display_goods.face_num
                    new_display_goods = DisplayGoods(display_goods.goods_data,
                                                     face_num=face_num,
                                                     superimpose_num=display_goods.superimpose_num)
                    new_display_goods_list.append(new_display_goods)

        if len(self.up_choose_goods_list) > 0 or len(self.second_up_choose_goods_list) > 0:
            self._generate_up_choose_goods_candidate(new_display_goods_list, candidate_step, candidate_threshold)
        else:
            # TODO 做候选上架处理
            self.candidate_display_goods_list_list.append(new_display_goods_list)

    def _generate_up_choose_goods_candidate(self, new_display_goods_list, candidate_step, candidate_threshold):
        # 先计算首个插入的位置
        up_choose_goods_to_insert_position = {}
        up_choose_goods_list = []
        up_choose_goods_list.extend(self.up_choose_goods_list)
        up_choose_goods_list.extend(self.second_up_choose_goods_list)
        for up_choose_goods in up_choose_goods_list:
            for i in range(len(new_display_goods_list) - 1, -1, -1):
                if new_display_goods_list[i].goods_data.category3 == up_choose_goods.category3:
                    up_choose_goods_to_insert_position[up_choose_goods] = [i + 1]
                    break

            # 防止同类商品全部下架
            if up_choose_goods not in up_choose_goods_to_insert_position:
                up_choose_goods_to_insert_position[up_choose_goods] = [len(new_display_goods_list)]


        up_choose_goods_to_end = {}
        for up_choose_goods in up_choose_goods_list:
            up_choose_goods_to_end[up_choose_goods] = False
        # 逐步往后挪动插入位置
        candidate_cnt = 1
        while candidate_cnt < candidate_threshold:
            for up_choose_goods in up_choose_goods_to_insert_position.keys():
                if not up_choose_goods_to_end[up_choose_goods]:
                    insert_position = up_choose_goods_to_insert_position[up_choose_goods][-1]

                    next_position = insert_position - candidate_step
                    if next_position >= 0 and new_display_goods_list[
                                next_position - 1].goods_data.category3 == up_choose_goods.category3:
                        up_choose_goods_to_insert_position[up_choose_goods].append(next_position)

                        candidate_cnt = self._calculate_candidate_cnt(up_choose_goods_to_insert_position)
                        if candidate_cnt >= candidate_threshold:
                            break
                    else:
                        up_choose_goods_to_end[up_choose_goods] = True

            # 判断是否已经没有解
            is_end = True
            for up_choose_goods in up_choose_goods_list:
                if not up_choose_goods_to_end[up_choose_goods]:
                    is_end = False
            if is_end:
                break

        # FIXME 同一个三级分类的上架多个品，出现的候选解要变化
        # 取出所有解的集合
        up_choose_goods_to_candidate_list = dict_arrange(up_choose_goods_to_insert_position)
        for up_choose_goods_to_candidate in up_choose_goods_to_candidate_list:
            candidate_display_goods_list = new_display_goods_list.copy()
            insert_candidate_list = list(up_choose_goods_to_candidate.items())
            insert_candidate_list.sort(key=lambda x: x[1], reverse=True)
            for insert_candidate in insert_candidate_list:
                # FIXME 暂时没有处理上架商品的face_num 和 superimpose_num
                candidate_display_goods_list.insert(insert_candidate[1], DisplayGoods(insert_candidate[0]))

            self.candidate_display_goods_list_list.append(candidate_display_goods_list)

    def _calculate_candidate_cnt(self, key_to_candidate_list):
        ret = 1
        for key in key_to_candidate_list.keys():
            ret *= len(key_to_candidate_list[key])
        return ret

    def _reduce_face_num(self, need_width):
        """
        操作self.display_goods_to_reduce_face_num
        扩面的销售产出按照psd金额/n递减计算
        :param need_width:
        :return: reduce_width
        """
        #
        reduce_width = 0

        reduce_face_display_goods_list = []
        for child_area in self.child_area_list:
            for display_goods in child_area.display_goods_list:
                # 必须下架的商品要排除
                if display_goods not in self.down_display_goods_list:
                    if display_goods.face_num > 1:
                        reduce_face_display_goods_list.append(display_goods)

        reduce_face_display_goods_list.sort(key=lambda x: x.goods_data.psd_amount / x.face_num)

        second_reduce_face_display_goods_list = []
        for reduce_face_display_goods in reduce_face_display_goods_list:
            reduce_width += reduce_face_display_goods.goods_data.width
            self.display_goods_to_reduce_face_num[reduce_face_display_goods] = 1
            if reduce_face_display_goods.face_num > 2:
                second_reduce_face_display_goods_list.append(reduce_face_display_goods)
            if reduce_width > need_width:
                break

        # 最多减两轮face
        if reduce_width < need_width:
            for reduce_face_display_goods in second_reduce_face_display_goods_list:
                reduce_width += reduce_face_display_goods.goods_data.width
                self.display_goods_to_reduce_face_num[reduce_face_display_goods] += 1
                if reduce_width > need_width:
                    break

        return reduce_width

    def _up_other_goods(self, need_width):
        """
        # 操作self.second_up_display_goods_list 和 self.area_manager.up_choose_goods_list
        计算进一步需要上架的商品
        :param need_width:
        :return:
        """

        add_width = 0

        candidate_up_choose_goods_list = []
        for child_area in self.child_area_list:
            for choose_goods in self.choose_goods_list:
                # 必须下架的商品要排除
                if choose_goods.goods_role == 3: # 只能是可选上架商品
                    candidate_up_choose_goods_list.append(choose_goods)

        candidate_up_choose_goods_list.sort(key=lambda x: x.psd_amount, reverse=True)
        for up_choose_goods in candidate_up_choose_goods_list:
            add_width += up_choose_goods.width
            self.second_up_choose_goods_list.append(up_choose_goods)
            self.area_manager.up_choose_goods_list.append(up_choose_goods)
            if add_width > need_width-100:
                break

        return add_width

    def _down_other_goods(self, need_width):
        """
        # 操作self.second_down_display_goods_list 和 self.area_manager.down_display_goods_list
        计算进一步需要下架的商品
        :param need_width:
        :return:
        """

        reduce_width = 0

        candidate_down_display_goods_list = []
        for child_area in self.child_area_list:
            for display_goods in child_area.display_goods_list:
                # 必须下架的商品要排除
                if display_goods not in self.down_display_goods_list:
                    candidate_down_display_goods_list.append(display_goods)

        candidate_down_display_goods_list.sort(key=lambda x: x.goods_data.psd_amount)
        for down_display_goods in candidate_down_display_goods_list:
            reduce_width += down_display_goods.goods_data.width
            self.second_down_display_goods_list.append(down_display_goods)
            self.area_manager.down_display_goods_list.append(down_display_goods)
            if reduce_width > need_width:
                break

        return reduce_width

    def __str__(self):
        ret = str(self.category3_list) + ':' + str(self.total_width) + ':'
        for area_level in self.child_area_list:
            ret += str(area_level)
        return ret


class ChildArea:
    def __init__(self, level_id, display_goods_list):
        self.level_id = level_id
        self.display_goods_list = display_goods_list
        self.down_display_goods_list = []
        self.category3 = display_goods_list[0].goods_data.category3

    def get_goods_width(self):
        goods_width = 0
        for display_goods in self.display_goods_list:
            goods_width += display_goods.goods_data.width * display_goods.face_num
        return goods_width

    def __str__(self):
        ret = str(self.level_id) + '-' + str(self.category3) + ':['
        for display_goods in self.display_goods_list:
            for i in range(display_goods.face_num):
                ret += str(display_goods.goods_data)
                ret += ','
        ret += '], '

        return ret


if __name__ == '__main__':
    pass
