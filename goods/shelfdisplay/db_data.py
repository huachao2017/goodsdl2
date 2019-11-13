"""
ShareData
GoodsData
"""

class BaseData:
    """
    goods_arrange_weight: 四级分类、品牌、规格（包装）、尺寸（只选宽和高）
    category_area_ratio: 分类陈列面积比例表
    goods_data_list: GoodsData列表
    """
    goods_arrange_weight = {'category4': 1, 'package_type': 0.9, 'brand': 0.8, 'height':0.7, 'width': 0.6}
    category_area_ratio = {'a': 0.1, 'b': 0.2, 'c': 0.3, 'd': 0.4, 'e': 0.5}
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
    spec = None # 规格
    brand = None # 品牌
    width = None
    height = None
    depth = None
    is_superimpose = None # 1可叠放，2不可叠放
    is_suspension = None # 1可挂放，2不可挂放
    psd = None # 预测销量
