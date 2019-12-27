"""
子算法4.1 选品
子算法4.3 打分规则
"""

def choose_goods_for_category3(shelf, categoryid, extra_add=0):
    """
    根据面积比例选该分类下预测销量最大的品
    :param categoryid:
    :param shelf: 货架信息
    :param extra_add: 返回商品数=最佳比例+extra_add，
    :return:商品列表GoodsData
    """
    shelf_area = shelf.width * shelf.height
    ratio = shelf.shelf_category3_area_ratio[categoryid]
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
    同三级分类相邻品高度差	0.02*∑ ，在陈列摆放中直接计算
    同层板相邻品高度差	0.2*∑  ，在陈列摆放中直接计算
    空缺层板宽度	0.02*∑
    各层板的高度差	0.02*∑
    顶部高度剩余 0.2*∑
    :param candidate_shelf_list:
    :return: 分数最低的shelf
    """

    min_badcase_value = 100000
    best_candidate_shelf = None
    i = 0
    step = max(1, int(len(candidate_shelf_list) / 10))
    for candidate_shelf in candidate_shelf_list:
        i += 1
        # 空缺层板宽度
        # 各层板的高度差
        last_level = None
        for level in candidate_shelf.levels:
            candidate_shelf.badcase_value += level.get_nono_goods_width() * 0.02
            if last_level is not None:
                candidate_shelf.badcase_value += abs(level.goods_height - last_level.goods_height) * 0.02
            last_level = level
        # 顶部高度剩余
        candidate_shelf.badcase_value += (candidate_shelf.shelf.height - last_level.start_height + last_level.goods_height) * 0.04
        if i % step == 0:
            print('计算第{}个候选解,共{}层,value={}：'.format(i,len(candidate_shelf.levels),candidate_shelf.badcase_value))
        if candidate_shelf.badcase_value < min_badcase_value:
            min_badcase_value = candidate_shelf.badcase_value
            best_candidate_shelf = candidate_shelf
    print(min_badcase_value)

    return best_candidate_shelf
