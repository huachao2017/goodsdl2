class ShelfInfos:
    shelf_info=None


class ShelfInfo:
    shelf_id = None
    shelf_type_id = None
    length = None
    width = None
    depth = None
    levelinfos = None

class LevelInfo :
    level_id = None
    is_fitting = None
    upcinfos = None

class UpcInfo :
    upc=None
    row=None
    col=None
    name=None
    width = None
    height = None
    depth = None
    is_fitting = None
    mch_goods_code = None
    rotate = None