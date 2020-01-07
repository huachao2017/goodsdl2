"""
生成台账的入口，提供两种入口：
1、通过一个流程的批次进入generate_workflow_displays
2、指定一个批次的台账generate_displays

陈列需要批次是因为依赖于选品，选品目前是通过店号和批次去获取
"""
import json
import os
import traceback

from django.db import connections
from django.db import close_old_connections

from goods.models import ShelfDisplayDebug
from goods.shelfdisplay import db_data
from goods.shelfdisplay.firstdisplay import db_display_data as first_db_display_data
from goods.shelfdisplay.replacedisplay import db_display_data as replace_db_display_data
from goods.third_tools import dingtalk

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
        # FIXME 只获取有指定三级分类的台账
        cursor.execute(
            "select t.id, t.shelf_id from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.third_cate_ids != ''".format(
                uc_shopid))
        taizhangs = cursor.fetchall()
    except:
        msg = '获取台账失败：{}！'.format(uc_shopid)
        print(msg)
        dingtalk.send_message(msg)
        raise ValueError(msg)
    finally:
        cursor.close()

    # 计算陈列
    taizhang_display_list = []
    for one_tz_id in taizhangs:
        # 获取上次陈列
        old_display_id = None
        close_old_connections()
        cursor = connections['ucenter'].cursor()
        try:
            cursor.execute(
                "select id from sf_taizhang_display where taizhang_id={} and status in (1,2,3) and approval_status=1 order by start_datetime desc limit 1".format(
                    one_tz_id[0]))
            (old_display_id,) = cursor.fetchone()
        except Exception as e:
            # traceback.print_exc()
            print("没有找到已有陈列:{}".format(one_tz_id[0]))
        finally:
            cursor.close()

        generate_displays(uc_shopid, one_tz_id[0], batch_id, old_display_id)

    # 通知台账系统
    # url = "https://autodisplay:xianlife2018@taizhang.aicvs.cn/api/autoDisplay"
    # headers = {
    #     "Accept": "application/json",
    #     "Content-Type": "application/json"
    # }
    # for taizhang_display in taizhang_display_list:
    #     json_info = json.dumps(taizhang_display.to_json())
    #     data = bytes(json_info, 'utf8')
    #     resp = requests.post(url=url, data=data, headers=headers)
    #     print('通知台账系统：'.format(resp))



def generate_displays(uc_shopid, tz_id, batch_id, old_display_id = None):
    """
    自动陈列一个批次流程的指定台账
    :param uc_shopid: ucentor的shopid
    :param tz_id: 台账id
    :return: taizhang_display对象，如果为None则说明生成失败
    """

    if old_display_id is None:
        print("begin generate_first_displays:{},{},{}".format(uc_shopid, tz_id, batch_id))
    else:
        print("begin generate_replace_displays:{},{},{},{}".format(uc_shopid, tz_id, batch_id, old_display_id))

    close_old_connections()

    # 初始化基础数据
    base_data = db_data.init_base_data(uc_shopid, batch_id)

    # 创建陈列在ai系统的数据记录
    shelf_display_debug_model = ShelfDisplayDebug.objects.create(
        uc_shopid=uc_shopid,
        batch_id=batch_id,
        tz_id=tz_id
    )

    try:
        # 初始化台账数据
        if old_display_id is None:
            taizhang_display = first_db_display_data.init_display_data(uc_shopid, tz_id, base_data)
        else:
            taizhang_display = replace_db_display_data.init_display_data(uc_shopid, tz_id, old_display_id, base_data)
        taizhang_display.display()
        # 打印陈列图
        try:
            image_name = taizhang_display.to_image(taizhang_display.image_dir)
            shelf_display_debug_model.display_source = os.path.join(taizhang_display.image_relative_dir, image_name)

            image_old_name = taizhang_display.to_old_image(taizhang_display.image_dir)
            if image_old_name is not None:
                shelf_display_debug_model.old_display_source = os.path.join(taizhang_display.image_relative_dir, image_old_name)
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
