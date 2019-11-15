"""
输入：货架三级分类排列候选，货架内选品列表，三级分类的面积比例
输出：货架陈列
目标：总体得分最高

每层货架高度 = 当层商品最大高度+buff+层板高（可默认20mm）
商品扩面数 = n*psd/最大成列量（初始n默认为3）
spu：四级分类、品牌、规格（包装）、尺寸（只选宽和高）四个特征均相同，一个spu一起加入排序
强制条件：同品或同spu不拆分
根据算法4.1选品和算法4.2商品排列计算所有候选解。
根据算法4.3打分规则在给每个解打分后，获得最优解。
"""

from goods.shelfdisplay import single_algorithm
from goods.shelfdisplay import display_data

def goods_arrange(shelf, candidate_categoryid_list, goods_data_list, category_area_ratio, goods_arrange_weight):
    """
    第四步，商品布局主体函数
    :param shelf:货架
    :param candidate_categoryid_list: 货架三级分类排列候选
    :param goods_data_list: 候选商品
    :param category_area_ratio: 面积比例
    :param goods_arrange_weight: 商品排列权重
    :return:
    """

    # 一、准备工作
    # 1、计算扩面
    _solve_goods_face(shelf.depth, goods_data_list)
    # 2、计算spu
    # 3、每一个三级分类获得排序商品
    extra_add_num = 2 # TODO 冗余数量怎么定，如果没有了呢？
    categoryid_to_sorted_goods_list = {}
    _calcuate_shelf_category_area_ratio(shelf, candidate_categoryid_list[0], category_area_ratio)
    for categoryid in candidate_categoryid_list[0]:
        sorted_goods_list = single_algorithm.choose_goods_for_category3(categoryid, category_area_ratio, goods_data_list, shelf, extra_add=extra_add_num)
        categoryid_to_sorted_goods_list[categoryid] = sorted_goods_list

    # 设定shelf的全局计算参数
    shelf.categoryid_to_sorted_goods_list = categoryid_to_sorted_goods_list
    shelf.extra_add_num = extra_add_num
    shelf.goods_arrange_weight = goods_arrange_weight
    # 生成所有的候选解
    candidate_result_shelf_list = []
    for categoryid_list in candidate_categoryid_list:
        candidate_result_shelf_list.extend(
            _display_shelf(shelf, categoryid_list)
        )

    # 计算候选解的badcase得分
    best_candidate_shelf = single_algorithm.goods_badcase_score(candidate_result_shelf_list)

    shelf.best_candidate_shelf = best_candidate_shelf

    return True

def _display_shelf(shelf, categoryid_list):
    """
    陈列主算法
    :param shelf: 实际货架
    :param categoryid_list: 三级分类排序
    :return: 候选货架解列表
    """
    candidate_result_shelf_list = []

    candidate_shelf = display_data.CandidateShelf(shelf, categoryid_list)

    for i in range(5): # 试错5次
        candidate_shelf.recalculate()
        _try_display_shelf(candidate_shelf)
        # 计算货架多余或缺失宽度
        addition_width = shelf.calculate_addition_width()

        if addition_width > 0:
            # 陈列越界
            if addition_width < candidate_shelf.goods_mean_width*2: # TODO 阈值多少合适？
                # 舍弃最后一层，并退出试错
                candidate_shelf.levels = candidate_shelf.levels[:-1]
                break

            # 减少候选品
            reduce_width = 0
            for j in range(3): # 每个品最多减三轮
                for categoryid in candidate_shelf.categoryid_to_used_sorted_goods_list.keys():
                    goods = candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid][-1]
                    reduce_width += goods.width*goods.face_num
                    candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid] = candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid][:-1]
                    candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid].insert(0,goods)
                    if reduce_width > addition_width:
                        break
                if reduce_width > addition_width:
                    break
        else:
            # 成列不足
            positive_addition_width = -addition_width
            if positive_addition_width < candidate_shelf.goods_mean_width*2: # TODO 阈值多少合适？
                # 退出试错
                break

            # 增加候选品
            add_width = 0
            for j in range(2): # 每个品最多减两轮
                for categoryid in candidate_shelf.categoryid_to_used_sorted_goods_list.keys():
                    if len(candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid])>0: # 防止没有候选商品
                        goods = candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid][0]
                        add_width += goods.width*goods.face_num
                        candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid].append(goods)
                        candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid] = candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid][1:]
                        if add_width > positive_addition_width:
                            break
                if add_width > positive_addition_width:
                    break

    return candidate_result_shelf_list


def _try_display_shelf(candidate_shelf):
    for categoryid in candidate_shelf.categoryid_list:
        arrange_goods_list = single_algorithm.goods_arrange(
            candidate_shelf.shelf.categoryid_to_sorted_goods_list[categoryid],
            candidate_shelf.shelf.goods_arrange_weight)

        level = None
        for goods in arrange_goods_list:
            # 创建层
            level = _level_add_goods(candidate_shelf, level, goods)
            # TODO 什么情况以及如何才能再创建一个副本货架陈列


def _level_add_goods(candidate_shelf,cur_level,goods):
    """
    处理层添加和层的width和height变化
    :param candidate_shelf:
    :param levelid:
    :param goods:
    :return: 商品添加的层
    """

    display_goods = display_data.DisplayGoods(goods)
    if cur_level == None:
        # 初始陈列
        cur_level = display_data.Level(candidate_shelf, 0, candidate_shelf.shelf.bottom_height,True)
    ret_level = cur_level

    # 陈列商品 TODO 需要处理陈列商品跨层拆分
    success = ret_level.display_goods(display_goods)
    if not success:
        # 无法陈列商品
        ret_level = display_data.Level(
            candidate_shelf,
            cur_level.level_id+1,
            cur_level.start_height+cur_level.goods_height+candidate_shelf.shelf.level_buff_height+candidate_shelf.shelf.level_board_height,
            bool(1-cur_level.is_left_right_direction)
        )
        # TODO 需要考虑整层无法摆下的拆分
        ret_level.display_goods(display_goods)

    return ret_level

def _solve_goods_face(shelf_depth, goods_data_list):
    """
    扩面处理
    :param shelf_depth:
    :param goods_data_list:
    :return:
    """
    # TODO
    # TODO 层板深度问题处理怎么解决？
    pass

def _calcuate_shelf_category_area_ratio(shelf, categoryid_list, category_area_ratio):
    """
    计算出本货架的比例
    :param shelf:
    :param categoryid_list:
    :param category_area_ratio:
    :return: 修正的category_area_ratio
    """

    shelf_category_area_ratio = {}
    # TODO
    return shelf_category_area_ratio
