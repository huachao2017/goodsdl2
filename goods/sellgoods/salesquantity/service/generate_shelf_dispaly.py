from set_config import config
from goods.sellgoods.salesquantity.local_util import shelf_display
from goods.sellgoods.commonbean.taizhang import Taizhang
# 生成自动陈列
shelf_display = config.shellgoods_params['shelf_display']

def generate_displays(shopid, tz_id):
    """
    :param shopid:
    :param tz_id:
    :return:
    """

    print (shopid)
    taizhang = Taizhang()
    # TODO 调用方法获取 门店内货架与商品信息
    # 生成taizhang对象，初始化所有数据相关的字段

    # shelfs 华超 从数据库初始化，在shelf字段level中止

    # goods_array 李树、华超
    # 李树：输入参数中类的list，mch_goods_code列表，返回一个mch_goods_code列表
    # 华超：根据上一步生成goods_array，将所有goods的数据信息填入



    # kedu_to_goods 李树
    # 输入：taizhang，
    # 将goods的计算信息填入，同时将twidth_to_goods生成出来

    # 排列货架 生成陈列
    shelf_display.generate(taizhang)

    return taizhang

