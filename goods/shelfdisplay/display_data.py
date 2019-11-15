from django.db import connections

def init_data(tz_id, goods_data_list):
    taizhang = Taizhang()
    # TODO 获取数据
    return taizhang


class Taizhang:
    tz_id=None
    shelfs = []
    associated_catids = None

    candidate_goods_data_list = []

    def to_json(self):
        """
        :return:
        {
        taizhang_id:xx
        shelfs:[{
            shelf_id:xx
            levels:[{
                level_id:xx   #0是底层,1,2,3,4...
                height:xx
                hole_num:xx
                goods:[{
                    mch_goods_code:
                    upc:
                    width:
                    height:
                    depth:
                    displays:[{
                        top:
                        left:
                        row:
                        col:
                        },
                        {
                        ...
                        }]
                    },
                    {
                    ...
                    }]
                },
                {
                ...
                }]
            },
            {
            ...
            }]
        }
        """
        json_ret = {
            "taizhang_id":self.tz_id,
            "shelfs":[]
        }
        for shelf in self.shelfs:
            json_shelf={
                "shelf":shelf.shelf_id,
                "levels":[]
            }
            json_ret["shelfs"].append(json_shelf)
            for level in shelf.levels:
                if level.isTrue:
                    json_level = {
                        "level_id":level.level_id,
                        "height":level.level_height,
                        "goods":[]
                    }
                    json_shelf["levels"].append(json_level)
                    for good in level.goods:
                        json_goods = {
                            "mch_good_code": good.goods_data.mch_code,
                            "upc": good.goods_data.upc,
                            "width":good.goods_data.width,
                            "height":good.goods_data.height,
                            "depth":good.goods_data.depth,
                            "displays": []
                        }
                        json_level["goods"].append(json_goods)
                        # TODO
                        # for gooddisplay in good.gooddisplay_inss:
                        #     if gooddisplay.dep == 0:
                        #         json_display = {
                        #             "top": gooddisplay.top,
                        #             "left": gooddisplay.left,
                        #             "row": gooddisplay.row,
                        #             "col": gooddisplay.col,
                        #         }
                        #         json_goods["displays"].append(json_display)

        return json_ret

class Shelf:
    shelf_id = None

    # 空间参数
    width = None
    height = None
    depth = None
    bottom_height = 50 # 底层到地面的高度 # TODO 需考虑初始化
    level_board_height = 20 # 层板高度 # TODO 需考虑初始化
    level_buff_height = 30 # 层冗余高度 # TODO 需考虑初始化
    last_level_min_remain_height = 150 # 最后一层最小剩余高度

    # 计算用到的参数
    categoryid_to_sorted_goods_list = None # 候选商品列表
    extra_add_num = 2 # 每类冗余数量
    goods_arrange_weight = None

    best_candidate_shelf = None


class CandidateShelf:
    shelf = None
    categoryid_list = None
    categoryid_to_used_sorted_goods_list = {}
    categoryid_to_candidate_sorted_goods_list = {}

    categoryid_to_arrange_goods_list = None
    levels = []
    badcase_value = 0
    goods_mean_width = 0

    def __init__(self, shelf, categoryid_list, categoryid_to_arrange_goods_list):
        self.shelf = shelf
        self.categoryid_list = categoryid_list
        self.categoryid_to_arrange_goods_list = categoryid_to_arrange_goods_list

        goods_total_width = 0
        goods_num = 0
        for categoryid in shelf.categoryid_to_sorted_goods_list.keys():
            self.categoryid_to_used_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[categoryid][:-shelf.extra_add_num]
            self.categoryid_to_candidate_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[categoryid][-shelf.extra_add_num:]

            for goods in self.categoryid_to_used_sorted_goods_list[categoryid]:
                goods_num += 1
                goods_total_width += goods.width * goods.face_num

        self.goods_mean_width = goods_total_width/goods_num

    def get_real_arrange_goods_list(self, categoryid):
        """
        根据用到商品筛选商品排序表
        :param categoryid:
        :return:
        """
        arrange_goods_list = self.categoryid_to_arrange_goods_list[categoryid]

        used_goods_list = self.categoryid_to_used_sorted_goods_list[categoryid]

        real_arrange_goods_list = []
        for arrange_goods in arrange_goods_list:
            for used_goods in used_goods_list:
                if arrange_goods.mch_code == used_goods.mch_code:
                    real_arrange_goods_list.append(arrange_goods)
                    break

        return real_arrange_goods_list


    def recalculate(self):
        self.leves = []
        self.badcase_value = 0

    def calculate_addition_width(self):
        """
        计算货架多余或缺失宽度
        :return: 超出或不足的width
        """

        last_level = self.levels[-1]

        ret = 0
        if self.shelf.height - last_level.start_height < self.shelf.last_level_min_remain_height:
            # 超出层
            ret += last_level.goods_width
        else:
            # 空缺宽度
            ret -= self.shelf.width - last_level.goods_width

        return ret


class Level:
    candidate_shelf = None # 候选货架
    level_id = None # 层id
    is_left_right_direction = True # True从左向右，False从右向左
    goods_width = None  # 层宽度
    start_height = None  # 层板相对货架的起始高度
    goods_height = 0     # 商品最高高度
    # level_depth = None  # 层深度

    display_goods_list = []  # 陈列商品集合

    def __init__(self, candidate_shelf, level_id, start_height, is_left_right_direction):
        self.candidate_shelf = candidate_shelf
        self.level_id = level_id
        self.is_left_right_direction = is_left_right_direction
        self.start_height = start_height

    def display_goods(self, display_goods):
        if display_goods.get_width() + self.goods_width > self.candidate_shelf.shelf.width:
            # TODO 需要考虑拆分
            return False
        self.display_goods_list.append(display_goods)

        # 更新宽度
        self.goods_width += display_goods.get_width()

        # 更新高度
        if self.goods_height < display_goods.get_height():
            self.goods_height = display_goods.get_height()

        return True


class DisplayGoods:
    #初始化数据
    goods_data = None

    #计算信息
    # face_num = 1 # 陈列几个face
    # superimpose_rows = 1 # 叠放几行

    def __init__(self, goods_data):
        self.goods_data = goods_data

    def get_width(self):
        return self.goods_data.width * self.goods_data.face_num

    def get_height(self):
        return self.goods_data.height * self.goods_data.superimpose_num