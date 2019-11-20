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
import goods.shelfdisplay.goods_arrange_category3
from goods.shelfdisplay import display_data
from goods.shelfdisplay import single_algorithm
import math

def goods_arrange(shelf):
    """
    第四步，商品布局主体函数
    :param shelf:货架
    :return:
    """

    # 一、准备工作
    # 1、计算扩面
    _solve_goods_face(shelf.depth, shelf.shelf_goods_data_list)
    # 2、计算spu
    # 3、每一个三级分类获得排序商品
    extra_add_num = 2  # FIXME 冗余数量怎么定，如果没有了呢？
    categoryid_to_sorted_goods_list = {}

    for categoryid in shelf.shelf_category3_list:
        sorted_goods_list = single_algorithm.choose_goods_for_category3(shelf,categoryid,
                                                                        extra_add=extra_add_num)
        categoryid_to_sorted_goods_list[categoryid] = sorted_goods_list

        # print('排序商品列表：{},{}'.format(categoryid,len(sorted_goods_list)))

    # input("输任意键继续")

    # 设定shelf的全局计算参数
    shelf.categoryid_to_sorted_goods_list = categoryid_to_sorted_goods_list
    shelf.extra_add_num = extra_add_num
    # 生成所有的候选解
    candidate_result_shelf_list = []
    categoryid_to_arrange_goods_list_list = {}
    for categoryid in shelf.shelf_category3_list:
        arrange_goods_list_list = goods.shelfdisplay.goods_arrange_category3.goods_arrange(
            shelf.categoryid_to_sorted_goods_list[categoryid])
        categoryid_to_arrange_goods_list_list[categoryid] = arrange_goods_list_list

    print("共{}个分类解：".format(len(shelf.candidate_category_list)))
    # input("按任何键继续：")
    i = 0
    for categoryid_list in shelf.candidate_category_list:
        i += 1
        candidate_shelf_list = create_candidate_shelf_list(
            shelf,
            categoryid_list,
            categoryid_to_arrange_goods_list_list)
        print("开始第{}个分类解（共{}个商品解）：".format(i,len(candidate_shelf_list)))
        j = 0
        for candidate_shelf in candidate_shelf_list:
            j += 1
            # print("开始第{}.{}个商品组合解：".format(i, j))
            if _display_shelf(candidate_shelf):
                candidate_result_shelf_list.append(candidate_shelf)

    # 计算候选解的badcase得分
    print('共找到{}个候选解'.format(len(candidate_result_shelf_list)))
    if len(candidate_result_shelf_list) == 0:
        return False
    best_candidate_shelf = single_algorithm.goods_badcase_score(candidate_result_shelf_list)

    shelf.best_candidate_shelf = best_candidate_shelf

    return True


def create_candidate_shelf_list(shelf, categoryid_list, categoryid_to_arrange_goods_list_list):
    """
    排列组合所有商品排序不同的候选货架列表
    :param shelf:
    :param categoryid_list:
    :param categoryid_to_arrange_goods_list_list:
    :return: candidate_shelf_list
    """

    candidate_shelf_list = []
    list_categoryid_to_arrange_goods_list = single_algorithm.dict_arrange(categoryid_to_arrange_goods_list_list)
    for categoryid_to_arrange_goods_list in list_categoryid_to_arrange_goods_list:
        candidate_shelf = display_data.CandidateShelf(shelf, categoryid_list, categoryid_to_arrange_goods_list)
        candidate_shelf_list.append(candidate_shelf)

    return candidate_shelf_list


