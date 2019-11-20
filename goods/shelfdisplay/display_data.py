from django.db import connections
from goods.shelfdisplay.single_algorithm import calculate_shelf_category_area_ratio


def init_data(uc_shopid, tz_id, base_data):
    taizhang = Taizhang()
    cursor = connections['ucenter'].cursor()
    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账
    try:
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.id = {}".format(
                uc_shopid, tz_id))
        (taizhang_id, shelf_id, count) = cursor.fetchone()
    except:
        print('获取台账失败：{},{}！'.format(uc_shopid, tz_id))
        raise ValueError('taizhang error:{},{}'.format(uc_shopid, tz_id))

    # 获取商店台账可放的品类
    try:
        cursor.execute(
            "select associated_catids from sf_taizhang_display where taizhang_id = {} and status in (0,1) and approval_status = 0".format(
                taizhang_id))
        (associated_catids,) = cursor.fetchone()
    except:
        print('获取台账陈列失败：{}！'.format(taizhang_id))
        associated_catids = None
    if associated_catids is None or associated_catids == '':
        associated_catids = '0501,0502,0503,0504,0505,0506'  # FIXME only for test

    cursor.execute(
        "select t.shelf_no,s.length,s.height,s.depth,s.hole_height,s.hole_distance from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(
            shelf_id))
    (shelf_no, length, height, depth, hole_height, hole_distance) = cursor.fetchone()

    # 计算五个值
    shelf_category_list = associated_catids.split(',')
    shelf_category3_intimate_weight = {}
    shelf_category3_level_value = {}
    for shelf_category in shelf_category_list:
        for category3_list_str in base_data.category3_intimate_weight.keys():
            # 做部分删减
            category3_list = category3_list_str.split(',')
            if shelf_category in category3_list:
                shelf_category3_intimate_weight[category3_list_str] = base_data.category3_intimate_weight[
                    category3_list_str]
        if shelf_category in base_data.category3_level_value:
            shelf_category3_intimate_weight[shelf_category] = base_data.shelf_category3_level_value[shelf_category]

    # 重新计算货架的三级分类比例
    shelf_category_area_ratio = calculate_shelf_category_area_ratio(shelf_category_list, base_data.category_area_ratio)
    shelf_goods_data_list = []
    for goods in base_data.goods_data_list:
        if goods.category3 in shelf_category_list:
            shelf_goods_data_list.append(goods)

    for i in range(count):
        shelf = Shelf(shelf_id, shelf_no, length, height, depth,
                      shelf_category_list,
                      shelf_category3_intimate_weight,
                      shelf_category3_level_value,
                      shelf_category_area_ratio,
                      shelf_goods_data_list)
        taizhang.shelfs.append(shelf)

    cursor.close()
    return taizhang


class Taizhang:
    tz_id = None
    shelfs = []

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
            "taizhang_id": self.tz_id,
            "shelfs": []
        }
        for shelf in self.shelfs:
            json_shelf = {
                "shelf": shelf.shelf_id,
                "levels": []
            }
            json_ret["shelfs"].append(json_shelf)
            for level in shelf.best_candidate_shelf.levels:
                if level.isTrue:
                    json_level = {
                        "level_id": level.level_id,
                        "height": level.level_height,
                        "goods": []
                    }
                    json_shelf["levels"].append(json_level)
                    for display_goods in level.get_left_right_display_goods_list():
                        json_goods = {
                            "mch_good_code": display_goods.goods_data.mch_code,
                            "upc": display_goods.goods_data.upc,
                            "width": display_goods.goods_data.width,
                            "height": display_goods.goods_data.height,
                            "depth": display_goods.goods_data.depth,
                            "displays": []
                        }
                        json_level["goods"].append(json_goods)
                        for goods_display_info in display_goods.get_display_info(level):
                            json_display = {
                                "top": goods_display_info.top,
                                "left": goods_display_info.left,
                                "row": goods_display_info.row,
                                "col": goods_display_info.col,
                            }
                            json_goods["displays"].append(json_display)

        return json_ret


