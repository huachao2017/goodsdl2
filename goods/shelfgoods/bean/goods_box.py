#定义每层的商品位置关系类
class GoodsBox:
    level = None
    level_columns = None
    goodscolumns = None
    def __init__(self,level,level_columns,goodscolumns):
        self.level = level
        self.level_columns = level_columns
        self.goodscolumns = goodscolumns

class GoodsColumn:
    upc=None
    name=None
    box_id = None
    location_column = None
    location_row = None
    location_left = None
    location_bottom = None
    location_weight = None
    location_height = None
    location_box = None
    compare_result = None
    compare_code = None
    is_fitting = None
    process_code = None
    is_label = None
    result = None



