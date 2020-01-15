def get_level_to_display_goods_name(shelf):
    level_to_display_goods_name_str = {}
    for level in shelf.levels:
        display_goods_name_str = ''
        for display_goods in level.display_goods_list:
            for i in range(display_goods.face_num):
                display_goods_name_str += display_goods.goods_data.goods_name
                display_goods_name_str += ','

        level_to_display_goods_name_str[level.level_id] = display_goods_name_str

    return level_to_display_goods_name_str


class TestGoods:
    def __init__(self, category2, category3, goods_name, height, width, psd_amount, goods_role, ranking):
        self.category2 = category2
        self.category3 = category3
        self.goods_name = goods_name
        self.height = height
        self.width = width
        self.psd_amount = psd_amount
        self.goods_role = goods_role
        self.ranking = ranking

    def equal(self, another_goods):
        if another_goods is not None:
            return self.goods_name == another_goods.goods_name
        return False

    def __str__(self):
        return self.goods_name