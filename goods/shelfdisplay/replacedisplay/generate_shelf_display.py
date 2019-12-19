"""
生成台账的入口，提供两种入口：
1、通过一个流程的批次进入generate_workflow_displays
2、指定一个批次的台账generate_displays

陈列需要批次是因为依赖于选品，选品目前是通过店号和批次去获取
"""
from goods.shelfdisplay import db_data
from goods.models import ShelfDisplayDebug
import json
import traceback
import os
from django.db import connections

def generate_workflow_displays(uc_shopid, batch_id):
    """
    自动陈列一个批次流程的所有台账
    :param uc_shopid: ucentor的shopid
    :param batch_id: 流程的批次号
    :return:
    """
    cursor = connections['ucenter'].cursor()
    # 获取台账
    try:
        cursor.execute(
            "select t.id from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {}".format(
                uc_shopid))
        taizhangs = cursor.fetchall()
    except:
        traceback.print_exc()
        print('获取台账失败：{}！'.format(uc_shopid))
        raise ValueError('taizhang error:{}'.format(uc_shopid))
    finally:
        cursor.close()

    # 计算陈列
    taizhang_display_list = []
    for one_tz_id in taizhangs:
        taizhang_display = generate_displays(uc_shopid, one_tz_id[0], batch_id)
        if taizhang_display is not None:
            taizhang_display_list.append(taizhang_display)


def generate_displays(uc_shopid, tz_id, batch_id):
    """
    自动陈列一个批次流程的指定台账
    :param uc_shopid: ucentor的shopid
    :param tz_id: 台账id
    :return: taizhang_display对象，如果为None则说明生成失败
    """

    print("begin generate_displays:{},{},{}".format(uc_shopid, tz_id, batch_id))

    # 初始化基础数据
    base_data = db_data.init_base_data(uc_shopid, batch_id)

    # 创建陈列在ai系统的数据记录
    shelf_display_debug_model = ShelfDisplayDebug.objects.create(
        uc_shopid=uc_shopid,
        batch_id=batch_id,
        tz_id=tz_id
    )

    try:
        # 初始化台账数据 TODO
        taizhang_display = db_data.init_display_data(uc_shopid, tz_id, base_data)
        taizhang_display.display()
        # 打印陈列图
        try:
            image_name = taizhang_display.to_image(taizhang_display.image_dir)
            shelf_display_debug_model.display_source = os.path.join(taizhang_display.image_relative_dir, image_name)
        except Exception as e:
            print('陈列图生成错误：{}'.format(e))
            traceback.print_exc()
        # 更新陈列在ai系统的数据记录
        shelf_display_debug_model.json_ret = json.dumps(taizhang_display.to_json())
        shelf_display_debug_model.calculate_time = taizhang_display.display_calculate_time
        shelf_display_debug_model.save()
        print("Success:{},{}".format(uc_shopid, tz_id))
        return taizhang_display
    except Exception as e:
        # 更新陈列在ai系统的数据记录
        shelf_display_debug_model.json_ret = str(e)
        shelf_display_debug_model.save()
        traceback.print_exc()
        print("Failed:{},{},{}".format(uc_shopid, tz_id, batch_id))
        return None
