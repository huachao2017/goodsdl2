class Good:
    upc = None
    name = None
    mch_good_code = None
    mch_id = None
    first_cls_code = None
    second_cls_code = None
    third_cls_code = None
    width = None
    height = None
    depth = None
    sale_num = None  #销量
    start_num = None  #最小起订量
    display_num = None # 最终陈列量
    good_scale = None # 单品刻度宽度
    display_code = None # 陈列分类code
    faces_num = None # faces 数
    isfitting = None # 是否需要挂放
    fitting_rows = None # 需要挂放几行
    is_superimpose = None # 是否需要叠放  True  or False
    superimpose_rows = None # 叠放几行
    isboxing = None # 是否需要盒放
    box_nums = None # 盒子能容纳的量
    box_width = None # 盒子的宽度
    box_height = None
    box_depth = None
    box_faces = None # 盒子的face数
    box_isstack = None # 盒子是否叠放
    box_row = None # 盒子叠放row

class GoodDisplay:
    col = None  # 在level上的列
    row = None  # 行
    dep = None  # 深度方向上的列
    top = None
    left = None
