"""
1、按四级分类、品牌、规格（包装）顺序分组，
2、分组按平均高度排序，组内按先按商品高度排序，排序从高到低和从低到高都要输出解
3、可交换规则：
3.1、高度差距小于10mm的分组可以交换位置输出解
3.2、商品在同一分组中且高度差小于10mm并且宽度差大于10mm可交换解输出（此条暂不做）
"""
import math
from goods.shelfdisplay import single_algorithm

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
    root_goods_tree = init_goods_tree(goods_list)

    # 2，排序，调换
    # 只做从低到高的，生成解的时候都有一个从高到低的解
    root_goods_tree.sort_height()
    root_goods_tree.calculate_result()
    print(root_goods_tree)

    # 3，生成解列表
    ret = root_goods_tree.get_all_simple_result()
    # TODO 需要生成所有从高到低的解
    return ret


def init_goods_tree(goods_list):
    """
    先四级分类，后包装，后品牌
    返回CategoryTree列表，初始类似的结构：（（a，b），c），（（d，e），f），g）

    :param goods_list:
    :return:
    """

    # 初始化树结构
    root_goods_tree = GoodsTree(0, name='root')
    for goods in goods_list:
        cur_parent_tree = root_goods_tree
        if goods.category4 is not None:
            cur_parent_tree = cur_parent_tree.create_child_node(1,goods.category4)

        if goods.package_type is not None:
            cur_parent_tree = cur_parent_tree.create_child_node(2,goods.package_type)

        if goods.brand is not None:
            cur_parent_tree = cur_parent_tree.create_child_node(3,goods.brand)

        cur_parent_tree.create_child_goods(goods)

    # 自动剪枝node（如果node下只有一个child）
    root_goods_tree.prune()
    root_goods_tree.prune()
    root_goods_tree.prune()

    # 计算node的height
    root_goods_tree.calculate_height_value()

    return root_goods_tree

