"""
子算法4.1 选品
子算法4.2 商品排列
子算法4.3 打分规则
"""

def choose_goods_for_3category(categoryid, category_area_ratio, extra_add=0):
    """
    根据面积比例选该分类下预测销量最大的品
    :param categoryid:
    :param category_area_ratio:
    :param extra_add: 返回商品数=最佳比例+extra_add，
    :return:商品列表GoodsData
    """
    pass

def goods_arrange(goods_list, goods_arrange_weight):
    """
    按四级分类、品牌、规格（包装）、尺寸（只选宽和高）排序
    特征权重
    按特征权重高低排列
    :param goods_list:
    :param goods_arrange_weight:排序权值
    :return: goods_list:
    """
    pass

def goods_badcase_score(shelf_list):
    """
    扩面跨层	1*∑
    spu跨层	0.3*∑
    同三级分类相邻品高度差	0.2*∑
    同层板相邻品高度差	0.02*∑
    空缺层板宽度	0.02*∑
    各层板的高度差	0.02*∑
    :param shelf_list:
    :return: True or False
    """
    pass