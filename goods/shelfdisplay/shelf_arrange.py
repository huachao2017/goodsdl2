"""
输入：一个或多个货架二级/三级分类结构
输出：货架三级分类排列候选
根据三级分类亲密度表和三级分类层数分值表计算三级分类布局组合。
算法说明：
排序规则中，亲密度优先
根据得分排序组合，输出多个符合要求的排序组合
"""

def shelf_arrange(shelf, category3_intimate_weight, category3_level_value):
    """

    :param shelf: display_data中的shelf对象
    :param category3_intimate_weight: 亲密度数据
    :param category3_level_value: 层数分值数据
    :return: 候选分类列表，例如[[a,b,c,d],[d,c,b,a]]
    """
    candidate_category_list = []
    # TODO
    return candidate_category_list