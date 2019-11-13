"""
子算法4.1 选品
子算法4.2 商品排列
子算法4.3 打分规则
"""

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
        area = goods.width * goods.height * goods.faces_num
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
    按四级分类、品牌、规格（包装）、尺寸（只选宽和高）排序
    特征权重
    按特征权重高低排列
    :param goods_list:
    :param goods_arrange_weight:排序权值
    :return: goods_list:
    """
    max_weight = 0
    max_weight_attribute = None
    for k,weight in goods_arrange_weight.items():
        if weight > max_weight:
            max_weight = weight
            max_weight_attribute = k
    goods_list.sort(key=lambda x: x.spd, reverse=True)





def goods_badcase_score(shelf_list):
    """
    扩面跨层	1*∑
    spu跨层	0.3*∑
    同三级分类相邻品高度差	0.2*∑
    同层板相邻品高度差	0.02*∑
    空缺层板宽度	0.02*∑
    各层板的高度差	0.02*∑
    :param shelf_list:
    :return: 分数最低的shelf
    """
    pass