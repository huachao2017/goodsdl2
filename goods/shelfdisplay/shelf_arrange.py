"""
算法说明：
排序规则中，亲密度优先
根据得分排序组合，输出多个符合要求的排序组合
组合内的层数分值说明：假设组合（a，b，c）
a，b，c如分值都大于5，则以最大的计算
a，b，c如分值都小于5，则以最小的计算
a，b，c如分值既有大于5又有小于5，则为N（未定义）
"""
import itertools,copy
def shelf_arrange(shelf):
    """
    流程：
        先全部无约束的排序
        然后根据亲密度条件筛选
        然后根据上下关系筛选
    :param shelf: display_data中的shelf对象
    :return: 候选分类列表，例如[[a,b,c,d],[d,c,b,a]]
    """
    category3_intimate_weight = shelf.category3_intimate_weight
    category3_level_value = shelf.category3_level_value

    original_category3_list = shelf.shelf_category_list
    return main_calculate(category3_intimate_weight, category3_level_value, category3_list)

def main_calculate(category3_intimate_weight, category3_level_value, category3_list):
    """
    根据亲密度，层数分计算
    :param category3_intimate_weight: 亲密度
    :param category3_level_value: 层数分
    :param category3_list: 分类列表
    :return: 总体后选列表
    """

    # 1，初始化数据
    category_tree_list = init_category_tree(category3_intimate_weight, category3_level_value, category3_list)

    # 2，计算level_value
    for category_tree in category_tree_list:
        category_tree.calculate_level_value()

    # 3, 输出里层排序
    for category_tree in category_tree_list:
        category_tree.calculate_result()

    # 4，外层排序解集
    candidate_category_tree_order = calculate_outer_result(category_tree_list,category3_level_value)

    # 5, 里外合并
    ret = combine_all_result(candidate_category_tree_order)

    return ret

def calculate_outer_result(category_tree_list,category3_level_value,category3_list):
    """
    计算外层解
    :param category_tree_list:
    :return: candidate_category_tree_order
    """
    ret = []  # 最终返回
    iter = itertools.permutations(category_tree_list, len(category_tree_list))
    all_arrange = list(iter)
    print('所有排列数:', len(all_arrange))
    # print(result)
    all_arrange_2 = copy.deepcopy(all_arrange)
    for arrange in all_arrange:
        for obj in arrange:
            #是否符合上下关系
            tem_list = []
            if obj.level_value:
                # 这步考虑没定义的
                tem_list.append(obj.level_value)
            for i, v in enumerate(tem_list):
                if i < len(tem_list) - 1:
                    if tem_list[i] > tem_list[i + 1]:
                        all_arrange_2.remove(arrange)

    #查看未定义的是否在0分和10分之间,即可以转化为0和10是否都在两头
    min_list = []
    max_list = []
    for k, v in category3_level_value.items():
        if v == 0 and k in category3_list:
            min_list.append(k)
        if v == 10 and k in category3_list:
            max_list.append(k)
    print('min_list', min_list)
    for arrange in all_arrange_2:
        tem_list = []
        for obj in arrange:
            tem_list.append(obj.category3)
        if is_equal(tem_list[:len(min_list)], min_list) and is_equal(tem_list[-len(max_list):], max_list):
            ret.append(arrange)

    # TODO @李树

    return ret

def is_equal(a,b):
    """
    检查a、b是否元素相等，只是排列组合不同而已
    :param a:
    :param b:
    :return:
    """
    if len(a) != len(b):
        return False
    for i in a:
        if not i in b:
            return False
    return True

def combine_all_result(candidate_category_tree_order):
    """
    遍历并组合所有内部解和外部解，并把对象转为category
    :param candidate_category_tree_order:
    :return:
    """
    ret = []
    for obj_arrange in candidate_category_tree_order:
        temp_list = []
        lengh = len(obj_arrange)
        for obj in obj_arrange:
            lengh = len(obj.result_list)
            for result in obj.result_list:
                temp_list.append(obj.result_list)



    # TODO @李树

    return ret

def init_category_tree(category3_intimate_weight, category3_level_value, category3_list):
    """
    返回CategoryTree列表
    :param category3_intimate_weight:
    :param category3_level_value:
    :param category3_list:
    :return:
    """
    ret = []
    # TODO

    return ret

class CategoryTree:
    children = []
    parent = None
    level_value = None
    category = None
    result_list = None # 这里面是对象解：[[Child1,Child2,Child3],[Child2,Child3,Child1]]

    def __init__(self):
        pass

    def calculate_level_value(self):
        pass

    def calculate_result(self):
        pass

    def __str__(self):
        return self.category

if __name__ == '__main__':
    # TODO 李树
    category3_intimate_weight = {}
    category3_level_value = {}
    category3_list = {'a','b'}
    a = main_calculate(category3_intimate_weight,category3_level_value,category3_list)
    print('--------------候选列表---------------')
    print(a)
