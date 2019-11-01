class Shelf:
    taizhang_id = None
    shelf_id =  None
    shelf_class_codes = None
    width = None
    height = None
    depth = None
    levels = None

    def __init__(self,taizhang_id,shelf_id, shelf_class_codes,width,height,depth):
        self.taizhang_id = taizhang_id
        self.shelf_id = shelf_id
        self.shelf_class_codes = shelf_class_codes
        self.width = width
        self.height = height
        self.depth = depth