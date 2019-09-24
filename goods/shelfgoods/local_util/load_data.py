# from goods.shelfgoods.utils import mysql_util
from goods.shelfgoods.utils import django_mysql_util
from goods.shelfgoods.sql import taizhang,ai
from goods.shelfgoods.local_util import parse_util
import os
from django.conf import settings
import logging
logger = logging.getLogger("detect")
import cv2
class LoadData:

    def get_tz_dispaly_goods(self,display_id):
        # mysql_ins  = mysql_util.MysqlUtil("taizhang")
        mysql_ins = django_mysql_util.DjangoMysql("ucenter")
        try:
            sql = taizhang.get_display_good
            #TODO 对sql传参
            sql = sql.format(display_id)
            result=mysql_ins.selectOne(sql)
            display_info = result[0]
            shelf_floor_upc = parse_util.parse_tz_display_goods(display_info)
            mysql_ins.close()
            return shelf_floor_upc
        except Exception as e :
            logger.error("get_tz_dispaly_goods failed  , display_id="+str(display_id))
            logger.error(e)
            mysql_ins.close()
            return None


    def get_ai_goods(self,shelf_image_id):
        # mysql_ins = mysql_util.MysqlUtil("ai")
        mysql_ins = django_mysql_util.DjangoMysql("default")
        try:
            sql = ai.get_shelf_goods
            sql = sql.format(shelf_image_id)
            results = mysql_ins.selectAll(sql)
            box_id = []
            shelf_img_id = []
            xmin, ymin, xmax, ymax = [],[],[],[]
            level = []
            for row in list(results):
                box_id.append(int(row[0]))
                shelf_img_id.append(int(row[1]))
                xmin.append(int(row[2]))
                ymin.append(int(row[3]))
                xmax.append(int(row[4]))
                ymax.append(int(row[5]))
                level.append(int(row[6]))
            # #对level 做一致性处理  （陈列从下往上， 这里是从上往下）
            # max_level = max(level)
            # new_level = []
            # for lv in level:
            #     new_level.append(max_level-lv)
            mysql_ins.close()
            if (len(shelf_img_id))>0:
                shelf_img = self.get_ai_shelf_img(shelf_img_id[0])
                return box_id, shelf_img_id, xmin, ymin, xmax, ymax, level,shelf_img
        except Exception as e:
            logger.error("get_ai_goods failed ,shelf_image_id="+str(shelf_image_id))
            logger.error(e)
            return None,None,None,None,None,None,None,None
    def get_ai_shelf_img(self,shelf_img_idi):
        mysql_ins = django_mysql_util.DjangoMysql('default')
        try:
            sql = ai.get_shelf_img.format(int(shelf_img_idi))
            result = mysql_ins.selectOne(sql)
            print(result[0])
            img_file = os.path.join(settings.MEDIA_ROOT, str(result[0]))
            if os.path.isfile(img_file) == False:
                logger.error("LoadData get_ai_shelf_img is Null , shelf_img_path = "+str(img_file))
                return None
            shelf_img = cv2.imread(img_file)
            mysql_ins.close()
            return shelf_img
        except Exception as e:
            logger.error("get_ai_shelf_img failed ,shelf_img_idi="+str(shelf_img_idi))
            logger.error(e)
            mysql_ins.close()
            return None




