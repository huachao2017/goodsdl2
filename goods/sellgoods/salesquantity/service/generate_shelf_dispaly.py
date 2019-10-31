from set_config import config
from goods.sellgoods.salesquantity.local_util import shelf_display
from goods.sellgoods.commonbean.taizhang import Taizhang
from goods.sellgoods.commonbean.shelf import Shelf
from goods.goodsdata import get_raw_shop_shelfs,get_raw_goods_info
# 生成自动陈列
shelf_display = config.shellgoods_params['shelf_display']

def generate_displays(shopid, tz_id):
    """
    :param shopid:
    :param tz_id:
    :return:
    """

    taizhang = Taizhang()
    # 生成taizhang对象，初始化所有数据相关的字段
    raw_shelfs = get_raw_shop_shelfs(shopid,tz_id)
    taizhang.tz_id = tz_id
    for raw_shelf in raw_shelfs:
        shelf = Shelf(
            raw_shelf.taizhang_id,
            raw_shelf.shelf_id,
            raw_shelfs.associated_catids,
            raw_shelfs.length,
            raw_shelfs.height,
            raw_shelfs.depth
        )
        taizhang.shelfs.append(shelf)

    # caculate_goods_array 李树、华超
    # 李树：输入参数中类的list，mch_goods_code列表，返回一个mch_goods_code列表
    # 华超：根据上一步生成caculate_goods_array，将所有goods的数据信息填入



    # twidth_to_goods 李树
    # 输入：taizhang，
    # 将goods的计算信息填入，同时将twidth_to_goods生成出来

    # 排列货架 生成陈列
    shelf_display.generate(taizhang)

    return taizhang

