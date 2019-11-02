from goods.sellgoods.commonbean.level import Level
from goods.sellgoods.salesquantity.proxy import display_rule
from goods.sellgoods.commonbean.good import GoodDisplay
import math
from goods.sellgoods.auto_display import service_for_display
from set_config import config
tz_display_maxitems = config.shellgoods_params['shelf_display_maxitems']
shelf_levels_max = config.shellgoods_params['shelf_levels_max']
shelf_level_start_height = config.shellgoods_params['shelf_level_start_height']
shelf_level_redundancy_height = config.shellgoods_params['shelf_level_redundancy_height']
shelf_top_level_height = config.shellgoods_params['shelf_top_level_height']
shelf_top_level_none_width = config.shellgoods_params['shelf_top_level_none_width']
def generate(tz_ins):
    """
     :param tz 对象
     :return:
     """
    # 上架商品到tz

    print ("tz.kedu1 "+str(tz_ins.last_twidth))
    put_good_to_tz(tz_ins)
    print("tz.kedu2 " + str(tz_ins.last_twidth))
    for shelf_ins in tz_ins.shelfs:
        # 计算上架后的货架 根据level冗余宽度 填充商品
        for level_ins in shelf_ins.levels:
            print ("shelf_id,level_id , sum, level_height,level_start_height "+str((shelf_ins.shelf_id,level_ins.level_id,len(level_ins.goods),level_ins.level_height,level_ins.level_start_height)))
    put_none_level_good_to_shelf(tz_ins)

def put_none_level_good_to_shelf(tz_ins):
    # 返回 [shelf_id,level_id,[good_ins]]
    # TODO 调用api  填充商品
    shelf_goods_list = api_get_level_none_good(tz_ins)
    for shelf_ins in tz_ins.shelfs:
        for level_ins in shelf_ins.levels:
            for (shelf_id,level_id,good_inss) in shelf_goods_list:
                if shelf_ins.shelf_id == shelf_id and level_ins.level_id == level_id:
                    put_good(level_ins,good_inss)



# 上商品到货架
def put_good_to_tz(tz_ins):
    try_flag = False
    for i in range(tz_display_maxitems):
        print("try display nums = "+str(i))
        shelfs = tz_ins.shelfs
        tz_goods = tz_ins.calculate_goods_array
        shelf_goods = display_rule.sort_display_code(tz_goods)  # 陈列分类  TODO 需要等加入陈列分类后测试 加入
        shelf_goods = display_rule.sort_good_height(shelf_goods)  # 商品高度
        shelf_goods = display_rule.sort_good_volume(shelf_goods)  # 商品体积
        put_shelf_goods = shelf_goods.copy()
        end_shelf_levels = None
        end_shelf_height = None
        width_kedu_sum = 0
        for shelf_ins,cnt in zip(shelfs,range(len(shelfs))):
            print("display shelf_num  = " + str(cnt))
            isAlter = False # 是不是最后一个货架
            if cnt == len(shelfs)-1:
                isAlter = True
            shelf_id = shelf_ins.shelf_id
            shelf_width = shelf_ins.width
            shelf_height = shelf_ins.height
            shelf_depth = shelf_ins.depth
            shelf_levels = shelf_ins.levels
            if shelf_levels == None :
                shelf_levels=[]
            if isAlter == False:  #不是最后一个货架
                flag,put_shelf_goods,shelf_levels = put_none_last_shelf(shelf_levels, shelf_height, shelf_width, shelf_depth, put_shelf_goods)
                if flag :
                    return
            else:
                try_flag, width_kedu_sum,end_shelf_height,end_shelf_levels,shelf_levels = put_last_shelf(shelf_levels,shelf_height,shelf_width,shelf_depth,put_shelf_goods,try_flag)
            shelf_ins.levels = shelf_levels
        if try_flag: # 层多于 货架物理层数
            # TODO 调用api 重新获取商品信息 需要传入变化的刻度
            print ("max true level do..............")
            is_update_flag = service_for_display.update_mark_goods_array(tz_ins, 0-width_kedu_sum)
            # is_update_flag = api_get_shelf_goods(tz_ins,(0-width_kedu_sum))
            if is_update_flag == False:
                break
            else:
                continue
        # 判断最顶层的 剩余商品的宽度值   如果该值 小于一定阈值 且重试次数大于5  结束重试
        elif end_shelf_height != None and end_shelf_height-end_shelf_levels[-1].level_start_height <= shelf_top_level_height and i > 5:
            if end_shelf_levels[-1].level_none_good_width < shelf_top_level_none_width:
                break
        elif end_shelf_height != None and end_shelf_height-end_shelf_levels[-1].level_start_height > shelf_top_level_height: # 层少于 货架物理层数
            # 用最后一层的刻度信息
            level_end_width_kedu_sum = get_level_kedu(end_shelf_levels[-1])
            # TODO 调用api 重新获取商品信息 需要传入变化的刻度
            print("min true level do..............")
            is_update_flag = service_for_display.update_mark_goods_array(tz_ins, 0 + level_end_width_kedu_sum)
            # is_update_flag = api_get_shelf_goods(tz_ins, 0 + level_end_width_kedu_sum)
            if is_update_flag == False:
                break
            else:
                continue
        else:
            continue

    return tz_ins


