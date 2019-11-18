"""
输入：一个或多个货架二级/三级分类结构
输出：货架三级分类排列候选
根据三级分类亲密度表和三级分类层数分值表计算三级分类布局组合。
算法说明：
排序规则中，亲密度优先
根据得分排序组合，输出多个符合要求的排序组合
"""

import itertools,copy,collections
category3_intimate_weight = {'a,b': 10,  'd,e': 10, 'd,e,f': 5, 'd,e,f,g': 3}
category3_level_value = {'b': 0,'a': 0, 'd': 10, 'f': 10}

def shelf_arrange(shelf, category3_intimate_weight, category3_level_value):
    """
    流程：
        先全部无约束的排序
        然后根据亲密度条件筛选
        然后根据上下关系筛选
    :param shelf: display_data中的shelf对象
    :param category3_intimate_weight: 亲密度数据
    :param category3_level_value: 层数分值数据
    :return: 候选分类列表，例如[[a,b,c,d],[d,c,b,a]]
    """
    original_category3_list = ['a','b','c','d','e','f','m']
    category3_arrange_all_list = category3_arrange_all(original_category3_list)   #所有的排列情况
    candidate_category_list_temp = []     # 候选的临时列表
    candidate_category_list = []     # 返回的候选的列表


    intimate_list = []    # 属于这个货架的亲密度的列表
    for group, value in category3_intimate_weight.items():  # 遍历每个亲密度
        belong_part_category3 = belong_part(group, original_category3_list)  # 亲密度中属于这个货架的那几个三级分类
        intimate_list.append(belong_part_category3)   # 列表套列表[[a,b],[d,e,f]]
    # 以下是去重
    intimate_list_temp = []
    for i in intimate_list:
        if i not in intimate_list_temp:
            intimate_list_temp.append(i)
    intimate_list = intimate_list_temp
    # print('intimate_list',intimate_list)

    for category3_arrange in category3_arrange_all_list[:]:    # 遍历每个排列,根据亲密度进行筛选
        number = 0    # 符合亲密关系的组合数
        for group in intimate_list:   # 遍历每个亲密度
            if len(group) > 1:
                for i in range(len(category3_arrange)-len(group)+1):
                    # print(group,category3_arrange[i:i+len(group)])
                    if is_equal(group,category3_arrange[i:i+len(group)]):  # 亲密度的那几个分类是在一块的
                        # 并且满足上下关系
                        # print('is_equal')
                        if is_match_up_down_relation(category3_arrange[i:i+len(group)],category3_level_value):
                            # print('is_match_up_down_relation')
                            number += 1
                            break
            else:
                number += 1
        if number == len(intimate_list):    #说明每个亲密组合都符合
            # print('category3_arrange',category3_arrange)
            candidate_category_list_temp.append(category3_arrange)

    # 查看未定义的是否在0和10之间
    candidate_category_list_temp2 = is_in_center(original_category3_list,candidate_category_list_temp,category3_level_value)
    print('candidate_category_list_temp2',len(candidate_category_list_temp2))
    # 根据上下关系筛选
    max_intimate_group_list = max_intimate_group(intimate_list)
    for group in candidate_category_list_temp2:
        del_list = get_delete_list(group,max_intimate_group_list,category3_level_value)  # 未定义的或者是亲密组合中不考虑的
        new_group = []
        for g in group:
            if not g in del_list:
                new_group.append(g)
        if is_match_up_down_relation(new_group,category3_level_value):
            candidate_category_list.append(group)


    # candidate_category_list = []
    # TODO 顺序是从下往上
    return candidate_category_list

