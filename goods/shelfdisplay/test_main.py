import os
import sys
import argparse
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from goods.shelfdisplay.generate_shelf_display import generate_displays
from goods.shelfdisplay.db_data import init_data

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--shopid', type=int, help='ucenter shop id', default=806)
    parser.add_argument('--tzid', type=int,
                        help='taizhang id', default=1203)
    parser.add_argument('--batchid', type=str,
                        help='batch id', default='TEST_20191127064522')
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    # taizhang = generate_displays(806, 1187)

    taizhang = generate_displays(args.shopid, args.tzid, args.batchid)


    # category_area_ratio: 分类陈列面积比例表
    # category3_intimate_weight: 三级分类亲密度
    # category3_level_value: 三级分类层数分值
    # goods_data_list: GoodsData列表
    # base_data = init_data(806)
    # print(base_data.category_area_ratio)
    # print(base_data.category3_intimate_weight)
    # print(base_data.category3_level_value)
    # for goods in base_data.goods_data_list:
    #     print(goods)