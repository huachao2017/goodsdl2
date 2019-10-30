from goods.sellgoods.commonbean.level import Level
from goods.sellgoods.salesquantity.proxy import display_rule
from set_config import config
shelf_display_maxitems = config.shellgoods_params['shelf_display_maxitems']
shelf_levels_max = config.shellgoods_params['shelf_levels_max']
shelf_level_start_height = config.shellgoods_params['shelf_level_start_height']
shelf_level_redundancy_height = config.shellgoods_params['shelf_level_redundancy_height']
shelf_top_level_height = config.shellgoods_params['shelf_top_level_height']
def generate(shop_ins):
    shop_id = shop_ins.shop_id
    shelfs = shop_ins.shelfs

    for shelf_ins in shelfs:

        shelf_goods = shelf_ins.goods
        shelf_goods = get_dispaly_code(shelf_goods)
        # 排序规则
        shelf_goods = display_rule.sort_display_code(shelf_goods) #陈列分类
        shelf_goods = display_rule.sort_good_height(shelf_goods) #商品高度
        shelf_goods = display_rule.sort_good_volume(shelf_goods) #商品体积

        # 上架商品


def put_good_to_shelf(shelf_ins,shelf_goods):

    for i in range(shelf_display_maxitems):
        shelf_id = shelf_ins.shelf_id
        shelf_width = shelf_ins.width
        shelf_height = shelf_ins.height
        shelf_depth = shelf_ins.depth
        shelf_levels = []
        for j in range(shelf_levels_max):
            level_ins = get_level(shelf_levels,shelf_height)
            if level_ins == None :
                return
            else:
                print ("do....")

def put_good_to_level(level_ins,shelf_goods):
    print ("do ....")

def get_level(shelf_levels,shelf_height):
    if shelf_levels == None or len(shelf_levels) == 0 :
        level_ins =Level()
        level_ins.level_id = 0
        level_ins.height = shelf_level_start_height
        return level_ins
    else:
        level_ids = []
        for level_ins in shelf_levels:
            level_ids.append(level_ins.level_id)
        level_ids = list(set(level_ids))
        level_ids.sort(level_ids)
        level_max_height = None
        for level_ins in shelf_levels:
            if level_ins.level_id == level_ids[-1]:
                level_max_height = level_ins.height
        if shelf_height - level_max_height < shelf_top_level_height:  # 小于距离限制，产生新层
            level_id = level_ids[-1]+1
            level_ins = Level()
            level_ins.level_id = level_id
            return level_ins
        else: # 不产生新层
            return None





def get_dispaly_code(shelf_goods):
    # TODO 调用api
    return shelf_goods
