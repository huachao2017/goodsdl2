# from goods.shelfgoods.utils import mysql_util
from goods.shelfgoods.utils import django_mysql_util
from goods.shelfgoods.sql import taizhang,ai
from goods.shelfgoods.local_util import parse_util
import os
from django.conf import settings
import logging
import traceback

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
            logger.error(traceback.format_exc())
            mysql_ins.close()
            return None

    def get_ai_goods(self,shelf_image_id):
        # mysql_ins = mysql_util.MysqlUtil("ai")
        mysql_ins = django_mysql_util.DjangoMysql("default")
        try:
            sql = ai.get_shelf_goods_result
            sql = sql.format(shelf_image_id)
            results = mysql_ins.selectAll(sql)
            print (results)
            box_id = []
            shelf_img_id = []
            xmin, ymin, xmax, ymax = [],[],[],[]
            level = []
            result=[]
            upc=[]
            is_label=[]
            col=[]
            row_c=[]
            process_code=[]
            for row in list(results):
                box_id.append(int(row[0]))
                shelf_img_id.append(int(row[1]))
                xmin.append(int(row[2]))
                ymin.append(int(row[3]))
                xmax.append(int(row[4]))
                ymax.append(int(row[5]))
                level.append(int(row[6]))
                result.append(int(row[7]))
                upc.append(str(row[8]))
                is_label.append(int(row[9]))
                col.append(int(row[10]))
                row_c.append(int(row[11]))
                process_code.append(int(row[12]))
            mysql_ins.close()
            if (len(shelf_img_id))>0:
                shelf_img = self.get_ai_shelf_img(shelf_img_id[0])
                level_boxes = self.get_check_level_boxes(box_id,level,xmin, ymin, xmax, ymax,result,upc,is_label,col,row_c,process_code)
                return level_boxes,shelf_img_id,shelf_img
        except Exception as e:
            logger.error("get_ai_goods failed ,shelf_image_id="+str(shelf_image_id))
            logger.error(traceback.format_exc())
            return None,None,None
    def get_check_level_boxes(self, box_ids, box_levels, xmins, ymins, xmaxs, ymaxs,results,upcs,is_labels,cols,rows,process_codes):
        levels = list(set(box_levels))
        level_boxes = {}
        for level in levels:
            level_boxes[level] = []
        for level in levels:
            for box_id, box_level, xmin, ymin, xmax, ymax,result,upc,is_label,col,row,process_code in zip(box_ids, box_levels, xmins, ymins, xmaxs, ymaxs,results,upcs,is_labels,cols,rows,process_codes):
                if level == box_level:
                    level_boxes[level].append((xmin, ymin, xmax, ymax, box_id))
        return level_boxes
    def get_ai_shelf_img(self,shelf_img_idi):
        mysql_ins = django_mysql_util.DjangoMysql('default')
        try:
            sql = ai.get_shelf_img.format(int(shelf_img_idi))
            result = mysql_ins.selectOne(sql)
            rectsource = str(result[0])
            source = str(result[1])
            img_file=None
            if rectsource != '' and rectsource != '0' :
                img_file = os.path.join(settings.MEDIA_ROOT, rectsource)
            else:
                img_file = os.path.join(settings.MEDIA_ROOT, source)
            if os.path.isfile(img_file) == False:
                logger.error("LoadData get_ai_shelf_img is Null , shelf_img_path = "+str(img_file))
                return None
            shelf_img = cv2.imread(img_file)
            mysql_ins.close()
            return shelf_img
        except Exception as e:
            logger.error("get_ai_shelf_img failed ,shelf_img_idi="+str(shelf_img_idi))
            logger.error(traceback.format_exc())
            mysql_ins.close()
        return None