# 上架到非最后一个货架
def put_none_last_shelf(shelf_levels,shelf_height,shelf_width,shelf_depth,put_shelf_goods):
    flag = False # 摆放结束的标志
    for j in range(shelf_levels_max):
        if put_shelf_goods != None and len(put_shelf_goods) > 0:
            level_ins = get_level(shelf_levels, shelf_height, shelf_width, shelf_depth, isAlter=False)
            if level_ins == None:
                break
            else:
                put_shelf_goods = put_good_to_level(level_ins, put_shelf_goods, shelf_levels)
                shelf_levels.append(level_ins)
        else:
            print ("选品不够 ，未摆满货架 ...... ")
            flag = True
    return flag,put_shelf_goods,shelf_levels

# 上架到最后一个货架
def put_last_shelf(shelf_levels,shelf_height,shelf_width,shelf_depth,put_shelf_goods,try_flag):
    width_kedu_sum = 0
    for j in range(shelf_levels_max):
        if put_shelf_goods != None and len(put_shelf_goods) > 0:
            level_ins = get_level(shelf_levels, shelf_height, shelf_width, shelf_depth, isAlter=True)
            if level_ins != None:
                put_shelf_goods = put_good_to_level(level_ins, put_shelf_goods, shelf_levels)
                shelf_levels.append(level_ins)
        else:  # 没有摆放商品时 ，摆放结束
            break
    for level_ins in shelf_levels:
        if level_ins.isTrue == False:
            try_flag = True
            # 获取 未生效层 总刻度宽度
            width_kedu_sum += get_level_kedu(level_ins)
    end_shelf_height = shelf_height
    end_shelf_levels = shelf_levels
    return try_flag,width_kedu_sum,end_shelf_height,end_shelf_levels,shelf_levels

# 上商品到层
def put_good_to_level(level_ins,shelf_goods,shelf_levels):
    new_shelf_goods = []
    flag = True
    for shelf_good in shelf_goods:
        need_good_weight = 0
        if shelf_good.is_superimpose:
            need_good_weight = math.ceil(float(shelf_good.faces_num / shelf_good.superimpose_rows)) * shelf_good.width
        else: # TODO 这里对于 盒放的商品 没有做处理
            need_good_weight = shelf_good.faces_num * shelf_good.width
        # 优先放置前面没有放满的上两层
        if flag:
            fl1 = put_good_to_last_second(shelf_good, shelf_levels, need_good_weight)
            if fl1:
                continue
            print ("level_id , level_none_good_width,need_good_weight =  %s,%s,%s"%(str(level_ins.level_id),str(level_ins.level_none_good_width),str(need_good_weight)))
            if (level_ins.goods == None or len(level_ins.goods) < 1) or (need_good_weight <= level_ins.level_none_good_width): #如果层上没有商品 或者 满足摆放条件 层上剩余宽度 > 摆放当前upc 所需宽度 摆放商品
                put_good(level_ins,shelf_good)
            else:
                flag = False
                new_shelf_goods.append(shelf_good)
        else:
            new_shelf_goods.append(shelf_good)

    return new_shelf_goods


def put_good_to_last_second(shelf_good,shelf_levels,need_good_weight):
    level_ins1 = None
    level_ins2 = None
    # print (shelf_levels)
    if shelf_levels != None and len(shelf_levels) > 1:
        level_ins1 = shelf_levels[-1]
        level_ins2 = shelf_levels[-2]
    elif   shelf_levels != None and len(shelf_levels) == 1:
        level_ins1 = shelf_levels[-1]
    if level_ins1 != None and need_good_weight <= level_ins1.level_none_good_width:  # 满足摆放条件 层上剩余宽度 > 摆放当前upc 所需宽度 摆放商品
        put_good(level_ins1, shelf_good)
        return True
    elif level_ins2 != None and  need_good_weight <= level_ins2.level_none_good_width: #满足摆放条件 层上剩余宽度 > 摆放当前upc 所需宽度 摆放商品
        put_good(level_ins2, shelf_good)
        return True
    return False




    # 上商品
