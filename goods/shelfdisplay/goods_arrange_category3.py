def goods_arrange(goods_list):
    """
    按四级分类、品牌、规格（包装）顺序分组，
    分组按平均高度排序，组内按先按商品高度排序，再按商品宽度
    1、排序从高到低和从低到高都要输出解
    2、高度差距小于5mm的分组可以交换位置输出解
    3、商品在同一分组中且高度相差5mm且宽度相差5mm内不做交换解输出
    :param goods_list:
    :return: 排序的新的goods_list的列表集:
    """
    max_weight = 0
    max_weight_attribute = None
    for k, weight in goods_arrange_weight.items():
        if weight > max_weight:
            max_weight = weight
            max_weight_attribute = k

    print(max_weight_attribute)

    goods_list.sort(key=lambda x: x.__dict__[max_weight_attribute], reverse=True)

    print(goods_list)
    temp_list = [goods_list[0]]
    goods_list_two = []
    for i in range(0, len(goods_list) - 1):
        if goods_list[i].__dict__[max_weight_attribute] == goods_list[i + 1].__dict__[max_weight_attribute]:
            temp_list.append(goods_list[i + 1])
        else:
            goods_list_two.append(temp_list)
            temp_list = [goods_list[i + 1]]
    return