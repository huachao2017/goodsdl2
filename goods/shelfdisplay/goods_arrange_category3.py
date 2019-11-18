"""
1、按四级分类、品牌、规格（包装）顺序分组，
2、分组按平均高度排序，组内按先按商品高度排序，排序从高到低和从低到高都要输出解
3、可交换规则：
3.1、高度差距小于10mm的分组可以交换位置输出解
3.2、商品在同一分组中且高度差小于10mm并且宽度差大于10mm可交换解输出（此条暂不做）
"""

def goods_arrange(goods_list):
    """
    按四级分类、品牌、规格（包装）顺序分组，
    分组按平均高度排序，组内按先按商品高度排序，再按商品宽度
    1、排序从高到低和从低到高都要输出解
    2、高度差距小于10mm的分组可以交换位置输出解
    3、商品在同一分组中且高度相差5mm且宽度相差5mm内不做交换解输出

    :param goods_list:
    :return: 排序的新的goods_list的列表集:
    """

    # 1，初始化

    # 2，排序，调换

    # 3，生成解列表



class CategoryTree:
    children = []
    parent = None
    height = None
    width = None
    category = None
    result_list = None # 这里面是对象解：[[Child1,Child2,Child3],[Child2,Child3,Child1]]

    def __init__(self):
        pass

    def calculate_height_value(self):
        pass

    def calculate_result(self):
        pass

    def __str__(self):
        return self.category

if __name__ == '__main__':
    # TODO
    goods_list = []
    a = goods_arrange(goods_list)
    print('--------------候选列表---------------')
    print(a)
