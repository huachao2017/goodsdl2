class ChildArea:
    def __init__(self, level_id, display_goods_list):
        self.level_id = level_id
        self.display_goods_list = display_goods_list
        self.down_display_goods_list = []
        self.category3 = display_goods_list[0].goods_data.category3

    def get_goods_width(self):
        goods_width = 0
        for display_goods in self.display_goods_list:
            goods_width += display_goods.goods_data.width * display_goods.face_num
        return goods_width

    def __str__(self):
        ret = str(self.level_id) + '-' + str(self.category3) + ':['
        for display_goods in self.display_goods_list:
            for i in range(display_goods.face_num):
                ret += str(display_goods.goods_data)
                ret += ','
        ret += '], '

        return ret