def _display_shelf(candidate_shelf):
    """
    陈列主算法
    :param candidate_shelf: 候选货架
    :return: True or False
    """
    addition_width = None
    for i in range(4):  # 试错4次
        candidate_shelf.recalculate()
        _try_display_shelf(candidate_shelf)
        # 计算货架多余或缺失宽度
        addition_width = candidate_shelf.calculate_addition_width()

        if addition_width > 0:
            print('{},{}'.format(i,addition_width))
            input("按任意键继续：")
            # 陈列越界
            if addition_width < candidate_shelf.goods_mean_width * 2:  # FIXME 阈值多少合适？
                # 舍弃最后一层，并退出试错
                candidate_shelf.levels = candidate_shelf.levels[:-1]
                return True

            # 减少候选品
            reduce_width = 0
            for j in range(3):  # 每个品最多减三轮
                for categoryid in candidate_shelf.categoryid_to_used_sorted_goods_list.keys():
                    if len(candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid]) > 2:
                        # 数量太少的不减
                        goods = candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid][-1]
                        reduce_width += goods.width * goods.face_num
                        candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid] = \
                        candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid][:-1]
                        candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid].insert(0, goods)
                        if reduce_width > addition_width:
                            break

                if reduce_width > addition_width:
                    break
        else:
            # print('{},{}'.format(i,addition_width))
            # input("按任意键继续：")
            positive_addition_width = -addition_width
            if positive_addition_width < candidate_shelf.goods_mean_width * 2:  # FIXME 阈值多少合适？
                # 退出试错
                return True

            # 增加候选品
            add_width = 0
            for j in range(2):  # 每个品最多加两轮
                for categoryid in candidate_shelf.categoryid_to_used_sorted_goods_list.keys():
                    if len(candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid]) > 0:  # 防止没有候选商品
                        goods = candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid][0]
                        add_width += goods.width * goods.face_num
                        candidate_shelf.categoryid_to_used_sorted_goods_list[categoryid].append(goods)
                        candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid] = candidate_shelf.categoryid_to_candidate_sorted_goods_list[categoryid][1:]
                        if add_width > positive_addition_width:
                            break
                    if add_width > positive_addition_width:
                        break

    if abs(addition_width) < candidate_shelf.shelf.width/5:
        # 剩余1/5货架宽内就是正确解
        if addition_width > 0:
            # 舍弃最后一层，并退出试错
            candidate_shelf.levels = candidate_shelf.levels[:-1]
        return True
    else:
        return False


def _try_display_shelf(candidate_shelf):
    level = None
    last_goods = None
    # total_num = 0
    for categoryid in candidate_shelf.categoryid_list:
        arrange_goods_list = candidate_shelf.get_real_arrange_goods_list(categoryid)
        # total_num += len(arrange_goods_list)
        for goods in arrange_goods_list:
            # 创建层
            level = _level_add_goods(candidate_shelf, level, goods, last_goods)
            last_goods = goods

    # print(total_num)

def _level_add_goods(candidate_shelf, input_level, goods, last_goods):
    """
    处理层添加和层的width和height变化
    :param candidate_shelf:
    :param input_level:
    :param goods:
    :param last_goods: 上一个goods
    :return: 商品添加的层
    """

    cur_level = input_level
    display_goods = display_data.DisplayGoods(goods)
    if cur_level is None:
        # 初始陈列
        cur_level = display_data.Level(candidate_shelf, 0, candidate_shelf.shelf.bottom_height, True)

    # 陈列商品 FIXME 需要处理陈列同商品跨层拆分
    success = cur_level.display_goods(display_goods)

    if not success:
        # FIXME 需要考虑整层无法摆下的拆分
        if cur_level != input_level:
            print('无法成列商品，商品在一层无法摆下！')
            raise ValueError('无法成列商品，商品在一层无法摆下！')
        # 无法陈列商品
        cur_level = display_data.Level(
            candidate_shelf,
            cur_level.level_id + 1,
            cur_level.start_height + cur_level.goods_height + candidate_shelf.shelf.level_buff_height + candidate_shelf.shelf.level_board_height,
            bool(1 - cur_level.is_left_right_direction)
        )
        cur_level.display_goods(display_goods)
        if goods.is_spu(last_goods):
            candidate_shelf.badcase_value += 0.3  # 计算spu badcase
    else:
        candidate_shelf.badcase_value += goods.height_diff(last_goods) * 0.02  # 计算同层板相邻品高度差 badcase
        if last_goods is not None and goods.category3 == last_goods.category3:
            candidate_shelf.badcase_value += goods.height_diff(last_goods) * 0.2  # 计算同三级分类相邻品高度差 badcase

    return cur_level


def _solve_goods_face(shelf_depth, goods_data_list):
    """
    扩面处理 n*psd/最大成列量（初始n默认为3）
    :param shelf_depth:
    :param goods_data_list:
    :return:
    """
    # FIXME 层板深度问题处理怎么解决？
    # TODO 需要考虑叠放
    # FIXME 这个计算需要放到摆放时现算

    total_width = 0
    total_face_num = 0
    for goods in goods_data_list:
        max_one_face = int(shelf_depth / goods.depth)
        goods.face_num = math.ceil(3 * goods.psd / max_one_face)
        total_width += goods.width * goods.face_num
        total_face_num += goods.face_num

    # print("total_num,totol_width,total_face_num:{},{},{}".format(len(goods_data_list),total_width,total_face_num))
    # input("按任意键继续：")



