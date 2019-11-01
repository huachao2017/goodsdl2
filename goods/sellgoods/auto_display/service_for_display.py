
import math
# from goods.goodsdata import *
# from goods.sellgoods.auto_display.drink_display import upc_statistics

def get_shop_selected_goods(shop_id):
    data = []
    return data

# 接口2  （李树）
# 获取每层的填充商品，补充陈列
# 入参：neighbour_cls_three_code 最近邻商品的三级code
#       level_cls_three_codes 当前层所含有的三级code列表
#       level_none_good_width  当前层 陈列中空置的宽度
# 返回： good 对象列表   sellgoods 下 commonbean 下
def api_get_level_none_good(shop_id,shelf_id,neighbour_cls_three_code,level_cls_three_codes,level_none_good_width):
    # TODO
    print ("do ..................")



# 接口3  （李树）
#获取带刻度的商品列表
# 入参：shop_id  门店id
#       shelf_id 货架id

# 返回： good 对象列表   sellgoods 下 commonbean 下
def api_get_mark_goods(taizhang,shelf_id,kd_value=None):
    # TODO
    pass






#接口4    （李树）
#接口4  获取shop对象
# 入参： shop_id
# 入参： isfir 是否首次生成 陈列  如果是：使用好邻居的推荐销量  否：使用线上该店的真实销量
# 返回： shop 对象  sellgoods 下 commonbean 下
def caculate_goods(taizhang):
    # TODO
    twidth_to_goods = {}
    mark = 0
    for shelf in taizhang.shelfs:
        for level in shelf.levels:
            for good in level.goods:
                good.display_num = max(good.sale_num*2,good.start_num)
                one_face_goods_number = int(shelf.depth/good.depth)
                if good.is_superimpose:   # 可叠放
                    one_face_goods_number = one_face_goods_number*good.superimpose_rows
                good.faces_num = max(good.display_num/one_face_goods_number,1)

                good.good_scale = good.faces_num*good.width
                mark += good.good_scale
                twidth_to_goods[mark] = good
    taizhang.twidth_to_goods = twidth_to_goods

def update_mark_goods_array(taizhang,change_total_width):

    if change_total_width < 0:
        sum = 0
        reversed_caculate_goods_array = list(reversed(taizhang.caculate_goods_array))
        for good in reversed_caculate_goods_array:
            a = math.fabs(change_total_width) - sum
            sum += good.good_scale
            b = sum - math.fabs(change_total_width)
            if a > 0 and b > 0:
                if a < b:
                    pass

            if sum > change_total_width:
                index = taizhang.caculate_goods_array.index(good)
                taizhang.caculate_goods_array = 0







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