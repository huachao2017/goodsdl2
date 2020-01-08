"""
台账陈列的主体对象结构：
TaizhangDisplay ->* Shelf -> BestCandidateShelf
CandidateShelf ->* Level ->* DisplayGoods ->* DisplayOneGoodsInfo（只在BestCandidateShelf这个对象生成）
"""
import datetime
import math
import os
import time
import urllib.request

import cv2
import numpy as np
from django.conf import settings

from goods.shelfdisplay.replacedisplay.display_object import Shelf
from goods.shelfdisplay.replacedisplay.area_arrange import AreaManager


class TaizhangDisplay:
    def __init__(self, tz_id):
        self.tz_id = tz_id
        self.shelf = None
        self.category3_list = None    # 三级分类列表
        self.choose_goods_list = None # 筛选过三级分类选品列表
        self.best_candidate_shelf = None
        self.image_relative_dir = os.path.join(settings.DETECT_DIR_NAME, 'taizhang', str(self.tz_id))
        self.image_dir = os.path.join(settings.MEDIA_ROOT, self.image_relative_dir)
        self.display_calculate_time = 0
        from pathlib import Path
        if not Path(self.image_dir).exists():
            os.makedirs(self.image_dir)

    def init_data(self, shelf, category3_list, choose_goods_list):
        self.shelf = shelf
        self.category3_list = category3_list
        self.choose_goods_list = choose_goods_list

    def display(self):
        """
        陈列主算法
        :return:
        """
        begin_time = time.time()

        print(self.shelf)

        # 区域处理
        levelid_to_displaygoods_list = {}
        for level in self.shelf.levels:
            levelid_to_displaygoods_list[level.level_id] = level.display_goods_list
        area_manager = AreaManager(self.shelf,
                                   levelid_to_displaygoods_list,
                                   self.choose_goods_list)

        self.best_candidate_shelf = area_manager.calculate_candidate_shelf()

        end_time = time.time()
        self.display_calculate_time = int(end_time - begin_time)


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
                    layout:
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
        shelf = self.best_candidate_shelf
        json_shelf = {
            "shelf_id": shelf.shelf_id,
            "levels": []
        }
        json_ret["shelfs"].append(json_shelf)
        if shelf is not None:
            for level in shelf.levels:
                json_level = {
                    "level_id": level.level_id,
                    "height": level.height,
                    "depth": level.depth,
                    "goods": []
                }
                json_shelf["levels"].append(json_level)
                for display_goods in level.display_goods_list:
                    if display_goods.goods_data.mch_code == '':
                        # 增加占位goods的处理
                        continue
                    json_goods = {
                        "mch_good_code": display_goods.goods_data.mch_code,
                        "upc": display_goods.goods_data.upc,
                        "width": display_goods.goods_data.width,
                        "height": display_goods.goods_data.height,
                        "depth": display_goods.goods_data.depth,
                        "p_width": display_goods.goods_data.width,
                        "p_height": display_goods.goods_data.height,
                        "p_depth": display_goods.goods_data.depth,
                        "layout": display_goods.goods_data.layout,
                        "displays": []
                    }
                    json_level["goods"].append(json_goods)
                    num = 0
                    for goods_display_info in display_goods.get_display_info(level):
                        num += 1
                        json_display = {
                            "top": goods_display_info.top,
                            "left": goods_display_info.left,
                            "row": goods_display_info.row,
                            "col": goods_display_info.col,
                        }
                        json_goods["displays"].append(json_display)

                    json_goods["max_display_num"] = display_goods.get_one_face_max_display_num(level) * num

        return json_ret

    def to_image(self, image_dir):

        # import PIL.ImageFont as ImageFont
        #     fontText = ImageFont.truetype("font/simsun.ttc", 12, encoding="utf-8")

        picurl_to_goods_image = {}
        image_name = None
        now = datetime.datetime.now()
        shelf = self.best_candidate_shelf
        image_name = 'new_{}.jpg'.format(now.strftime('%Y%m%d%H%M%S'))
        image_path = os.path.join(image_dir, image_name)
        image = np.ones((shelf.height, shelf.width, 3), dtype=np.int16)
        image = image * 255
        last_level = None
        level_height = 0
        for level in shelf.levels:
            if last_level is None:
                level_height += 30
            else:
                level_height += last_level.height
            level_start_height = level_height
            last_level = level
            for display_goods in level.display_goods_list:
                if display_goods.goods_data.mch_code == '':
                    # 增加占位goods的处理
                    continue
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
                              shelf.height - (
                              goods_display_info.top + level_start_height) + display_goods.goods_data.height)
                    # cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                    if goods_image is None:
                        cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                    else:
                        h = goods_image.shape[0]
                        w = goods_image.shape[1]
                        if point1[1] < 0:
                            if point2[1] < 0:
                                print('向上整体超出：{},{}'.format(point1, point2))
                                continue
                            # 上部超出货架
                            if point2[0] > shelf.width:
                                image[0:point1[1] + h, point1[0]:shelf.width, :] = goods_image[-point1[1]:h,
                                                                                   0:shelf.width - point1[0], :]
                            else:
                                image[0:point1[1] + h, point1[0]:point1[0] + w, :] = goods_image[-point1[1]:h, 0:w, :]
                        elif point2[0] > shelf.width:
                            if point1[0] > shelf.width:
                                print('向右整体超出{}：{},{}'.format(shelf.width, point1, point2))
                                continue
                            # 右侧超出货架
                            image[point1[1]:point1[1] + h, point1[0]:shelf.width, :] = goods_image[0:h,
                                                                                       0:shelf.width - point1[0], :]
                        else:
                            image[point1[1]:point1[1] + h, point1[0]:point1[0] + w, :] = goods_image[0:h, 0:w, :]
                    data_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - 10))
                    cv2.putText(image, '{}:{}-{}'.format(goods_display_info.row, goods_display_info.col,
                                                         display_goods.get_one_face_max_display_num(level)), data_point,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    code_txt_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - int(display_goods.goods_data.height / 2)))
                    cv2.putText(image, '{}'.format(display_goods.goods_data.mch_code), code_txt_point,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.imwrite(image_path, image)
        return image_name  # FIXME 只能返回一个货架

    def to_old_image(self, image_dir):

        # import PIL.ImageFont as ImageFont
        #     fontText = ImageFont.truetype("font/simsun.ttc", 12, encoding="utf-8")

        picurl_to_goods_image = {}
        image_name = None
        now = datetime.datetime.now()
        shelf = self.shelf
        image_name = 'old_{}.jpg'.format(now.strftime('%Y%m%d%H%M%S'))
        image_path = os.path.join(image_dir, image_name)
        image = np.ones((shelf.height, shelf.width, 3), dtype=np.int16)
        image = image * 255
        last_level = None
        level_height = 0
        for level in shelf.levels:
            if last_level is None:
                level_height += 30
            else:
                level_height += last_level.height
            level_start_height = level_height
            last_level = level
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
                              shelf.height - (
                              goods_display_info.top + level_start_height) + display_goods.goods_data.height)
                    # cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                    if goods_image is None:
                        cv2.rectangle(image, point1, point2, (0, 0, 255), 2)
                    else:
                        h = goods_image.shape[0]
                        w = goods_image.shape[1]
                        if point1[1] < 0:
                            if point2[1] < 0:
                                print('向上整体超出：{},{}'.format(point1, point2))
                                continue
                            # 上部超出货架
                            if point2[0] > shelf.width:
                                image[0:point1[1] + h, point1[0]:shelf.width, :] = goods_image[-point1[1]:h,
                                                                                   0:shelf.width - point1[0], :]
                            else:
                                image[0:point1[1] + h, point1[0]:point1[0] + w, :] = goods_image[-point1[1]:h, 0:w, :]
                        elif point2[0] > shelf.width:
                            if point1[0] > shelf.width:
                                print('向右整体超出{}：{},{}'.format(shelf.width, point1, point2))
                                continue
                            # 右侧超出货架
                            image[point1[1]:point1[1] + h, point1[0]:shelf.width, :] = goods_image[0:h,
                                                                                       0:shelf.width - point1[0], :]
                        else:
                            image[point1[1]:point1[1] + h, point1[0]:point1[0] + w, :] = goods_image[0:h, 0:w, :]
                    data_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - 10))
                    cv2.putText(image, '{}:{}-{}'.format(goods_display_info.row, goods_display_info.col,
                                                         display_goods.get_one_face_max_display_num(level)), data_point,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    code_txt_point = (goods_display_info.left, shelf.height - (
                        goods_display_info.top + level_start_height - int(display_goods.goods_data.height / 2)))
                    cv2.putText(image, '{}'.format(display_goods.goods_data.mch_code), code_txt_point,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        cv2.imwrite(image_path, image)
        return image_name  # FIXME 只能返回一个货架


# if __name__ == "__main__":
#     from goods.shelfdisplay import db_data
#
#     base_data = db_data.init_data(806)
#
#     taizhang = init_data(806, 1198, base_data)
#     print(taizhang.to_json())
