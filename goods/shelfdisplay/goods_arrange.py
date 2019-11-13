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

def goods_arrange(shelf, candidate_category_list, goods_data_list, category_area_ratio, goods_arrange_weight):
    """

    :param shelf:货架
    :param candidate_category_list: 货架三级分类排列候选
    :param goods_data_list: 候选商品
    :param category_area_ratio: 面积比例
    :param goods_arrange_weight: 商品排列权重
    :return:
    """

    # TODO
    return True