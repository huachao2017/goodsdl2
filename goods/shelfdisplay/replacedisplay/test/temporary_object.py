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