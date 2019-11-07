class Shelf:
    taizhang_id = None
    shelf_id =  None
    width = None
    height = None
    depth = None
    levels = None
    hole_height = 10 # 孔高
    hole_dis = 5 # 孔距

    def __init__(self,taizhang_id,shelf_id, width,height,depth):
        self.taizhang_id = taizhang_id
        self.shelf_id = shelf_id
        self.width = width
        self.height = height
        self.depth = depth