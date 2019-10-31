from goods.sellgoods.commonbean.level import Level
from goods.sellgoods.salesquantity.proxy import display_rule
from goods.sellgoods.commonbean.good import GoodDisplay
import math
from set_config import config
shelf_display_maxitems = config.shellgoods_params['shelf_display_maxitems']
shelf_levels_max = config.shellgoods_params['shelf_levels_max']
shelf_level_start_height = config.shellgoods_params['shelf_level_start_height']
shelf_level_redundancy_height = config.shellgoods_params['shelf_level_redundancy_height']
shelf_top_level_height = config.shellgoods_params['shelf_top_level_height']
shelf_top_level_none_width = config.shellgoods_params['shelf_top_level_none_width']
def generate(shop_id,isfir=False):
    shop_ins = api_get_shop(shop_id)
    shop_id = shop_ins.shop_id
    taizhangid_to_shelfs = shop_ins.taizhangid_to_shelf
    taizhangid_to_goods = shop_ins.taizhangid_to_goods_array
    for tzid in taizhangid_to_shelfs:
        shelfs = taizhangid_to_shelfs[tzid]
        shelf_goods = taizhangid_to_goods[tzid]
        for shelf_ins in shelfs:
            # 排序规则
            shelf_goods = display_rule.sort_display_code(shelf_goods) #陈列分类  TODO 需要等加入陈列分类后测试 加入
            shelf_goods = display_rule.sort_good_height(shelf_goods) #商品高度
            shelf_goods = display_rule.sort_good_volume(shelf_goods) #商品体积
            # 上架商品
            shelf_ins = put_good_to_shelf(shelf_ins,shelf_goods)
            # 计算上架后的货架 根据level冗余宽度 填充商品
            shelf_ins = put_none_level_good_to_shelf(shelf_ins)
    return  shop_ins

def put_none_level_good_to_shelf(shelf_ins):
    levels = shelf_ins.levels

    for level_ins in levels:
        level_cls_three_codes = []
        neighbour_cls_three_code=level_ins.goods[-1].thrid_cls_code
        for level_good in level_ins.goods:
            level_cls_three_codes.append(level_good.thrid_cls_code)
        level_cls_three_codes = list(set(level_cls_three_codes))
        level_none_good_width = level_ins.level_none_good_width
        # TODO 调用api  填充商品




# 上商品到货架
def put_good_to_shelf(shelf_ins,shelf_goods):
    put_shelf_goods = shelf_goods.copy()
    try_flag = False
    end_shelf_levels =None
    for i in range(shelf_display_maxitems):
        shelf_id = shelf_ins.shelf_id
        shelf_width = shelf_ins.width
        shelf_height = shelf_ins.height
        shelf_depth = shelf_ins.depth
        shelf_levels = []

        for j in range(shelf_levels_max):
            if put_shelf_goods != None and len(put_shelf_goods)>0 :
                level_ins = get_level(shelf_levels,shelf_height,shelf_width,shelf_depth)
                if level_ins == None :
                    print ("level error")
                    return
                else:
                    level_ins,put_shelf_goods = put_good_to_level(level_ins,put_shelf_goods)
                    shelf_levels.append(level_ins)
            else: # 没有摆放商品时 ，摆放结束
                break
        width_kedu_sum = 0
        for level_ins in shelf_levels:
            if level_ins.isTrue == False:
                try_flag = True
                # 获取 未生效层 总刻度宽度
                width_kedu_sum += get_level_kedu(level_ins)
        end_shelf_levels = shelf_levels

        if try_flag: # 层多于 货架物理层数
            # TODO 调用api 重新获取商品信息 需要传入变化的刻度
            print ("do..............")
            continue
        # 判断最顶层的 剩余商品的宽度值   如果该值 小于一定阈值 且重试次数大于5  结束重试
        if try_flag == False and shelf_height-shelf_levels[-1].level_start_height <= shelf_top_level_height and i > 5:
            if shelf_levels[-1].level_none_good_width < shelf_top_level_none_width:
                break
        elif try_flag == False and shelf_height-shelf_levels[-1].level_start_height > shelf_top_level_height: # 层少于 货架物理层数
            # 用最后一层的刻度信息
            level_end_width_kedu_sum = get_level_kedu(shelf_levels[-1])
            # TODO 调用api 重新获取商品信息 需要传入变化的刻度
            print("do..............")
            continue
    shelf_ins.levels = end_shelf_levels
    return shelf_ins,put_shelf_goods

# 上商品到层
def put_good_to_level(level_ins,shelf_goods):
    new_shelf_goods = []
    put_flag = True
    for shelf_good in shelf_goods:
            need_good_weight = 0
            if shelf_good.isstacking:
                need_good_weight = math.ceil(float(shelf_good.faces / shelf_good.stack_rows)) * shelf_good.width
            else: # TODO 这里对于 盒放的商品 没有做处理
                need_good_weight = shelf_good.faces * shelf_good.width

            if need_good_weight <= level_ins.level_none_good_width and put_flag: #满足摆放条件 层上剩余宽度 > 摆放当前upc 所需宽度 摆放商品
                level_ins = put_good(level_ins,shelf_good)
            elif need_good_weight >= level_ins.level_width: # 如果所需要的商品总宽度 大于 整个层宽
                if level_ins.goods == None or len(level_ins.goods) < 1:  # 层上没有任何商品， 则放置商品
                    level_ins = put_good(level_ins, shelf_good)
            else:
                put_flag = False
                # 出现放不下 ，把该商品 移到上一层
            if put_flag == False:
                new_shelf_goods.append(shelf_good)
    # 生成层高度
    level_heights = []
    for level_good in level_ins.goods:
        height = 0
        if level_good.dep == 0 :
            if level_good.isstacking :
                height =  level_good.stack_rows * level_good.height + shelf_level_redundancy_height
            else:
                height = level_good.height + shelf_level_redundancy_height
        level_heights.append(height)
    level_heights.sort()
    level_ins.level_height = level_heights[-1]
    return level_ins,new_shelf_goods

