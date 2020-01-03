import argparse
import sys
import main.import_django_settings
from django.db import connections
from django.db import close_old_connections

from goods.shelfdisplay.generate_shelf_display import generate_displays


def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--shopid', type=int, help='ucenter shop id', default=806)
    parser.add_argument('--tzid', type=int,
                        help='taizhang id', default=1199)
    parser.add_argument('--batchid', type=str,
                        help='batch id', default='TEST_20200102172630')
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    # taizhang = generate_displays(806, 1187)


    cursor = connections['ucenter'].cursor()
    cursor.execute(
        "select id from sf_taizhang_display where taizhang_id={} and status in (1,2,3) and approval_status=1 order by start_datetime desc limit 1".format(
            args.tzid))
    (old_display_id,) = cursor.fetchone()
    cursor.close()
    taizhang = generate_displays(args.shopid, args.tzid, args.batchid, old_display_id)
    print(taizhang.best_candidate_shelf)



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