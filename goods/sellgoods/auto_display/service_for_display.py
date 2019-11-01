
import math
import collections
# from goods.goodsdata import *
# from goods.sellgoods.auto_display.drink_display import upc_statistics

def calculate_goods(taizhang):
    # TODO

    twidth_to_goods = collections.OrderedDict()
    mark = 0
    shelf_depth = taizhang.shelfs[0].depth
    for good in taizhang.calculate_goods_array:
        good.display_num = max(good.sale_num*2,good.start_num)
        one_face_goods_number = int(shelf_depth/good.depth)
        if good.is_superimpose:   # 可叠放
            one_face_goods_number = one_face_goods_number*good.superimpose_rows
        good.faces_num = max(good.display_num/one_face_goods_number,1)

        good.good_scale = good.faces_num*good.width
        mark += good.good_scale
        twidth_to_goods[mark] = good
        # twidth_to_goods[good.mch_good_code] = mark
    taizhang.twidth_to_goods = twidth_to_goods
    taizhang.last_twidth = mark

def update_mark_goods_array(taizhang,change_total_width):
    """
    更新货架所需的商品的刻度
    :param taizhang:
    :param change_total_width: 改变的宽度
    :return:
    """

    # if change_total_width < 0:
    #     sum = 0
    #     reversed_calculate_goods_array = list(reversed(taizhang.calculate_goods_array))
    #     for good in reversed_calculate_goods_array:
    #         a = math.fabs(change_total_width) - sum
    #         sum += good.good_scale
    #         b = sum - math.fabs(change_total_width)
    #         if a > 0 and b > 0:
    #             good_index = taizhang.calculate_goods_array.index(good)
    #             if a > b:
    #                 taizhang.last_twidth = taizhang.twidth_to_goods(taizhang.calculate_goods_array[good_index-1].mch_good_code)
    #             else:
    #                 taizhang.last_twidth = taizhang.twidth_to_goods(taizhang.calculate_goods_array[good_index].mch_good_code)
    #
    # if change_total_width > 0:
    #     pass
    tem = []
    taizhang.last_twidth += change_total_width
    for mark,good in taizhang.twidth_to_goods:
        if mark < taizhang.last_twidth:
            tem.append(good)
    taizhang.calculate_goods_array = tem

def shelf_gap_choose_goods(taizhang,neighbour_good,level_goods,level_diff_width=None):
    """
    空隙补品
    :param taizhang:
    :param neighbour_good:
    :param level_goods:
    :param level_diff_width:
    :return:
    """







# class DisplayData():
#
#     def __init__(self):
#         pass
#     def get_shop_shelfs_upcs(self,shop_id):
#         # 获取某店的所有货架对应的陈列的类别
#         shelfs = get_shop_shelfs(shop_id)
#         # 获取该店选品列表
#         upcs = get_shop_selected_goods()
#         # 获取upc的统计信息
#         upc_statistics_dict = upc_statistics(upcs)
#         # 遍历每个货架，获取该货架下的类别的所有upc
#         for shelf in shelfs:
#             codes_str = shelf[0]
#             codes_list = codes_str.split(".")
#             for code in codes_list:
#                 if len(code) == 2:
#                     upc_statistics_dict[code]
#
#         # 获取upc对应的信息
#         # 根据类别和预计销售额进行排序
#         # 计算每个upc的宽度
#         # 依次给每个upc加上刻度