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
    root_category_tree_list = init_category_tree(category3_intimate_weight, category3_level_value, category3_list)
    # for root_category_tree in root_category_tree_list:
    #     print(root_category_tree)

    # 2，计算level_value
    for category_tree in root_category_tree_list:
        category_tree.calculate_level_value()

    # 3, 输出里层排序
    for category_tree in root_category_tree_list:
        category_tree.calculate_result()

    # 4，外层排序解集
    candidate_category_tree_order = calculate_outer_result(root_category_tree_list,category3_level_value,category3_list)

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
            tem_list.append(obj.category)
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
    返回CategoryTree列表，初始类似的结构：（（a，b），c），（（d，e），f），g）
    a、b	=10
    a、b、c=5
    d、e	=10
    d、e、f=6
    d、e、f、g=5

    :param category3_intimate_weight:
    :param category3_level_value:
    :param category3_list:
    :return:
    """
    sorted_intimate_list = sorted(category3_intimate_weight.items(), key=lambda item: item[1], reverse=True)
    print(sorted_intimate_list)

    all_category_tree_without_parent = []
    all_category_tree_only_parent = []
    tree_id = 1

    for intimate in sorted_intimate_list:
        cat_ids = intimate[0]
        intimate_value = intimate[1]
        category_list = cat_ids.split(',')
        if len(category_list) <= 0:
            print('cat_ids is error:{}'.format(cat_ids))
            continue
        category_to_category_tree = {}
        is_found = False
        all_found = True
        for category in category_list:
            found_category = _find_category(category, all_category_tree_without_parent)
            category_to_category_tree[category] = found_category
            if found_category is not None:
                is_found = True
            if found_category is None:
                all_found = False

        if is_found:
            # 增量创建
            if all_found:
                # 1、parent和parent组合
                id_to_parent_tree = {}
                for category in category_to_category_tree.keys():
                    parent = category_to_category_tree[category].parent
                    id_to_parent_tree[parent.id] = parent
                category_tree_parent = CategoryTree(tree_id, intimate_value)
                tree_id += 1
                category_tree_parent.init_parent(id_to_parent_tree.values())
                all_category_tree_only_parent.append(category_tree_parent)

            else:
                # 查找最小的亲密度值
                min_intimate_value = 1000
                min_intimate_parent_tree = None
                for category in category_to_category_tree.keys():
                    if category_to_category_tree[category] is not None:
                        if category_to_category_tree[category].intimate_value < min_intimate_value:
                            min_intimate_value = category_to_category_tree[category].intimate_value
                            min_intimate_parent_tree = category_to_category_tree[category].parent

                if min_intimate_value == intimate_value:
                    # 2、在一个存在的parent下面创建一个叶子
                    for category in category_to_category_tree.keys():
                        if category_to_category_tree[category] is None:
                            category_tree = CategoryTree(tree_id, intimate_value)
                            tree_id += 1
                            category_tree.init_child_with_parent(category,min_intimate_parent_tree)
                            all_category_tree_without_parent.append(category_tree)
                elif min_intimate_value > intimate_value:
                    # 3、扩层创建，和一个parent同层创建，并组合创建共同的parent
                    category_tree_leaf_list = []
                    category_tree_leaf_list.append(min_intimate_parent_tree)
                    for category in category_to_category_tree.keys():
                        if category_to_category_tree[category] is None:
                            category_tree = CategoryTree(tree_id, intimate_value)
                            tree_id += 1
                            category_tree.init_only_child(category)
                            category_tree_leaf_list.append(category_tree)
                            all_category_tree_without_parent.append(category_tree)
                    category_tree_parent = CategoryTree(tree_id, intimate_value)
                    tree_id += 1
                    category_tree_parent.init_parent(category_tree_leaf_list)
                    all_category_tree_only_parent.append(category_tree_parent)
        else:
            # 4、全新创建
            category_tree_leaf_list = []
            for category in category_list:
                category_tree = CategoryTree(tree_id, intimate_value)
                tree_id += 1
                category_tree.init_only_child(category)
                category_tree_leaf_list.append(category_tree)
                all_category_tree_without_parent.append(category_tree)
            category_tree_parent = CategoryTree(tree_id, intimate_value)
            tree_id += 1
            category_tree_parent.init_parent(category_tree_leaf_list)
            all_category_tree_only_parent.append(category_tree_parent)

    id_to_root_parent_tree = {}
    for parent_tree in all_category_tree_only_parent:
        if parent_tree.parent == None:
            id_to_root_parent_tree[parent_tree.id] = parent_tree

    return id_to_root_parent_tree.values()


def _find_category(category, category_tree_list):
    for category_tree in category_tree_list:
        ret = category_tree.find(category)
        if ret is not None:
            return ret

    return None


class CategoryTree:
    id = None
    children = None
    parent = None
    intimate_value = None
    level_value = None
    category = None
    result_list = None  # 这里面是对象解：[[Child1,Child2,Child3],[Child2,Child3,Child1]]

    def __init__(self, id, intimate_value):
        self.id = id
        self.intimate_value = intimate_value

    def init_only_child(self, category):
        # 初始叶子对象
        self.category = category

    def init_child_with_parent(self, category, parent):
        # 后续叶子对象
        self.category = category
        self.parent = parent
        parent.children.append(self)

    def init_parent(self, category_tree_children):
        # 组合节点
        self.children = []
        for category_tree in category_tree_children:
            self.children.append(category_tree)
            category_tree.parent = self

    def find(self, category):
        if self.children is None:
            if self.category == category:
                return self
        else:
            for child in self.children:
                ret = child.find(category)
                if ret is not None:
                    return ret

        return None

    def calculate_level_value(self):
        pass

    def calculate_result(self):
        pass

    def __str__(self):
        ret = ''
        if self.children is None:
            return self.category + ','
        else:
            ret += '('
            for child in self.children:
                ret += str(child)
            ret += '),'
        return ret


if __name__ == '__main__':
    # TODO 李树
    category3_intimate_weight = {
        'a,b': 10,
        'a,b,c': 5,
        'd,e': 10,
        'd,e,f': 6,
        'd,e,f,g': 5
    }
    category3_level_value = {}
    category3_list = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
    a = main_calculate(category3_intimate_weight, category3_level_value, category3_list)
    print('--------------候选列表---------------')
    print(a)