# 上商品
def put_good(level_ins,shelf_good):
    col = 0
    left = 0
    top = 0
    # 获取摆放初始坐标 和 左顶点信息
    if level_ins.goods == None or len(level_ins.goods) == 0:
        col = 0
    else:
        col = level_ins.goods[-1].col + 1
        for level_good in level_ins.goods:
            width = level_good.width
            for good_display_ins in level_good.gooddisplay_inss:
                if good_display_ins.dep == 0 and good_display_ins.row == 0 :
                    left += (good_display_ins.left +width)

    if shelf_good.gooddisplay_inss == None or len(shelf_good.gooddisplay_inss) <1:
        shelf_good.gooddisplay_inss = []
    for i in range(shelf_good.display_num):
        # 先摆列方向  TODO 未考虑冗余
        col_nums = int(math.ceil(float(shelf_good.faces / shelf_good.stack_rows)))
        for j in range(col_nums):
            # 再摆行方向
            if shelf_good.is_superimpose:
                for k in range(shelf_good.superimpose_rows):
                    # 再摆深方向  TODO 未考虑冗余
                    for l in range(int(math.floor(level_ins.level_depth / shelf_good.depth))):
                        gdins = GoodDisplay()
                        gdins.col =col + i
                        gdins.row = j
                        gdins.dep = l
                        gdins.left = left+i*shelf_good.width
                        gdins.top = top + j*shelf_good.height
                        shelf_good.gooddisplay_inss.append(gdins)
        level_ins.goods.append(shelf_good)
    # 更新 层的剩余宽度
    level_ins.level_none_good_width = level_ins.width - get_level_goods_col_sum(level_ins)
    return level_ins


def get_level_goods_col_sum(level_ins):
    goods_width  = 0
    for level_good in  level_ins.goods:
        if level_good.row == 0 and level_good.dep == 0 :
            goods_width+=level_good.width
    return goods_width



def get_level_kedu(level_ins):
    face_kedu = 0
    for good_ins in level_ins.goods:
        if good_ins.dep == 0 :
            ## TODO 可以考虑加冗余 宽度  这里暂时未加冗余
            face_kedu+=good_ins.width
    return face_kedu

def get_level(shelf_levels,shelf_height,shelf_width,shelf_depth):
    if shelf_levels == None or len(shelf_levels) == 0 :
        level_ins =Level()
        level_ins.level_id = 0
        level_ins.isTrue = True
        level_ins.level_width = shelf_width
        level_ins.level_depth = shelf_depth
        level_ins.level_start_height = shelf_level_start_height
        return level_ins
    else:
        level_ids = []
        for level_ins in shelf_levels:
            level_ids.append(level_ins.level_id)
        level_ids = list(set(level_ids))
        level_ids.sort()
        level_start_height = 0
        for level_ins in shelf_levels:
            if level_ins.level_id == level_ids[-1]:
                level_start_height = level_ins.height + level_ins.level_start_height
        if shelf_height - level_start_height < shelf_top_level_height:  # 小于距离限制，产生新层
            level_id = level_ids[-1]+1
            level_ins = Level()
            level_ins.level_id = level_id
            level_ins.isTrue = True
            level_ins.level_width = shelf_width
            level_ins.level_depth = shelf_depth
            level_ins.level_start_height = level_start_height
            return level_ins
        else: # 不产生新层 改为也产生新层 只是新层打上标记 不可用
            # return None
            level_id = level_ids[-1] + 1
            level_ins = Level()
            level_ins.level_id = level_id
            level_ins.isTrue = False
            level_ins.level_width = shelf_width
            level_ins.level_depth = shelf_depth
            level_ins.level_start_height = level_start_height



# 获取商品陈列分类
def get_dispaly_code(shelf_goods):
    # TODO 调用api
    return shelf_goods

# 接口1
# 获取陈列分类
# 入参 upcs   商品的upcs 列表
# 返回： [{"upc":code},{"upc":code}]
def api_get_dispaly_code(upc):
    # TODO
    print ("do ..................")

# 接口2
# 获取每层的填充商品，补充陈列
# 入参：neighbour_cls_three_code 最近邻商品的三级code
#       level_cls_three_codes 当前层所含有的三级code列表
#       level_none_good_width  当前层 陈列中空置的宽度
#       kd 上次取商品的刻度
# 返回： good 对象列表   sellgoods 下 commonbean 下
def api_get_level_none_good(shop_id,tz_id,neighbour_cls_three_code,level_cls_three_codes,level_none_good_width,kd=None):
    # TODO
    print ("do ..................")

# 接口3
#获取带刻度的商品列表
# 入参：shop_id  门店id
#       shelf_id 货架id

# 返回： good 对象列表   sellgoods 下 commonbean 下
def api_get_shelf_goods(shop_id,tz_id,kd_value=None,kd=None):
    # TODO
    print("do ..................")



#接口4  获取shop对象
# 入参： shop_id
# 入参： isfir 是否首次生成 陈列  如果是：使用好邻居的推荐销量  否：使用线上该店的真实销量
# 返回： shop 对象  sellgoods 下 commonbean 下
def api_get_shop(shop_id,isfir=False):
    # TODO
    print("do ..................")