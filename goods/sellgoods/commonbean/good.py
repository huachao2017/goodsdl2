class Good:
    #陈列信息
    gooddisplay_inss = None # 商品陈列对象 列表

    #初始化数据
    mch_good_code = None
    sale_num = None  # TODO 预测销量

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
    start_num = None  #最小起订量
    display_code = None # 陈列分类code
    isfitting = None # 是否需要挂放
    fitting_rows = 1 # 需要挂放几行
    is_superimpose = None # 是否需要叠放  True  or False
    superimpose_rows = 2 # 叠放几行
    # isboxing = None # 是否需要盒放
    # box_nums = None # 盒子能容纳的量
    # box_width = None # 盒子的宽度
    # box_height = None
    # box_depth = None
    # box_faces = None # 盒子的face数
    # box_isstack = None # 盒子是否叠放
    # box_row = None # 盒子叠放row

    #计算信息
    display_num = None # 最终陈列量
    good_scale = None # 单品刻度宽度
    faces_num = None # faces 数

class GoodDisplay:
    col = None  # 在level上的列
    row = None  # 行
    dep = None  # 深度方向上的列
    top = None
    left = None
