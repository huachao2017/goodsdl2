

import math
# from goods.goodsdata import *
from goods.sellgoods.auto_choose_goods.selected_goods_sort import *
from goods.sellgoods.auto_display.service_for_display import *
# from goods.sellgoods.commonbean.taizhang import *

def goods_sort(middle_list):
    """
    根据输入的中类列表进行选品的排序，排序时权衡了类别和销售额因素
    :param middle_list:
    :return:
    """
    goods_to_sort = ShelfGoodsSort(middle_list)
    list = goods_to_sort.main()
    result = []
    for i in list:
        result.append((i[5],i[4]))
    return result

def caculate_goods_info(taizhang):
    """
    计算商品的属性
    比如： 最终陈列量、单品刻度宽度、 faces数, 总刻度等
    :param taizhang:
    :return:
    """
    caculate_goods(taizhang)

def update_mark_goods_array(taizhang,change_total_width):
    """
    计算货架的商品刻度
    :param taizhang:
    :param change_total_width: 正数代表要加品，负数时减品
    :return:
    """
    update_mark_goods_array(taizhang,change_total_width)

def shelf_gap_choose_goods(taizhang,gap_width,neighbour_cls_three_code):
    """
    货架的缝隙进行商品填充
    :param taizhang:
    :param gap_width: 缝隙的宽度
    :param neighbour_cls_three_code: 缝隙旁边的小类
    :return:
    """
    pass


if __name__ == '__main__':
    a = goods_sort('0502')
    print(a)