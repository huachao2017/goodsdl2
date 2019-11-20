from django.db import connections
from goods.shelfdisplay.single_algorithm import calculate_shelf_category3_area_ratio


def init_data(uc_shopid, tz_id, base_data):
    taizhang = Taizhang(tz_id)
    cursor = connections['ucenter'].cursor()

    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账
    try:
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.id = {}".format(
                uc_shopid, tz_id))
        (taizhang_id, shelf_id, count, third_cate_ids) = cursor.fetchone()
    except:
        print('获取台账失败：{},{}！'.format(uc_shopid, tz_id))
        raise ValueError('taizhang error:{},{}'.format(uc_shopid, tz_id))

    cursor.execute(
        "select t.shelf_no,s.length,s.height,s.depth,s.hole_height,s.hole_distance from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(
            shelf_id))
    (shelf_no, length, height, depth, hole_height, hole_distance) = cursor.fetchone()

    # 计算五个值
    display_category3_list = third_cate_ids.split(',')
    shelf_category3_list = []
    # 检查所有三级分类
    for category3 in display_category3_list:
        try:
            cursor.execute(
                "select id from uc_category where mch_id={} and cat_id='{}' and level=3".format(
                    mch_id, category3))
            (id,) = cursor.fetchone()
            shelf_category3_list.append(category3)
        except:
            print('台账陈列类别无法找到：{}！'.format(category3))

    if len(shelf_category3_list) == 0:
        raise ValueError('no display category:{},{}'.format(uc_shopid, taizhang_id))

    shelf_category3_intimate_weight = {}
    shelf_category3_level_value = {}
    for shelf_category in shelf_category3_list:
        for category3_list_str in base_data.category3_intimate_weight.keys():
            # 做部分删减
            category3_list = category3_list_str.split(',')
            if shelf_category in category3_list:
                shelf_category3_intimate_weight[category3_list_str] = base_data.category3_intimate_weight[
                    category3_list_str]
        if shelf_category in base_data.category3_level_value:
            shelf_category3_intimate_weight[shelf_category] = base_data.shelf_category3_level_value[shelf_category]

    # 重新计算货架的三级分类比例
    shelf_category3_area_ratio = calculate_shelf_category3_area_ratio(shelf_category3_list, base_data.category_area_ratio)
    shelf_goods_data_list = []
    for goods in base_data.goods_data_list:
        if goods.category3 in shelf_category3_list:
            shelf_goods_data_list.append(goods)
    print('总共获取的候选陈列商品：{}个'.format(len(shelf_goods_data_list)))

    for i in range(count):
        shelf = Shelf(shelf_id, shelf_no, length, height, depth,
                      shelf_category3_list,
                      shelf_category3_intimate_weight,
                      shelf_category3_level_value,
                      shelf_category3_area_ratio,
                      shelf_goods_data_list)
        taizhang.shelfs.append(shelf)

    cursor.close()
    return taizhang


class Taizhang:
    tz_id = None
    shelfs = []

    def __init__(self, tz_id):
        self.tz_id = tz_id

    def to_json(self):
        """
        :return:
        {
        taizhang_id:xx
        shelfs:[{
            shelf:xx
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
            if shelf.best_candidate_shelf is not None:
                for level in shelf.best_candidate_shelf.levels:
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
    average_level_height = 300 # 平均高度，用于计算剩余货架宽度

    shelf_category3_list = None  # 货架指定分类列表
    shelf_category3_intimate_weight = None  # 货架分类涉及的亲密度分值
    shelf_category3_level_value = None  # 货架分类涉及的层数分值
    shelf_category3_area_ratio = None  # 货架内分类面积比例
    shelf_goods_data_list = []  # 货架候选商品列表

    # 以上都是初始化后就会有的数据

    # 计算用到的参数
    candidate_category_list = None
    categoryid_to_sorted_goods_list = None  # 候选商品列表
    extra_add_num = 2  # 每类冗余数量

    best_candidate_shelf = None

    def __init__(self, shelf_id, type, width, height, depth,
                 shelf_category3_list,
                 shelf_category3_intimate_weight,
                 shelf_category3_level_value,
                 shelf_category3_area_ratio,
                 shelf_goods_data_list):
        self.shelf_id = shelf_id
        self.type = type
        self.width = width
        self.height = height
        self.depth = depth

        self.shelf_category3_list = shelf_category3_list
        self.shelf_category3_intimate_weight = shelf_category3_intimate_weight
        self.shelf_category3_level_value = shelf_category3_level_value
        self.shelf_category3_area_ratio = shelf_category3_area_ratio
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
            ret -= self.shelf.width - last_level.goods_width
            # 货架高度剩余很多就加一个货架宽度
            if (self.shelf.height - last_level.start_height) > 2*self.shelf.average_level_height:
                ret -= self.shelf.width
            # 空缺宽度

        return ret


class Level:
    candidate_shelf = None  # 候选货架
    level_id = None  # 层id
    is_left_right_direction = True  # True从左向右，False从右向左
    goods_width = 0  # 层宽度
    start_height = None  # 层板相对货架的起始高度
    goods_height = 0  # 商品最高高度
    # level_depth = None  # 层深度

    display_goods_list = []  # 陈列商品集合

    def __init__(self, candidate_shelf, level_id, start_height, is_left_right_direction):
        self.candidate_shelf = candidate_shelf
        self.level_id = level_id
        self.is_left_right_direction = is_left_right_direction
        self.start_height = start_height
        candidate_shelf.levels.append(self)

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

    taizhang = init_data(806, 1187, base_data)
    print(taizhang.to_json())
