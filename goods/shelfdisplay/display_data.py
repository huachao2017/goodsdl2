from django.db import connections
from goods.shelfdisplay.single_algorithm import calculate_shelf_category3_area_ratio
import urllib.request
from django.conf import settings
import os
import numpy as np
import cv2
from goods.shelfdisplay import goods_arrange
from goods.shelfdisplay import shelf_arrange
import datetime
import time
import math
import json


def init_data(uc_shopid, tz_id, base_data):
    taizhang = Taizhang(tz_id)
    cursor = connections['ucenter'].cursor()

    # 获取fx系统的shopid,台账系统的商家mch_id
    cursor.execute("select mch_shop_code,mch_id from uc_shop where id = {}".format(uc_shopid))
    (shopid, mch_id) = cursor.fetchone()

    # 获取台账
    try:
        # cursor.execute(
        #     "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {} and t.id = {}".format(
        #         uc_shopid, tz_id))
        # FIXME 没有指定商店
        cursor.execute(
            "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_taizhang t where t.id = {}".format(tz_id))
        (taizhang_id, shelf_id, count, third_cate_ids) = cursor.fetchone()
        if third_cate_ids is None or third_cate_ids == '':
            raise ValueError('third_cate_ids is None:{},{},{}'.format(taizhang_id,shelf_id,count))
    except:
        print('获取台账失败：{},{}！'.format(uc_shopid, tz_id))
        raise ValueError('taizhang error:{},{}'.format(uc_shopid, tz_id))

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

    # 计算五个值
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
                "select cat_id, name, pid from uc_category where mch_id={} and cat_id='{}' and level=3".format(
                    mch_id, category3))
            (cat_id, name, pid) = cursor.fetchone()
        except:
            print('台账陈列类别无法找到：{}！'.format(category3))
        if cat_id is not None:
            total_height = 0
            for goods in base_data.goods_data_list:
                if goods.category3 == cat_id:
                    total_height += goods.height
                    shelf_goods_data_list.append(goods)
                    if goods.category3 in shelf_category3_to_goods_cnt:
                        shelf_category3_to_goods_cnt[cat_id] += 1
                    else:
                        shelf_category3_to_goods_cnt[cat_id] = 1
            if cat_id in shelf_category3_to_goods_cnt:
                average_height = total_height / shelf_category3_to_goods_cnt[cat_id]
                category3_to_category3_obj[cat_id] = Category3(cat_id, name, pid, average_height)

    # 根据商品筛选三级分类 FIXME 三级分类目前一定是超量的
    print('总共获取的候选陈列商品: ')
    print(shelf_category3_to_goods_cnt)
    if len(shelf_goods_data_list) == 0:
        raise ValueError('no display category:{},{}'.format(uc_shopid, taizhang_id))
    shelf_category3_list = shelf_category3_to_goods_cnt.keys()

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

    # 重新计算货架的三级分类比例
    shelf_category3_area_ratio = calculate_shelf_category3_area_ratio(shelf_category3_list, base_data.category_area_ratio)

    for i in range(count):
        shelf = Shelf(shelf_id, shelf_no, length, height, depth, level_depth_list,
                      shelf_category3_list,
                      shelf_category3_intimate_weight,
                      shelf_category3_level_value,
                      shelf_category3_to_category3_obj,
                      shelf_category3_area_ratio,
                      shelf_goods_data_list)
        taizhang.shelfs.append(shelf)

    cursor.close()
    return taizhang

class Category3:
    def __init__(self, category3, name, pid, average_height):
        self.category3 = category3
        self.name = name
        self.pid = pid
        self.average_height = average_height

