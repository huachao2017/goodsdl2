import json

from django.db import connections

from goods.shelfdisplay.db_data import Category3
from goods.shelfdisplay.firstdisplay.display_taizhang import TaizhangDisplay, Shelf


def init_display_data(uc_shopid, tz_id, base_data):
    """
    初始化陈列相关的台账、货架、指定分类数据，最终生成初始化好的taizhang_display对象
    :param uc_shopid: ucentor系统shopid
    :param tz_id:
    :param base_data:
    :return: taizhang_display对象
    """
    taizhang_display = TaizhangDisplay(tz_id)
    cursor = connections['ucenter'].cursor()

    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账信息
    try:
        # cursor.execute(
        #     "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.id = {}".format(
        #         uc_shopid, tz_id))
        # FIXME 没有指定商店
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_taizhang t where t.id = {}".format(tz_id))
        (taizhang_id, shelf_id, count, third_cate_ids) = cursor.fetchone()
        if third_cate_ids is None or third_cate_ids == '':
            raise ValueError('third_cate_ids is None:{},{},{}'.format(taizhang_id, shelf_id, count))
    except:
        print('获取台账失败：{},{}！'.format(uc_shopid, tz_id))
        cursor.close()
        raise ValueError('taizhang_display error:{},{}'.format(uc_shopid, tz_id))

    # 获取货架信息
    cursor.execute(
        "select t.shelf_no,s.length,s.height,s.depth,s.hole_height,s.hole_distance,s.option from sf_shelf s, sf_shelf_type t where s.shelf_type_id=t.id and s.id={}".format(
            shelf_id))
    (shelf_no, length, height, depth, hole_height, hole_distance, option) = cursor.fetchone()
    level_depth_list = []
    try:
        shelf_levels_option = json.loads(option)
        for one_level_option in shelf_levels_option:
            if 'floor_depth' in one_level_option:
                level_depth_list.append(int(one_level_option['floor_depth']))
    except:
        print('货架层信息不合法：{}！'.format(option))
        level_depth_list = []

    # 准备陈列需要的数据
    display_category3_list = third_cate_ids.split(',')
    display_category3_list = list(set(display_category3_list))
    category3_to_category3_obj = {}
    shelf_category3_to_goods_cnt = {}
    shelf_goods_data_list = []
    # 检查所有三级分类
    for category3 in display_category3_list:
        cat_id = None
        try:
            cursor.execute(
                "select cat_id, name, pid from ao_display_category where mch_id={} and cat_id='{}' and level=3".format(
                    mch_id, category3))
            (cat_id, name, pid) = cursor.fetchone()
        except:
            print('台账陈列类别无法找到：{}！'.format(category3))

        # FIXME 目前只支持cat_id是字符串
        cat_id = str(cat_id)
        if cat_id is not None:
            total_height = 0
            # 筛选商品
            for goods in base_data.goods_data_list:
                if goods.category3 == cat_id and goods.goods_role != 2: # 删除品需要去掉
                    total_height += goods.height
                    shelf_goods_data_list.append(goods)
                    if goods.category3 in shelf_category3_to_goods_cnt:
                        shelf_category3_to_goods_cnt[cat_id] += 1
                    else:
                        shelf_category3_to_goods_cnt[cat_id] = 1
            # 生成Category3对象数据
            if cat_id in shelf_category3_to_goods_cnt:
                average_height = total_height / shelf_category3_to_goods_cnt[cat_id]
                category3_to_category3_obj[cat_id] = Category3(cat_id, name, pid, average_height)

    # 根据商品筛选三级分类 FIXME 三级分类目前一定是超量的
    print('总共获取的候选陈列商品: {}'.format(len(shelf_goods_data_list)))
    print(shelf_category3_to_goods_cnt)

    if len(shelf_goods_data_list) == 0:
        raise ValueError('no any display goods')
    shelf_goods_data_list.sort(key=lambda x: x.mch_code)
    for goods_data in shelf_goods_data_list:
        print(goods_data)

    shelf_category3_list = list(shelf_category3_to_goods_cnt.keys())
    shelf_category3_list.sort()
    print('总共需要陈列的分类: {}'.format(len(shelf_category3_list)))
    print(shelf_category3_list)

    shelf_category3_intimate_weight, shelf_category3_level_value, shelf_category3_to_category3_obj = filter_to_shelf_data(
        base_data, shelf_category3_list, category3_to_category3_obj)

    # 重新计算货架的三级分类比例
    shelf_category3_area_ratio = calculate_shelf_category3_area_ratio(shelf_category3_list,
                                                                      base_data.category_area_ratio)

    # TODO 需要支持多个货架
    for i in range(count):
        shelf = Shelf(shelf_id, shelf_no, length, height, depth, level_depth_list,
                      shelf_category3_list,
                      shelf_category3_intimate_weight,
                      shelf_category3_level_value,
                      shelf_category3_to_category3_obj,
                      shelf_category3_area_ratio,
                      shelf_goods_data_list)
        taizhang_display.shelfs.append(shelf)

    cursor.close()
    return taizhang_display


def filter_to_shelf_data(base_data, shelf_category3_list, category3_to_category3_obj):
    """
    根据shelf_category3_list重新生成shelf相关的亲密度、上下层关系和三级分类字典对象
    :param base_data:
    :param shelf_category3_list:
    :param category3_to_category3_obj:
    :return:shelf_category3_intimate_weight, shelf_category3_level_value, shelf_category3_to_category3_obj
    """
    shelf_category3_intimate_weight = {}
    shelf_category3_level_value = {}
    shelf_category3_to_category3_obj = {}
    for category3 in shelf_category3_list:
        for category3_list_str in base_data.category3_intimate_weight.keys():
            # 做部分删减
            category3_list = category3_list_str.split(',')
            if category3 in category3_list:
                shelf_category3_intimate_weight[category3_list_str] = base_data.category3_intimate_weight[
                    category3_list_str]
        if category3 in base_data.category3_level_value:
            shelf_category3_level_value[category3] = base_data.category3_level_value[category3]
        if category3 in category3_to_category3_obj:
            shelf_category3_to_category3_obj[category3] = category3_to_category3_obj[category3]

    return shelf_category3_intimate_weight, shelf_category3_level_value, shelf_category3_to_category3_obj


def calculate_shelf_category3_area_ratio(categoryid_list, category_area_ratio):
    """
    计算出本货架的比例
    :param shelf:
    :param categoryid_list:
    :param category_area_ratio:
    :return: 修正的category_area_ratio
    """

    shelf_category3_area_ratio = {}
    total_ratio = 0.0
    ratio_valid = True  #
    for categoryid in categoryid_list:
        if categoryid not in category_area_ratio:
            ratio_valid = False
            print('error: category_area_ratio data is not valid!')
            break
        total_ratio += category_area_ratio[categoryid]

    if ratio_valid:
        for categoryid in categoryid_list:
            shelf_category3_area_ratio[categoryid] = category_area_ratio[categoryid] / total_ratio
    else:
        # FIXME 如果分类面积比例是无效的，则每个类平均分配货架
        for categoryid in categoryid_list:
            shelf_category3_area_ratio[categoryid] = 1 / len(categoryid_list)

    return shelf_category3_area_ratio