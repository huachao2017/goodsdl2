from set_config import config
from goods.sellgoods.salesquantity.local_util import shelf_display
from goods.sellgoods.commonbean.taizhang import Taizhang
from goods.sellgoods.commonbean.shelf import Shelf
from goods.goodsdata import get_raw_shop_shelfs,get_raw_goods_info
from goods.sellgoods.auto_choose_goods.out_service_api import goods_sort,caculate_goods_info
# 生成自动陈列
shelf_display = config.shellgoods_params['shelf_display']

def generate_displays(uc_shopid, tz_id):
    """
    :param uc_shopid:
    :param tz_id:
    :return:
    """

    taizhang = Taizhang()
    # 生成taizhang对象，初始化所有数据相关的字段
    raw_shelfs = get_raw_shop_shelfs(uc_shopid,tz_id)
    taizhang.tz_id = tz_id
    for raw_shelf in raw_shelfs:
        shelf = Shelf(
            raw_shelf.taizhang_id,
            raw_shelf.shelf_id,
            raw_shelf.length,
            raw_shelf.height,
            raw_shelf.depth
        )
        taizhang.associated_catids = raw_shelf.associated_catids # FIXME
        taizhang.shelfs.append(shelf)

    goods_list = goods_sort(taizhang.associated_catids)
    # caculate_goods_array 李树、华超
    # 李树：输入参数中类的list，mch_goods_code列表，返回一个mch_goods_code列表
    # 华超：根据上一步生成caculate_goods_array，将所有goods的数据信息填入

    mch_codes = []
    for goods in taizhang.caculate_goods_array:
        mch_codes.append(goods.mch_good_code)
    mch_cods_to_data_law_goods = get_raw_goods_info(uc_shopid,mch_codes)
    for goods in taizhang.caculate_goods_array:
        data_law_goods = mch_cods_to_data_law_goods[goods.mch_good_code]
        corp_classify_code = data_law_goods.corp_classify_code
        if len(str(corp_classify_code)) == 6:
            goods.first_cls_code = corp_classify_code[0:2]
            goods.second_cls_code = corp_classify_code[0:4]
            goods.third_cls_code = corp_classify_code
        else:
            print('corp_classify_code error: {}'.format(corp_classify_code))

        goods.width = data_law_goods.width
        goods.height = data_law_goods.height
        goods.depth = data_law_goods.depth
        goods.start_num = data_law_goods.start_num
        goods.display_code = data_law_goods.display_code # 陈列分类code
        goods.isfitting = None # TODO 是否需要挂放
        goods.fitting_rows = 1 # 需要挂放几行
        goods.is_superimpose = data_law_goods.is_superimpose
        goods.superimpose_rows = 2 # 叠放几行


    # twidth_to_goods 李树
    # 输入：taizhang，
    # 将goods的计算信息填入，同时将twidth_to_goods生成出来
    caculate_goods_info(taizhang)

    # 排列货架 生成陈列
    shelf_display.generate(taizhang)

    return taizhang

