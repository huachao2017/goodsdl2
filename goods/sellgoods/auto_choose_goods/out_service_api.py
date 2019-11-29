

import math
# from goods.goodsdata import *
from goods.sellgoods.auto_choose_goods.selected_goods_sort import *
from goods.sellgoods.auto_display.service_for_display import *
# from goods.sellgoods.commonbean.taizhang import *

def goods_sort(middle_list,shop_id = 1284):
    """
    根据输入的中类列表进行选品的排序，排序时权衡了类别和销售额因素
    :param middle_list:商品中类的列表
    :param shop_id:商店id，默认时普天店
    :return:(mch,销售额)的列表
    """
    goods_to_sort = ShelfGoodsSort(middle_list)
    list = goods_to_sort.main()
    result = []
    for i in list:
        result.append((i[5],i[4]))
    return result

def calculate_goods_info(taizhang):
    """
    计算商品的属性
    比如： 最终陈列量、单品刻度宽度、 faces数, 总刻度等
    :param taizhang:
    :return:
    """
    calculate_goods(taizhang)

def update_mark_goods_array(taizhang,shelf_diff_width):
    """
    计算货架的商品刻度
    :param taizhang: 对象
    :param shelf_diff_width 宽度超出或缺少的，超出为负，缺少为正
    :return:
    """
    update_mark_goods_array_origin(taizhang,shelf_diff_width)

def shelf_gap_choose_goods(taizhang):
    """
    货架的缝隙进行商品填充

    :return:(shelf_id,level_id,good对象)的列表
    """
    result_list = shelf_gap_choose_goods_origin(taizhang)
    return result_list
def shelf_gap_expand_gooods(taizhang):
    """
        对于每层的空隙，进行周边商品增加face来填充
    :param taizhang:
    :return:
    """
    return shelf_gap_expand_gooods_origin(taizhang)



if __name__ == '__main__':
    shelf_gap_expand_gooods('1')
    # a = goods_sort('0502')
    # print(a)

