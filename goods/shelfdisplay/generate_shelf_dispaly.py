from goods.shelfdisplay import db_data
from goods.shelfdisplay import display_data
from goods.models import ShelfDisplayDebug
import json
import traceback
import os


def generate_displays(uc_shopid, tz_id):
    """
    :param uc_shopid:
    :param tz_id:
    :return: taizhang对象
    """

    print("begin generate_displays:{},{}".format(uc_shopid, tz_id))

    # 初始化基础数据
    base_data = db_data.init_data(uc_shopid)

    shelf_display_debug_model = ShelfDisplayDebug.objects.create(
        tz_id=tz_id
    )

    try:
        # 初始化台账数据
        taizhang = display_data.init_data(uc_shopid, tz_id, base_data)
        taizhang.display()
        # 打印陈列图
        try:
            image_name = taizhang.to_image(taizhang.image_dir)
            shelf_display_debug_model.display_source = os.path.join(taizhang.image_relative_dir, image_name)
        except Exception as e:
            print('陈列图生成错误：{}'.format(e))
            traceback.print_exc()
        shelf_display_debug_model.json_ret = json.dumps(taizhang.to_json())
        shelf_display_debug_model.save()
        print("Success:{},{}".format(uc_shopid, tz_id))
        return taizhang
    except Exception as e:
        shelf_display_debug_model.json_ret = str(e)
        shelf_display_debug_model.save()
        print("Failed:{},{}".format(uc_shopid, tz_id))
        return None