class Taizhang:
    def __init__(self, tz_id):
        self.tz_id = tz_id
        self.shelfs = []
        self.image_relative_dir = os.path.join(settings.DETECT_DIR_NAME, 'taizhang',str(self.tz_id))
        self.image_dir = os.path.join(settings.MEDIA_ROOT, self.image_relative_dir)
        self.display_calculate_time = 0
        from pathlib import Path
        if not Path(self.image_dir).exists():
            os.makedirs(self.image_dir)

    def display(self):
        begin_time = time.time()

        # 第三步
        # FIXME 这版仅支持一个货架的台账
        candidate_category_list = shelf_arrange.shelf_arrange(self.shelfs[0])
        self.shelfs[0].candidate_category_list = candidate_category_list

        # 第四步
        goods_arrange.goods_arrange(self.shelfs[0])

        end_time = time.time()
        self.display_calculate_time = int(end_time-begin_time)

    def to_json(self):
        """
        :return:
        {
        taizhang_id:xx
        shelfs:[{
            shelf:xx
            levels:[{
                level_id:xx   #0是底层,1,2,3,4...
                height:xx
                depth:xx
                hole_num:xx
                goods:[{
                    mch_goods_code:
                    upc:
                    width:
                    height:
                    depth:
                    displays:[{
                        top:
                        left:
                        row:
                        col:
                        },
                        {
                        ...
                        }]
                    },
                    {
                    ...
                    }]
                },
                {
                ...
                }]
            },
            {
            ...
            }]
        }
        """
        json_ret = {
            "taizhang_id": self.tz_id,
            "shelfs": []
        }
        for shelf in self.shelfs:
            json_shelf = {
                "shelf_id": shelf.shelf_id,
                "levels": []
            }
            json_ret["shelfs"].append(json_shelf)
            if shelf.best_candidate_shelf is not None:
                index = -1
                for level in shelf.best_candidate_shelf.levels:
                    index += 1
                    if index == len(shelf.best_candidate_shelf.levels)-1:
                        # 最后一层殊处理
                        level_height = shelf.height - level.start_height
                    else:
                        level_height = shelf.best_candidate_shelf.levels[index+1].start_height - level.start_height
                    json_level = {
                        "level_id": level.level_id,
                        "height": level_height,
                        "depth": level.depth,
                        "goods": []
                    }
                    json_shelf["levels"].append(json_level)
                    for display_goods in level.get_left_right_display_goods_list():
                        json_goods = {
                            "mch_good_code": display_goods.goods_data.mch_code,
                            "upc": display_goods.goods_data.upc,
                            "width": display_goods.goods_data.width,
                            "height": display_goods.goods_data.height,
                            "depth": display_goods.goods_data.depth,
                            "displays": []
                        }
                        json_level["goods"].append(json_goods)
                        for goods_display_info in display_goods.get_display_info(level):
                            json_display = {
                                "top": goods_display_info.top,
                                "left": goods_display_info.left,
                                "row": goods_display_info.row,
                                "col": goods_display_info.col,
                            }
                            json_goods["displays"].append(json_display)

                    last_level = level
        return json_ret

    def to_image(self, image_dir):
        index = 0

        # import PIL.ImageFont as ImageFont
        #     fontText = ImageFont.truetype("font/simsun.ttc", 12, encoding="utf-8")

        picurl_to_goods_image = {}
        image_name = None
        now = datetime.datetime.now()
        for shelf in self.shelfs:
            index += 1
            image_name = '{}_{}.jpg'.format(index, now.strftime('%Y%m%d%H%M%S'))
            image_path = os.path.join(image_dir, image_name)
            image = np.ones((shelf.height, shelf.width, 3), dtype=np.int16)
            image = image * 255

            for level in shelf.best_candidate_shelf.levels:
                level_start_height = level.start_height
                for display_goods in level.display_goods_list:
                    picurl = '{}{}'.format(settings.UC_PIC_HOST, display_goods.goods_data.tz_display_img)
                    if picurl in picurl_to_goods_image:
                        goods_image = picurl_to_goods_image[picurl]
                    else:
                        try:
                            goods_image_name = '{}.jpg'.format(display_goods.goods_data.mch_code)
                            goods_image_path = os.path.join(image_dir, goods_image_name)
                            urllib.request.urlretrieve(picurl, goods_image_path)
                            goods_image = cv2.imread(goods_image_path)
                            goods_image = cv2.resize(goods_image,
                                                     (display_goods.goods_data.width, display_goods.goods_data.height))
                        except Exception as e:
                            print('get goods pic error:{}'.format(e))
                            goods_image = None
                        picurl_to_goods_image[picurl] = goods_image

                    for goods_display_info in display_goods.get_display_info(level):
                        point1 = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height))
                        point2 = (goods_display_info.left + display_goods.goods_data.width,
                                  shelf.height - (goods_display_info.top + level_start_height) + display_goods.goods_data.height)
                        # cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                        if goods_image is None:
                            cv2.rectangle(image,point1,point2,(0,0,255),2)
                        else:
                            h = goods_image.shape[0]
                            w = goods_image.shape[1]
                            if point1[1] < 0:
                                if point2[1] < 0:
                                    print('向上整体超出：{},{}'.format(point1,point2))
                                    continue
                                # 上部超出货架
                                if point2[0] > shelf.width:
                                    image[0:point1[1] + h, point1[0]:shelf.width, :] = goods_image[-point1[1]:h, 0:shelf.width-point1[0],:]
                                else:
                                    image[0:point1[1] + h, point1[0]:point1[0] + w, :] = goods_image[-point1[1]:h, 0:w, :]
                            elif point2[0] > shelf.width:
                                if point1[0] > shelf.width:
                                    print('向右整体超出{}：{},{}'.format(shelf.width, point1, point2))
                                    continue
                                # 右侧超出货架
                                image[point1[1]:point1[1]+h, point1[0]:shelf.width,:] = goods_image[0:h, 0:shelf.width-point1[0], :]
                            else:
                                image[point1[1]:point1[1]+h, point1[0]:point1[0]+w,:] = goods_image[0:h, 0:w, :]
                        data_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - 10))
                        cv2.putText(image, '{}'.format(display_goods.get_one_face_max_display_num(level)), data_point,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                        code_txt_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - int(display_goods.goods_data.height / 2)))
                        cv2.putText(image, '{}'.format(display_goods.goods_data.mch_code), code_txt_point,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            cv2.imwrite(image_path, image)
        return image_name # FIXME 只能返回一个货架


class Shelf:
    # 空间常量
    bottom_height = 50  # 底层到地面的高度 # TODO 需考虑初始化
    level_board_height = 20  # 层板高度 # TODO 需考虑初始化
    level_buff_height = 30  # 层冗余高度 # TODO 需考虑初始化
    last_level_min_remain_height = 150  # FIXME 最后一层最小剩余高度，有顶和没有顶需要区分
    average_level_height = 250 # 平均高度，用于计算剩余货架宽度

    extra_add_num = 2  # 每类冗余数量

    def __init__(self, shelf_id, type, width, height, depth, level_depth_list,
                 shelf_category3_list,
                 shelf_category3_intimate_weight,
                 shelf_category3_level_value,
                 shelf_category3_to_category3_obj,
                 shelf_category3_area_ratio,
                 shelf_goods_data_list):
        self.shelf_id = shelf_id
        self.type = type
        self.width = width
        self.height = height
        self.depth = depth

        # 分析货架每层层板的深度
        self.level_depth_list = level_depth_list

        self.shelf_category3_list = shelf_category3_list  # 货架指定分类列表
        self.shelf_category3_intimate_weight = shelf_category3_intimate_weight  # 货架分类涉及的亲密度分值
        self.shelf_category3_level_value = shelf_category3_level_value  # 货架分类涉及的层数分值
        self.shelf_category3_to_category3_obj = shelf_category3_to_category3_obj # 货架分类的详细信息
        self.shelf_category3_area_ratio = shelf_category3_area_ratio  # 货架内分类面积比例
        self.shelf_goods_data_list = shelf_goods_data_list  # 货架候选商品列表

        # 计算用到的参数
        self.candidate_category_list = None
        self.categoryid_to_sorted_goods_list = None  # 候选商品列表
        self.best_candidate_shelf = None

class CandidateShelf:
    def __init__(self, shelf, categoryid_list, categoryid_to_arrange_goods_list):
        self.shelf = shelf
        self.categoryid_list = categoryid_list
        self.categoryid_to_arrange_goods_list = categoryid_to_arrange_goods_list
        self.levels = []
        self.categoryid_to_used_sorted_goods_list = {}
        self.categoryid_to_candidate_sorted_goods_list = {}
        self.badcase_value = 0.0
        self.goods_mean_width = 0

        goods_total_width = 0
        goods_num = 0
        for categoryid in shelf.categoryid_to_sorted_goods_list.keys():
            if len(shelf.categoryid_to_sorted_goods_list[categoryid]) > shelf.extra_add_num:
                self.categoryid_to_used_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[categoryid][
                                                                        :-shelf.extra_add_num]
                self.categoryid_to_candidate_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[
                                                                                 categoryid][-shelf.extra_add_num:]
            else:
                self.categoryid_to_used_sorted_goods_list[categoryid] = shelf.categoryid_to_sorted_goods_list[categoryid]
                self.categoryid_to_candidate_sorted_goods_list[categoryid] = []

            for goods in self.categoryid_to_used_sorted_goods_list[categoryid]:
                goods_num += 1
                goods_total_width += goods.width * (goods.face_num + goods.add_face_num)

        self.goods_mean_width = goods_total_width / goods_num

    def get_real_arrange_goods_list(self, categoryid):
        """
        根据用到商品筛选商品排序表
        :param categoryid:
        :return:
        """
        arrange_goods_list = self.categoryid_to_arrange_goods_list[categoryid]

        used_goods_list = self.categoryid_to_used_sorted_goods_list[categoryid]

        real_arrange_goods_list = []
        for arrange_goods in arrange_goods_list:
            for used_goods in used_goods_list:
                if arrange_goods.mch_code == used_goods.mch_code:
                    real_arrange_goods_list.append(arrange_goods)
                    break

        # print(len(real_arrange_goods_list))
        return real_arrange_goods_list

    def recalculate(self):
        self.levels = []
        self.badcase_value = 0.0

    def calculate_addition_width(self):
        """
        计算货架多余或缺失宽度
        :return: 超出或不足的width
        """

        last_level = self.levels[-1]

        ret = 0
        if self.shelf.height - last_level.start_height < self.shelf.last_level_min_remain_height:
            # 超出层
            ret += last_level.goods_width
            # 只要有层超出就减掉整层宽度
            for i in range(len(self.levels)-2, -1, -1):
                if self.levels[i].start_height > self.shelf.height:
                    ret += self.shelf.width
        else:
            ret -= self.shelf.width - last_level.goods_width
            # 货架高度剩余很多就加一个货架宽度
            if (self.shelf.height - last_level.start_height) > last_level.goods_height + self.shelf.level_buff_height + self.shelf.level_board_height + self.shelf.last_level_min_remain_height:
                ret -= self.shelf.width
            # 空缺宽度

        return ret


class Level:
    def __init__(self, candidate_shelf, level_id, start_height, is_left_right_direction):
        self.candidate_shelf = candidate_shelf  # 候选货架
        self.level_id = level_id  # 层id
        self.is_left_right_direction = is_left_right_direction  # True从左向右，False从右向左
        self.goods_width = 0   # 层宽度
        self.depth = candidate_shelf.shelf.depth
        if len(candidate_shelf.shelf.level_depth_list) > 0:
            # 用层板深度设值
            if self.level_id < len(candidate_shelf.shelf.level_depth_list):
                self.depth = candidate_shelf.shelf.level_depth_list[self.level_id]
            else:
                self.depth = candidate_shelf.shelf.level_depth_list[-1]
        self.start_height = start_height
        self.goods_height = 0 # 商品最高高度
        candidate_shelf.levels.append(self)
        self.display_goods_list = []  # 陈列商品集合

    def display_goods(self, display_goods):
        # 动态计算展示商品的排面
        display_goods.calculate_face_num(self)
        if display_goods.get_width() + self.goods_width > self.candidate_shelf.shelf.width:
            # TODO 需要考虑拆分
            addition_width = display_goods.get_width() + self.goods_width - self.candidate_shelf.shelf.width
            if addition_width > int(display_goods.goods_data.width/5):
                # 可以超出一些货架，超出商品宽的1/5则失败
                return False
        self.display_goods_list.append(display_goods)

        # 更新宽度
        self.goods_width += display_goods.get_width()

        # 更新高度
        if self.goods_height < display_goods.get_height():
            self.goods_height = display_goods.get_height()

        return True

    def get_nono_goods_width(self):
        return self.candidate_shelf.shelf.width - self.goods_width

    def get_left_right_display_goods_list(self):
        if self.is_left_right_direction:
            return self.display_goods_list
        else:
            return self.display_goods_list[::-1]

    def __str__(self):
        ret = str(self.level_id)
        ret += ','
        ret += str(self.start_height)
        ret += ','
        ret += str(self.goods_width)
        return ret


class DisplayGoods:
    def __init__(self, goods_data):
        self.goods_data = goods_data

    def calculate_face_num(self, level):
        """
        扩面处理 n*psd/最大成列量（初始n默认为3）
        :param level:
        :return:
        """
        # 考虑叠放
        if self.goods_data.is_superimpose == 1:
            self.goods_data.superimpose_num = math.floor(level.candidate_shelf.shelf.average_level_height/self.goods_data.height)
            if self.goods_data.superimpose_num > 4:
                self.goods_data.superimpose_num = 4
        # 计算商品的单face最大陈列量
        max_one_face = int(level.depth / self.goods_data.depth) * self.goods_data.superimpose_num
        if max_one_face == 0:
            max_one_face = self.goods_data.superimpose_num
        self.goods_data.face_num = math.ceil(3 * self.goods_data.psd / max_one_face)

    def get_width(self):
        return self.goods_data.width * (self.goods_data.face_num + self.goods_data.add_face_num)

    def get_height(self):
        return self.goods_data.height * self.goods_data.superimpose_num

    def get_one_face_max_display_num(self, level):
        max_one_face = int(level.depth / self.goods_data.depth)
        if max_one_face == 0:
            max_one_face = 1
        return max_one_face

    def get_display_info(self, level):
        """
        :return:GoodsDisplayInfo列表
        """
        display_goods_info = []
        display_goods_list = level.get_left_right_display_goods_list()
        init_top = self.goods_data.height
        init_left = 0
        for display_goods in display_goods_list:
            if self.goods_data.equal(display_goods.goods_data):
                break
            init_left += display_goods.get_width()
        for i in range(self.goods_data.face_num+self.goods_data.add_face_num):
            for j in range(self.goods_data.superimpose_num):
                col = i
                row = j
                top = init_top + j * self.goods_data.height
                left = init_left + i * self.goods_data.width
                display_goods_info.append(DisplayOneGoodsInfo(col, row, top, left))

        return display_goods_info


class DisplayOneGoodsInfo:
    def __init__(self, col, row, top, left):
        self.col = col  # 在level上的列
        self.row = row  # 行
        self.top = top
        self.left = left


# if __name__ == "__main__":
#     from goods.shelfdisplay import db_data
#
#     base_data = db_data.init_data(806)
#
#     taizhang = init_data(806, 1198, base_data)
#     print(taizhang.to_json())
