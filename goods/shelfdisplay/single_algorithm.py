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
    同三级分类相邻品高度差	0.2*∑ ，在陈列摆放中直接计算
    同层板相邻品高度差	0.02*∑  ，在陈列摆放中直接计算
    空缺层板宽度	0.02*∑
    各层板的高度差	0.02*∑
    :param candidate_shelf_list:
    :return: 分数最低的shelf
    """

    min_badcase_value = 100000
    best_candidate_shelf = None
    i = 0
    for candidate_shelf in candidate_shelf_list:
        i += 1
        if i % 10 == 0:
            print('计算第{}个候选解：'.format(i))
        # 空缺层板宽度
        # 各层板的高度差
        last_level = None
        for level in candidate_shelf.levels:
            candidate_shelf.badcase_value += level.get_nono_goods_width() * 0.02
            if last_level is not None:
                candidate_shelf.badcase_value += abs(level.goods_height - last_level.goods_height) * 0.02
            last_level = level
        if min_badcase_value > candidate_shelf.badcase_value:
            min_badcase_value = candidate_shelf.badcase_value
            best_candidate_shelf = candidate_shelf

    return best_candidate_shelf


def calculate_shelf_category3_area_ratio(categoryid_list, category_area_ratio):
    """
    计算出本货架的比例
    :param shelf:
    :param categoryid_list:
    :param category_area_ratio:
    :return: 修正的category_area_ratio
    """

    shelf_category3_area_ratio = {}
    total_ratio = 0.0
    ratio_valid = True #
    for categoryid in categoryid_list:
        if categoryid not in category_area_ratio:
            ratio_valid = False
            print('error: category_area_ratio data is not valid!')
            break
        total_ratio += category_area_ratio[categoryid]

    if ratio_valid:
        for categoryid in categoryid_list:
            shelf_category3_area_ratio[categoryid] = category_area_ratio[categoryid] / total_ratio
    else:
        # FIXME 如果分类面积比例是无效的，则每个类平均分配货架
        for categoryid in categoryid_list:
            shelf_category3_area_ratio[categoryid] = 1 / len(categoryid_list)


    return shelf_category3_area_ratio


def dict_arrange(key_to_candidate_list):
    """

    :param key_to_candidate_list:
    :return: list_key_to_candidate
    """

    ret = []
    data_len = []
    index1 = []
    index2 = {}
    for i in key_to_candidate_list.keys():
        data_len.append(len(key_to_candidate_list[i]))
        index1.append(i)
        index2[i] = 0
    while True:
        key_to_candidate = {}
        for i in range(len(index1)):
            key_to_candidate[index1[i]] = key_to_candidate_list[index1[i]][
                index2[index1[i]]]

        ret.append(key_to_candidate)

        total0 = 0
        for i in range(len(index1)):
            cur = len(index1) - i - 1
            if index2[index1[cur]] < data_len[cur] - 1:
                index2[index1[cur]] += 1
                break
            else:
                index2[index1[cur]] = 0
                total0 += 1

        if total0 == len(index1):
            break

    return ret

if __name__ == "__main__":
    a = {0: [1, 2, 3, 4], 1: [5, 6, 7, 8], 2: [9, 10, 11]}
    list_key_to_candidate = dict_arrange(a)
    print(len(list_key_to_candidate))
    for key_to_candidate in list_key_to_candidate:
        print(key_to_candidate)
