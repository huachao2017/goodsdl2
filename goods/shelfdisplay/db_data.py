from django.db import connections

"""
ShareData
GoodsData
"""


def init_data():
    base_data = BaseData()
    # TODO 获取数据
    return base_data

class BaseData:
    """
    goods_arrange_weight: 四级分类、品牌、规格（包装）、尺寸（只选宽和高）
    category_area_ratio: 分类陈列面积比例表
    category3_intimate_weight: 三级分类亲密度
    category3_level_value: 三级分类层数分值
    goods_data_list: GoodsData列表
    """
    goods_arrange_weight = {'category4': 1, 'package_type': 0.9, 'brand': 0.8, 'height':0.7, 'width': 0.6}
    category_area_ratio = {'a': 0.1, 'b': 0.2, 'c': 0.3, 'd': 0.4, 'e': 0.5}
    category3_intimate_weight = {'a,b': 10, 'a,b,c': 5, 'd,e': 10, 'd,e,f': 5, 'd,e,f,g': 3}
    category3_level_value = {'b': 0, 'c': 10}
    goods_data_list = []

class GoodsData:
    """
    商品的纯信息数据
    """
    mch_code = None
    goods_name = None
    upc = None
    tz_display_img = None
    category1 = None
    category2 = None
    category3 = None
    category4 = None
    package_type = None # 包装方式
    brand = None # 品牌
    width = None
    height = None
    depth = None
    is_superimpose = None # 1可叠放，2不可叠放
    is_suspension = None # 1可挂放，2不可挂放
    psd = None # 预测销量

    face_num = 1 #在某个货架时填入 # FIXME 临时方案
    superimpose_num = 1 #在商品初始化时填入

    def equal(self, another_goods):
        if another_goods is not None:
            return self.mch_code == another_goods.mch_code
        return False

    def is_spu(self, another_goods):
        if another_goods is not None:
            return self.category4 == another_goods.category4 and self.package_type == another_goods.package_type and self.brand == another_goods.brand \
                   and abs(self.height - another_goods.height) < 5 and abs(self.width - another_goods.width) < 5
        return False

    def height_diff(self,another_goods):
        if another_goods is not None:
            # FIXME 需考虑叠放
            return self.height - another_goods.height
        return 0



