"""
子算法4.1 选品
子算法4.3 打分规则
"""

def choose_goods_for_category3(categoryid, shelf, extra_add=0):
    """
    根据面积比例选该分类下预测销量最大的品
    :param categoryid:
    :param shelf: 货架信息
    :param extra_add: 返回商品数=最佳比例+extra_add，
    :return:商品列表GoodsData
    """
    shelf_area = shelf.width * shelf.heigth
    ratio = shelf.shelf_category_area_ratio[categoryid]
    category3_area = shelf_area * ratio
    category3_list = []
    for i in shelf.shelf_goods_data_list:
        if i.category3 == categoryid:
            category3_list.append(i)
    category3_list.sort(key=lambda x: x.psd, reverse=True)
    mark = 0
    goods_results = []
    for goods in category3_list:
        area = goods.width * goods.height * goods.face_num
        mark += area
        if mark > category3_area:
            if extra_add == 0:
                break
            else:
                extra_add -= 1
        goods_results.append(goods)
    return goods_results


def goods_badcase_score(candidate_shelf_list):
    """
    扩面跨层	1*∑，在陈列摆放中直接计算
    spu跨层	0.3*∑，在陈列摆放中直接计算
    同三级分类相邻品高度差	0.2*∑ ，在陈列摆放中直接计算
    同层板相邻品高度差	0.02*∑  ，在陈列摆放中直接计算
    空缺层板宽度	0.02*∑
    各层板的高度差	0.02*∑
    :param candidate_shelf_list:
    :return: 分数最低的shelf
    """

    min_badcase_value = 100000
    best_candidate_shelf = None
    for candidate_shelf in candidate_shelf_list:
        # 空缺层板宽度
        # 各层板的高度差
        last_level = None
        for level in candidate_shelf.levels:
            candidate_shelf.badcase_value += level.get_nono_goods_width() * 0.02
            if last_level is not None:
                candidate_shelf.badcase_value += abs(level.height - last_level.height) * 0.02
            last_level = level
        if min_badcase_value > candidate_shelf.badcase_value:
            min_badcase_value = candidate_shelf.badcase_value
            best_candidate_shelf = candidate_shelf

    return best_candidate_shelf


def calculate_shelf_category_area_ratio(categoryid_list, category_area_ratio):
    """
    计算出本货架的比例
    :param shelf:
    :param categoryid_list:
    :param category_area_ratio:
    :return: 修正的category_area_ratio
    """

    shelf_category_area_ratio = {}
    total_ratio = 0.0
    for categoryid in categoryid_list:
        total_ratio += category_area_ratio[categoryid]
    for categoryid in categoryid_list:
        shelf_category_area_ratio[categoryid] = category_area_ratio[categoryid] / total_ratio

    return shelf_category_area_ratio



