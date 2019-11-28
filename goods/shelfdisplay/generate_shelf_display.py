from goods.shelfdisplay import db_data
from goods.shelfdisplay import display_data
from goods.models import ShelfDisplayDebug, AllWorkFlowBatch
import json
import traceback
import os
import time
from django.db import connections
import requests


def generate_workflow_displays(uc_shopid, batch_id):
    try:
        workflow = AllWorkFlowBatch.objects.filter(uc_shopid=uc_shopid).filter(batch_id=batch_id).filter(auto_display_status=1).get()
    except:
        print('没有需要计算的workflow：{},{}'.format(uc_shopid, batch_id))
        raise ValueError('workflow error:{},{}'.format(uc_shopid, batch_id))

    cursor = connections['ucenter'].cursor()
    # 获取台账
    try:
        # FIXME 只获取有指定三级分类的台账
        cursor.execute(
            "select t.id from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.third_cate_ids != ''".format(
                uc_shopid))
        taizhangs = cursor.fetchall()
    except:
        print('获取台账失败：{}！'.format(uc_shopid))
        raise ValueError('taizhang error:{}'.format(uc_shopid))
    cursor.close()

    # 计算陈列
    begin_time = time.time()
    taizhang_display_list = []
    for one_tz_id in taizhangs:
        taizhang_display = generate_displays(uc_shopid, one_tz_id[0], batch_id)
        if taizhang_display is not None:
            taizhang_display_list.append(taizhang_display)
    end_time = time.time()
    auto_display_calculate_time = int(end_time-begin_time)

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

    # 更新workflow
    workflow.auto_display_status = 3
    workflow.auto_display_calculate_time = auto_display_calculate_time
    workflow.save()


def generate_displays(uc_shopid, tz_id, batch_id = 0):
    """
    :param uc_shopid:
    :param tz_id:
    :return: taizhang对象
    """

    print("begin generate_displays:{},{},{}".format(uc_shopid, tz_id, batch_id))

    # 初始化基础数据
    base_data = db_data.init_data(uc_shopid)

    shelf_display_debug_model = ShelfDisplayDebug.objects.create(
        uc_shopid=uc_shopid,
        batch_id=batch_id,
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
        shelf_display_debug_model.calculate_time = taizhang.display_calculate_time
        shelf_display_debug_model.save()
        print("Success:{},{}".format(uc_shopid, tz_id))
        return taizhang
    except Exception as e:
        shelf_display_debug_model.json_ret = str(e)
        shelf_display_debug_model.save()
        print("Failed:{},{},{}".format(uc_shopid, tz_id, batch_id))
        return None
