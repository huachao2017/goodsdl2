import os
import cv2
import numpy as np
from set_config import config
from goods.sellgoods.salesquantity.local_util import shelf_display
from goods.sellgoods.commonbean.taizhang import Taizhang
from goods.sellgoods.commonbean.shelf import Shelf
from goods.sellgoods.commonbean.good import Good
from goods.goodsdata import get_raw_shop_shelfs,get_raw_goods_info
from goods.sellgoods.auto_choose_goods.out_service_api import goods_sort,calculate_goods_info
# 生成自动陈列
# shelf_display = config.shellgoods_params['shelf_display']

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
        taizhang.associated_catids = raw_shelf.associated_catids
        taizhang.shelfs.append(shelf)

    # caculate_goods_array 李树、华超
    simple_goods_list = goods_sort(taizhang.associated_catids)
    mch_codes = []
    for simple_goods in simple_goods_list:
        mch_codes.append(simple_goods[0])

    # 李树：输入参数中类的list，mch_goods_code列表，返回一个mch_goods_code列表
    # 华超：根据上一步生成caculate_goods_array，将所有goods的数据信息填入
    mch_codes_to_data_raw_goods = get_raw_goods_info(uc_shopid,mch_codes)
    taizhang.calculate_goods_array = []
    for simple_goods in simple_goods_list:
        if simple_goods[0] in mch_codes_to_data_raw_goods:
            data_raw_goods = mch_codes_to_data_raw_goods[simple_goods[0]]
            good = Good()
            good.mch_good_code = simple_goods[0]
            good.sale_account = simple_goods[1]
            corp_classify_code = data_raw_goods.corp_classify_code
            if len(str(corp_classify_code)) == 6:
                good.first_cls_code = corp_classify_code[0:2]
                good.second_cls_code = corp_classify_code[0:4]
                good.third_cls_code = corp_classify_code
            else:
                good.first_cls_code = 0
                good.second_cls_code = 0
                good.third_cls_code = 0
                print('corp_classify_code error: {}'.format(corp_classify_code))

            # 陈列分类code TODO
            if len(str(data_raw_goods.display_code)) == 6:
                good.display_code = data_raw_goods.display_code
            else:
                good.display_code = 0
                print('corp_classify_code error: {}'.format(corp_classify_code))

            good.name = data_raw_goods.goods_name
            good.upc = data_raw_goods.upc
            good.icon = data_raw_goods.tz_display_img
            good.width = data_raw_goods.width
            good.height = data_raw_goods.height
            good.depth = data_raw_goods.depth
            good.start_num = data_raw_goods.start_sum
            good.fitting_rows = 1 # 需要挂放几行
            good.is_superimpose = data_raw_goods.is_superimpose
            good.isfitting = data_raw_goods.is_suspension
            good.superimpose_rows = 2 # 叠放几行
            taizhang.calculate_goods_array.append(good)

    # twidth_to_goods 李树
    # 输入：taizhang，
    # 将goods的计算信息填入，同时将twidth_to_goods生成出来
    calculate_goods_info(taizhang)

    # 排列货架 生成陈列
    shelf_display.generate(taizhang)

    return taizhang

def print_taizhang(taizhang,image_dir):
    index = 0
    for shelf in taizhang.shelfs:
        index += 1
        image_path = os.path.join(image_dir,'{}.jpg'.format(index))
        image = np.ones((shelf.width,shelf.height,3),dtype=np.int8)
        image = image*255
        for level in shelf.levels:
            if level.isTrue:
                level_start_height = level.level_start_height
                for good in level.goods:
                    for gooddisplay in good.gooddisplay_inss:
                        point1 = (gooddisplay.left,gooddisplay.top+level_start_height)
                        point2 = (gooddisplay.left+good.width,gooddisplay.top+level_start_height-good.height)
                        cv2.rectangle(image,point1,point2,(0,0,255),2)
                        txt_point = (gooddisplay.left,gooddisplay.top+level_start_height-int(good.height/2))
                        cv2.putText(image, '{}'.format(good.name),txt_point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.imwrite(image_path,image)

if __name__ == "__main__":
    taizhang = generate_displays(806,1142)
    # print(taizhang)
    import os
    with open("1.txt","w") as f:
        f.write(str(taizhang.__str__()))
    image_dir = '/home/src/goodsdl2/media/images/taizhang/{}'.format(taizhang.tz_id)
    from pathlib import Path
    if not Path(image_dir).exists():
        os.makedirs(image_dir)
    print_taizhang(taizhang, image_dir)
