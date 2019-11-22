import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

from goods.shelfdisplay.generate_shelf_dispaly import generate_displays
from goods.shelfdisplay.db_data import init_data

if __name__ == "__main__":
    # taizhang = generate_displays(806, 1187)

    taizhang = generate_displays(806, 1210)


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