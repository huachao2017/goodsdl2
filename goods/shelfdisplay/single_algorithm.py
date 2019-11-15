"""
子算法4.1 选品
子算法4.2 商品排列
子算法4.3 打分规则
"""
from goods.shelfdisplay.db_data import *

def choose_goods_for_category3(categoryid, category_area_ratio, goods_data_list, shelf_data, extra_add=0):
    """
    根据面积比例选该分类下预测销量最大的品
    :param categoryid:
    :param category_area_ratio:
    :param goods_data_list: 商品列表
    :param shelf_data: 货架信息
    :param extra_add: 返回商品数=最佳比例+extra_add，
    :return:商品列表GoodsData
    """
    shelf_area = shelf_data.width * shelf_data.heigth
    ratio = category_area_ratio[categoryid]
    category3_area = shelf_area * ratio
    category3_list = []
    for i in goods_data_list:
        if i.category3 == categoryid:
            category3_list.append(i)
    category3_list.sort(key=lambda x: x.spd, reverse=True)
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



def goods_arrange(goods_list, goods_arrange_weight):
    """
    按四级分类、品牌、规格（包装）顺序分组，
    分组按平均高度排序，组内按先按商品高度排序，再按商品宽度
    1、排序从高到低和从低到高都要输出解
    2、高度差距小于5mm的分组可以交换位置输出解
    3、商品在同一分组中且高度相差5mm且宽度相差5mm内不做交换解输出
    :param goods_list:
    :param goods_arrange_weight:排序权值
    :return: 排序的新的goods_list的列表集:
    """
    max_weight = 0
    max_weight_attribute = None
    for k,weight in goods_arrange_weight.items():
        if weight > max_weight:
            max_weight = weight
            max_weight_attribute = k

    print(max_weight_attribute)

    goods_list.sort(key=lambda x:x.__dict__[max_weight_attribute], reverse=True)


    print(goods_list)
    temp_list = [goods_list[0]]
    goods_list_two = []
    for i in range(0,len(goods_list)-1):
        if goods_list[i].__dict__[max_weight_attribute] == goods_list[i+1].__dict__[max_weight_attribute]:
            temp_list.append(goods_list[i+1])
        else:
            goods_list_two.append(temp_list)
            temp_list = [goods_list[i+1]]
    return 



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
            candidate_shelf.badcase_value += level.get_nono_goods_width()*0.02
            if last_level is not None:
                candidate_shelf.badcase_value += abs(level.height - last_level.height)*0.02
            last_level = level
        if min_badcase_value > candidate_shelf.badcase_value:
            min_badcase_value = candidate_shelf.badcase_value
            best_candidate_shelf = candidate_shelf

    return best_candidate_shelf

if __name__ == '__main__':
    a = GoodsData()
    a.category4 = 1
    c = GoodsData()
    c.category4 = 3
    b = GoodsData()
    b.category4 = 2
    goods_arrange([a, c, b], BaseData.goods_arrange_weight)