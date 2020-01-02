class Shelf:
    def __init__(self, shelf_id, height, width, depth):
        self.levels = []
        self.shelf_id = shelf_id
        self.height = height
        self.width = width
        self.depth = depth

    def add_level(self, level):
        self.levels.append(level)

    def copy_raw(self):
        shelf = Shelf(self.shelf_id, self.height, self.width, self.depth)
        for level in self.levels:
            copy_level = Level(shelf, level.level_id, level.height, level.depth)
            shelf.levels.append(copy_level)

        return shelf

    def __str__(self):
        ret = ''
        for level in self.levels:
            ret += str(level.level_id)
            ret += ':'
            for display_goods in level.display_goods_list:
                for i in range(display_goods.face_num):
                    ret += display_goods.goods_data.goods_name
                    ret += ','

            ret += '\n'

        return ret

class Level:
    def __init__(self, shelf, level_id, height, depth):
        self.shelf = shelf  # 货架
        self.level_id = level_id  # 层id
        self.height = height
        self.depth = depth
        self.display_goods_list = []

    def add_display_goods(self, display_goods):
        self.display_goods_list.append(display_goods)

    def __str__(self):
        ret = str(self.level_id)
        ret += ','
        ret += str(self.height)
        ret += ','
        ret += str(self.depth)
        return ret

class DisplayGoods:
    def __init__(self, goods_data, face_num = 1, superimpose_num = 1):
        self.goods_data = goods_data
        self.face_num = face_num
        self.superimpose_num = superimpose_num

    def get_display_info(self, level):
        """
        :return:GoodsDisplayInfo列表
        """
        display_goods_info = []
        display_goods_list = level.display_goods_list
        init_top = self.goods_data.height
        init_left = 0
        for display_goods in display_goods_list:
            if self.goods_data.equal(display_goods.goods_data):
                break
            init_left += display_goods.goods_data.width * display_goods.face_num
        for i in range(self.face_num + self.goods_data.superimpose_num):
            for j in range(self.superimpose_num):
                col = i
                row = j
                top = init_top + j * self.goods_data.height
                left = init_left + i * self.goods_data.width
                display_goods_info.append(DisplayOneGoodsInfo(col, row, top, left))

        return display_goods_info

    def get_one_face_max_display_num(self, level):
        max_one_face = int(level.depth / self.goods_data.depth)
        if max_one_face <= 0:
            print('商品深度越界：{}，{}'.format(self.goods_data.depth, level.depth))
            max_one_face = 1
        return max_one_face

class DisplayOneGoodsInfo:
    def __init__(self, col, row, top, left):
        self.col = col  # 在level上的列
        self.row = row  # 行
        self.top = top
        self.left = left