class GoodsTree:
    children = None
    type = None # 0:root; 1:category4; 2:package_type; 3:brand; 4:goods
    parent = None
    height = None
    width = None
    name = None
    goods = None
    result_list = None # 这里面是对象解：[[Child1,Child2,Child3],[Child2,Child3,Child1]]
    one_goods_combination_threshhold = 10 # 一个商品组合阈值
    all_goods_combination_threshhold = 100 # 所有商品组合的阈值

    def __init__(self, type, parent=None, goods = None, name = None):
        self.type = type
        self.parent = parent
        self.name = name
        if goods is None:
            self.children = []
        else:
            self.goods = goods
            self.name = goods.goods_name
            self.height = goods.height
            self.width = goods.width

        if self.parent is not None:
            self.parent.children.append(self)

    def create_child_node(self, name, type):
        ret = self.find_in_children(name, type)
        if ret is None:
            ret = GoodsTree(type, parent=self, name=name)
        return ret

    def create_child_goods(self, goods):
        return GoodsTree(4, parent=self, goods=goods)

    def prune(self):
        if self.children is not None:
            if len(self.children) == 1:
                if self.children[0].type == 4:
                    if self.parent is None:
                        return
                    self.parent.children.remove(self)
                    self.parent.children.append(self.children[0])
                else:
                    self.children[0].prune()
            else:
                for child in self.children:
                    child.prune()

    def find_in_children(self, name, type):
        if self.children is None:
            return None
        for child in self.children:
            if child.name == name and child.type == type:
                return child
        return None


    def calculate_height_value(self):
        height = 0
        width = 0
        if self.children is not None:
            for child in self.children:
                if child.children is not None:
                    h, w = child.calculate_height_value()
                    height += h
                    width += w
                if child.type == 4:
                    height += child.height
                    width += child.width

            self.height = int(height/len(self.children))
            self.width = width
        return self.height, self.width

    def sort_height(self):
        if self.children is not None:
            for child in self.children:
                if child.children is not None:
                    child.sort_height()
            self.children.sort(key=lambda x:x.height)

    def calculate_result(self):
        """
        仅按从低到高做解
        高度差小于10mm并且宽度差大于10mm可交换解输出
        :return:
        """
        if self.children is not None:
            for child in self.children:
                if child.children is not None:
                    child.calculate_result()
            self.result_list = [self.children.copy()]

            i = -1
            j = -1
            for child in self.children:
                i += 1
                if i == 0:
                    continue
                if abs(self.children[i-1].height-child.height) < 10 and abs(self.children[i-1].width - child.width) > 10:
                    # FIXME 放大宽加大
                    # FIXME 仅做近邻交换的解
                    another_result = self.children.copy()
                    another_result[i-1], another_result[i] = another_result[i] , another_result[i-1]
                    j += 1
                    if j > self.one_goods_combination_threshhold:
                        break
                    self.result_list.append(another_result)

    def get_all_simple_result(self):
        if self.children is not None:
            all_simple_result = []
            if self.parent is None:
                j = -1
            for result in self.result_list:
                index = 0
                index_to_simple_result_list = {}
                for one_tree in result:
                    if one_tree.children is not None:
                        child_all_simple_result = one_tree.get_all_simple_result()
                        index_to_simple_result_list[index] = child_all_simple_result
                        index += 1
                    else:
                        index_to_simple_result_list[index] = [one_tree.goods]
                        index += 1
                list_index_to_simple_result = single_algorithm.dict_arrange(index_to_simple_result_list)
                if self.parent is None:
                    max_length = len(list_index_to_simple_result)
                    if max_length > self.all_goods_combination_threshhold:  # 如果大于阈值，则根据步长设置进行下采样
                        step_size = math.ceil(max_length / self.all_goods_combination_threshhold)
                    else:
                        step_size = 1
                    print(max_length)
                    print(step_size)
                for index_to_simple_result in list_index_to_simple_result:
                    if self.parent is None:
                        j += 1
                    if self.parent is not None or j % step_size == 0:  # 进行下采样
                        simple_result_list = []
                        for i in range(index):
                            if type(index_to_simple_result[i]) is list:
                                for one_simple in index_to_simple_result[i]:
                                    simple_result_list.append(one_simple)
                            else:
                                simple_result_list.append(index_to_simple_result[i])
                        all_simple_result.append(simple_result_list)
            return all_simple_result

    def __str__(self):
        ret = ''
        if self.children is None:
            return str(self.name) + '-' + str(self.height) + ',' + str(self.width) + ','
        else:
            ret += str(self.type)
            ret += '-'
            ret += str(self.name)
            ret += '-'
            ret += str(self.height)
            ret += '-'
            ret += str(self.width)
            ret += '-'
            ret += str(len(self.result_list))
            ret += ':('
            for child in self.children:
                ret += str(child)
            ret += '),'
            if self.parent is None:
                simple_results = self.get_all_simple_result()
                ret += str(len(simple_results))
                ret += '-'
                ret += '['
                for result in simple_results:
                    ret += '['
                    for goods in result:
                        ret += str(goods.goods_name)
                        ret += ','
                    ret += ']'
                ret += ']'
        return ret

class TestGoods:
    category4 = None
    package_type = None
    brand = None
    goods_name = None
    height = None
    width = None

    def __init__(self, category4, package_type, brand, goods_name, height, width):
        self.category4 = category4
        self.package_type = package_type
        self.brand = brand
        self.goods_name = goods_name
        self.height = height
        self.width = width

    def __str__(self):
        ret = '('
        ret += str(self.category4)
        ret += ','
        ret += str(self.package_type)
        ret += ','
        ret += str(self.brand)
        ret += ','
        ret += str(self.goods_name)
        ret += ','
        ret += str(self.height)
        ret += ','
        ret += str(self.width)
        ret += ')'
        return ret

if __name__ == '__main__':
    goods_list = []
    goods_list.append(TestGoods('特高', '瓶装', '可口可乐', '可乐500ml', 300, 50))
    goods_list.append(TestGoods(None, '瓶装', '可口可乐', '雪碧500ml', 270, 50))
    goods_list.append(TestGoods(None, '杯装', '可口可乐', '橙汁', 270, 50))
    goods_list.append(TestGoods(None, '瓶装', '农夫山泉', '矿泉水500ml', 270, 50))
    goods_list.append(TestGoods(None, '瓶装', None, '冰红茶', 260, 50))
    goods_list.append(TestGoods(None, '杯装', '农夫山泉', '东方树叶', 250, 50))
    goods_list.append(TestGoods(None, '瓶装', '农夫山泉', '茶Π', 250, 50))
    for goods in goods_list:
        print(goods)
    a = goods_arrange(goods_list)
    print('--------------候选列表---------------')
    print(a)