def put_good(level_ins,shelf_good):
    col = 0
    left = 0
    top = 0
    # 获取摆放初始坐标 和 左顶点信息
    if level_ins.goods == None or len(level_ins.goods) == 0:
        col = 0
    else:
        for level_good in level_ins.goods:
            width = level_good.width
            for good_display_ins in level_good.gooddisplay_inss:
                if good_display_ins.dep == 0 and good_display_ins.row == 0 :
                    left += (good_display_ins.left +width)
                    col = good_display_ins.col + 1
    if shelf_good.gooddisplay_inss == None or len(shelf_good.gooddisplay_inss) <1:
        shelf_good.gooddisplay_inss = []
    for i in range(shelf_good.display_num):
        # 先摆列方向  TODO 未考虑冗余
        col_nums = int(math.ceil(float(shelf_good.faces_num / shelf_good.superimpose_rows)))
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
        if level_ins.goods == None:
            level_ins.goods = []
        level_ins.goods.append(shelf_good)
    # 更新 层的剩余宽度
    level_ins.level_none_good_width = level_ins.level_width - get_level_goods_col_sum(level_ins)
    # 更新层的高度
    level_ins.level_height = get_level_height(level_ins)

def get_level_height(level_ins):
    level_height_end = 0
    for level_good in level_ins.goods:
        for gooddisplay_ins in level_good.gooddisplay_inss:
            if gooddisplay_ins.dep == 0 :
                level_height = 0
                if level_good.is_superimpose :
                    level_height =  level_good.superimpose_rows * level_good.height
                else:
                    level_height = level_good.height
                if level_height >= level_height_end:
                    level_height_end = level_height
    return level_height_end

def get_level_goods_col_sum(level_ins):
    goods_width  = 0
    for level_good in  level_ins.goods:
        for gooddisplay_ins in level_good.gooddisplay_inss:
            if gooddisplay_ins.row == 0 and gooddisplay_ins.dep == 0 :
                goods_width+=level_good.width
    return goods_width



def get_level_kedu(level_ins):
    face_kedu = 0
    for good_ins in level_ins.goods:
        for gooddisplay_ins in good_ins.gooddisplay_inss:
            if gooddisplay_ins.dep == 0 :
                ## TODO 可以考虑加冗余 宽度  这里暂时未加冗余
                face_kedu+=good_ins.width
    return face_kedu

def get_level(shelf_levels,shelf_height,shelf_width,shelf_depth,isAlter=False):
    if shelf_levels == None or len(shelf_levels) == 0 :
        level_ins =Level()
        level_ins.level_id = 0
        level_ins.isTrue = True
        level_ins.level_width = shelf_width
        level_ins.level_depth = shelf_depth
        level_ins.level_start_height = shelf_level_start_height
        level_ins.level_none_good_width = shelf_width
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
                level_start_height = level_ins.level_height + level_ins.level_start_height
        if shelf_height - level_start_height > shelf_top_level_height:  # 小于距离限制，产生新层
            level_id = level_ids[-1]+1
            level_ins = Level()
            level_ins.level_id = level_id
            level_ins.isTrue = True
            level_ins.level_width = shelf_width
            level_ins.level_depth = shelf_depth
            level_ins.level_start_height = level_start_height
            level_ins.level_none_good_width = shelf_width
            return level_ins
        elif isAlter: # 不产生新层 改为也产生新层 只是新层打上标记 不可用  只有最后一个货架有逻辑层
            level_id = level_ids[-1] + 1
            level_ins = Level()
            level_ins.level_id = level_id
            level_ins.isTrue = False
            level_ins.level_width = shelf_width
            level_ins.level_depth = shelf_depth
            level_ins.level_start_height = level_start_height
            level_ins.level_none_good_width = shelf_width
        else: #如果不是最后一个货架 ， 不产生新层
            return None




# 接口1
# 获取每层的填充商品，补充陈列
# 入参：neighbour_good 最近邻商品的三级code
#       level_goods 当前层所含有的三级code列表
#       level_diff_width  当前层 陈列中空置的宽度
# 返回： good 对象列表   sellgoods 下 commonbean 下
def api_get_level_none_good(taizhang):
    # TODO
    print ("do ..................")

# 接口2
# 重新计算所需刻度的商品列表
# 入参：taizhang  对象
#       shelf_diff_width 宽度超出或缺少的，超出为负，缺少为正

# 返回： True/False True为有更新，False为无更新
def api_get_shelf_goods(taizhang,shelf_diff_width=None):
    # TODO
    print("do ..................")