class Shelf:
    shelf_id = None
    type = None

    # 空间参数
    width = None
    height = None
    depth = None
    bottom_height = 50  # 底层到地面的高度 # TODO 需考虑初始化
    level_board_height = 20  # 层板高度 # TODO 需考虑初始化
    level_buff_height = 30  # 层冗余高度 # TODO 需考虑初始化
    last_level_min_remain_height = 150  # 最后一层最小剩余高度

    shelf_category_list = None  # 货架指定分类列表
    shelf_category3_intimate_weight = None  # 货架分类涉及的亲密度分值
    shelf_category3_level_value = None  # 货架分类涉及的层数分值
    shelf_category_area_ratio = None  # 货架内分类面积比例
    shelf_goods_data_list = []  # 货架候选商品列表

    # 以上都是初始化后就会有的数据

    # 计算用到的参数
    candidate_category_list = None
    categoryid_to_sorted_goods_list = None  # 候选商品列表
    extra_add_num = 2  # 每类冗余数量

    best_candidate_shelf = None

    def __init__(self, shelf_id, type, width, height, depth,
                 shelf_category_list,
                 shelf_category3_intimate_weight,
                 shelf_category3_level_value,
                 shelf_category_area_ratio,
                 shelf_goods_data_list):
        self.shelf_id = shelf_id
        self.type = type
        self.width = width
        self.height = height
        self.depth = depth

        self.shelf_category_list = shelf_category_list
        self.shelf_category3_intimate_weight = shelf_category3_intimate_weight
        self.shelf_category3_level_value = shelf_category3_level_value
        self.shelf_category_area_ratio = shelf_category_area_ratio
        self.shelf_goods_data_list = shelf_goods_data_list


class CandidateShelf:
    shelf = None
    categoryid_list = None
    categoryid_to_used_sorted_goods_list = {}
    categoryid_to_candidate_sorted_goods_list = {}

    categoryid_to_arrange_goods_list = None
    levels = []
    badcase_value = 0.0
    goods_mean_width = 0

    def __init__(self, shelf, categoryid_list, categoryid_to_arrange_goods_list):
        self.shelf = shelf
        self.categoryid_list = categoryid_list
        self.categoryid_to_arrange_goods_list = categoryid_to_arrange_goods_list

        goods_total_width = 0
        goods_num = 0
        for categoryid in shelf.categoryid_to_sorted_goods_list.keys():
            self.categoryid_to_used_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[categoryid][
                                                                    :-shelf.extra_add_num]
            self.categoryid_to_candidate_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[
                                                                             categoryid][-shelf.extra_add_num:]

            for goods in self.categoryid_to_used_sorted_goods_list[categoryid]:
                goods_num += 1
                goods_total_width += goods.width * goods.face_num

        self.goods_mean_width = goods_total_width / goods_num

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
        self.badcase_value = 0.0

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
    candidate_shelf = None  # 候选货架
    level_id = None  # 层id
    is_left_right_direction = True  # True从左向右，False从右向左
    goods_width = None  # 层宽度
    start_height = None  # 层板相对货架的起始高度
    goods_height = 0  # 商品最高高度
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

    def get_nono_goods_width(self):
        return self.candidate_shelf.shelf.width - self.goods_width

    def get_left_right_display_goods_list(self):
        if self.is_left_right_direction:
            return self.display_goods_list
        else:
            return self.display_goods_list[::-1]


class DisplayGoods:
    # 初始化数据
    goods_data = None

    # 计算信息
    # face_num = 1 # 陈列几个face
    # superimpose_rows = 1 # 叠放几行

    def __init__(self, goods_data):
        self.goods_data = goods_data

    def get_width(self):
        return self.goods_data.width * self.goods_data.face_num

    def get_height(self):
        return self.goods_data.height * self.goods_data.superimpose_num

    def get_display_info(self, level):
        """
        :return:GoodsDisplayInfo列表
        """
        display_goods_info = []
        display_goods_list = level.get_left_right_display_goods_list()
        init_top = self.goods_data.height
        init_left = 0
        for display_goods in display_goods_list:
            if self.goods_data.equal(display_goods.goods_data):
                break
            init_left += display_goods.get_width()
        for i in range(self.goods_data.face_num):
            for j in range(self.goods_data.superimpose_num):
                col = i
                row = j
                top = init_top + j * self.goods_data.height
                left = init_left + i * self.goods_data.width
                display_goods_info.append(DisplayOneGoodsInfo(col, row, top, left))

        return []


class DisplayOneGoodsInfo:
    col = None  # 在level上的列
    row = None  # 行
    top = None
    left = None

    def __init__(self, col, row, top, left):
        self.col = col
        self.row = row
        self.top = top
        self.left = left

if __name__ == "__main__":
    from goods.shelfdisplay import db_data
    base_data = db_data.init_data(806)

    taizhang = init_data(806, 1173, base_data)
    print(taizhang.to_json())
