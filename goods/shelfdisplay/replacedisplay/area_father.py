"""
区域求解，在一个区域内将必须上架和必须下架的商品处理完毕，并获的候选解
"""

from goods.shelfdisplay.normal_algorithm import dict_arrange
from goods.shelfdisplay.replacedisplay.area_child import ChildArea
from goods.shelfdisplay.replacedisplay.display_object import DisplayGoods
from goods.third_tools import dingtalk


class Area:
    max_width_tolerance = 20

    def __init__(self, area_manager):
        self.area_manager = area_manager
        self.child_area_list = []
        self.category2 = None
        self.category3_list = []

        # 基础计算数据
        self.choose_goods_list = []
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


    def calculate_width(self):
        """
        self.levelid_to_goods_width = {}
        self.levelid_to_remain_width = {}
        self.total_width = 0
        self.width_tolerance = 0
        :return:
        """

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
        if self.width_tolerance > self.max_width_tolerance:
            self.width_tolerance = self.max_width_tolerance

    def prepare_goods_data(self):
        """
        准备选品数据，每层商品宽度，下架必下架品存储到child_area里，上架必上品存储到area里
        self.up_choose_goods_list = []
        self.down_display_goods_list = []
        :return:
        """

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
        # if up_total_width > 0:
        #     need_width += self.width_tolerance

        # 第三步：如需要：挤排面
        if need_width > 0:
            reduce_width = self._reduce_face_num(need_width)

            need_width = need_width - reduce_width
            # 第四步：如需要：下架商品
            if need_width > self.width_tolerance:
                reduce_width = self._down_other_goods(need_width)

            if reduce_width + self.width_tolerance < need_width:
                print('挤下商品无法解决的区域：')
                # dingtalk.send_message(str(self), 2)
                print(self)
        elif need_width < 0:
            add_width = self._up_other_goods(-need_width)
            if add_width + need_width < self.width_tolerance:
                print('增上商品出现无法解决的区域：')
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
            # 减少太多就放弃
            if reduce_width + reduce_face_display_goods.goods_data.width > need_width + self.width_tolerance:
                break
            reduce_width += reduce_face_display_goods.goods_data.width
            self.display_goods_to_reduce_face_num[reduce_face_display_goods] = 1
            if reduce_face_display_goods.face_num > 2:
                second_reduce_face_display_goods_list.append(reduce_face_display_goods)
            if reduce_width >= need_width:
                break

        # 最多减两轮face
        if reduce_width < need_width:
            for reduce_face_display_goods in second_reduce_face_display_goods_list:
                # 减少太多就放弃
                if reduce_width + reduce_face_display_goods.goods_data.width > need_width + self.width_tolerance:
                    break
                reduce_width += reduce_face_display_goods.goods_data.width
                self.display_goods_to_reduce_face_num[reduce_face_display_goods] += 1
                if reduce_width >= need_width:
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
        for choose_goods in self.choose_goods_list:
            # 必须没有被上架过
            if choose_goods in self.area_manager.up_choose_goods_list:
                continue
            # 必须下架的商品要排除
            if choose_goods.goods_role == 3: # 只能是可选上架商品
                candidate_up_choose_goods_list.append(choose_goods)

        candidate_up_choose_goods_list.sort(key=lambda x: x.psd_amount, reverse=True)
        for up_choose_goods in candidate_up_choose_goods_list:
            # 超出太多就放弃
            if add_width + up_choose_goods.width > need_width + self.width_tolerance:
                break
            add_width += up_choose_goods.width
            self.second_up_choose_goods_list.append(up_choose_goods)
            self.area_manager.up_choose_goods_list.append(up_choose_goods)
            if add_width >= need_width:
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
            # 减少太多就放弃
            if reduce_width + down_display_goods.goods_data.width > need_width + self.width_tolerance:
                break
            reduce_width += down_display_goods.goods_data.width
            self.second_down_display_goods_list.append(down_display_goods)
            self.area_manager.down_display_goods_list.append(down_display_goods)
            if reduce_width >= need_width:
                break

        return reduce_width

    def __str__(self):
        ret = str(self.category3_list) + ':' + str(self.total_width) + ':'
        for area_level in self.child_area_list:
            ret += str(area_level)
        return ret