def is_in_center(original_category3_list,candidate_category_list_temp,category3_level_value):
    """
    查看未定义的是否在0分和10分之间
    即可以转化为0和10是否都在两头
    :return:
    """
    min_list = []
    max_list = []
    for k,v in category3_level_value.items():
        if v == 0 and k in original_category3_list:
            min_list.append(k)
        if v == 10 and k in original_category3_list:
            max_list.append(k)
    print('min_list',min_list)
    candidate_category_list_temp2 = []
    for group in candidate_category_list_temp:
        if is_equal(group[:len(min_list)],min_list) and is_equal(group[-len(max_list):],max_list):
            candidate_category_list_temp2.append(group)

    return candidate_category_list_temp2

def is_match_up_down_relation(list,category3_level_value):
    """
    是否符合上下关系
    :param list:
    :param category3_level_value:
    :return:
    """

    tem_list = []
    for i in list:
        # 没考虑没定义的
        if i in category3_level_value:
            v = category3_level_value[i]
            tem_list.append(v)

    for i,v in enumerate(tem_list):
        if i < len(tem_list)-1:
            if tem_list[i] > tem_list[i+1]:
                return False

    return True

def get_delete_list(category_list,max_intimate_group_list,category3_level_value):
    """
        把商品列表中，对排序没有用的商品的列表返回
    :param category_list:示例[a,c,b,e,d]
    :param max_intimate_group_list: 最大的亲密度组合
    :return:即未定义的或者是亲密组合中不考虑的
    """
    temp_list = []   # 一个排列中，多个亲密度组合的列表
    for m in max_intimate_group_list:
        for i,c in enumerate(category_list):
            # flag = 0
            if c in m:
                temp_list.append(category_list[i:i+len(m)])
                break

    del_list = []

    for group in temp_list:
        # score_dict = collections.OrderedDict()
        score_list = []
        for g in group:
            if g in category3_level_value:
                score = category3_level_value[g]
                # score_dict[g] = score
                score_list.append([g,score])

        del_list.extend(group)       # 默认都没有定义上下层分值，所以先都放到删除列表里（未定义的在这不参与排名筛选）
        if score_list:
            if score_list[0][1] > 5:     # 最低的大于5
                del_list.remove(score_list[-1][0])     #按照最高分算，就从删除列表里扣除
            if score_list[-1][1] < 5:     # 最高的小于5
                del_list.remove(score_list[0][0])     #按照最低分算，就从删除列表里扣除

    # 以下,既不在亲密度组合里，又是未定义的
    max_intimate_group_list_one = []
    for m in max_intimate_group_list:
        max_intimate_group_list_one += m   # 变成一维平铺的
    for i, c in enumerate(category_list):
        # flag = 0
        if not c in max_intimate_group_list_one:
            if not c in category3_level_value:
                del_list.append(c)
    return del_list

def max_intimate_group(intimate_list):
    """
    :param intimate_list:
    :return: 最大的那几个亲密度组合，如
    """
    two = []
    max_intimate_group_list = []

    for i in intimate_list:
        if len(i) == 2:
            two.append(i)
    for j in two:
        max = j
        for m in intimate_list:
            if is_son(j,m):
                if len(m) > len(max):
                    max = m
        # if max != j:
        max_intimate_group_list.append(max)  # FIXME 2个的也加进去吗
    return max_intimate_group_list

def is_son(a,b):
    """
    a列表的元素是否都是b列表的子集
    :param a:
    :param b:
    :return:
    """
    for i in a:
        if not i in b:
            return False
    return True

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

def belong_part(a,b):
    """
    返回a字符串中属于b的各元素
    :param a:
    :param b:
    :return:
    """
    result = []
    for i in a:
        if i in b:
            result.append(i)
    return result

def category3_arrange_all(list1):
    """
    :return: 输出无约束情况下所有排列的可能
    """
    # list1 = [1, 2, 3, 4, 5]
    iter = itertools.permutations(list1, len(list1))
    result = list(iter)
    print('所有排列数:',len(result))
    print(result)
    return result

if __name__ == '__main__':
    a = shelf_arrange(1, category3_intimate_weight, category3_level_value)
    print('--------------候选列表---------------')
    print(a)
