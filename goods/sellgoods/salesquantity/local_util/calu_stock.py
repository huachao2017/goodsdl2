import math
def get_stock(upc_depth,shelf_depth,faces):
    if upc_depth == None or upc_depth == 0 :
        upc_depth = 0.001
    if shelf_depth == None or shelf_depth == 0:
        shelf_depth = 0.001
    if faces == None or faces == 0:
        faces = 1
    min_stock = faces
    max_stock = faces * math.floor(float(shelf_depth)/upc_depth)
    return max_stock,min_stock