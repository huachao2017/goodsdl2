class Shelf:
    taizhang_id = None
    shelf_id =  None
    width = None
    height = None
    depth = None
    levels = []

class Level:
    level_id = None # 层id
    goods_list = None  # 商品集合
    isTrue = None  # 是否货架上的真实层
    level_none_good_width = None  # 层空余的宽度
    level_start_height = None  # 层相对货架的起始高度
    level_width = None  #层宽度
    level_height = None  # 层高度
    level_depth = None  # 层深度

class Goods:
    #陈列信息
    gooddisplay_inss = [] # 商品陈列对象 列表

    #初始化数据
    mch_good_code = None
    sale_num = None  # TODO 预测销量
    sale_account = None # 预测销售额

    #数据信息
    upc = None
    name = None
    icon = None
    first_cls_code = None
    second_cls_code = None
    third_cls_code = None
    width = None
    height = None
    depth = None
    isfitting = None # 是否需要挂放
    fitting_rows = 1 # 需要挂放几行
    is_superimpose = None # 是否需要叠放  True  or False
    superimpose_rows = 2 # 叠放几行

    #计算信息
    display_num = None # 最终陈列量
    good_scale = None # 单品刻度宽度
    faces_num = None # faces 数
    one_face_most_goods_num = None # 单face最多的商品数
