from django.db import close_old_connections
import traceback
import time
import os
import django
import main.import_django_settings
from django.db import connections
from set_config import config
import traceback
from goods.choose_goods.lishu_util import oss_down_up
import uuid
import os
from goods.freezer.keras_yolo3.yolo3 import yolo_shelf
shelf_yolo_ins = yolo_shelf.YOLO()
class DetectShelf:
    default_params={
        'shelf':0.6,
        'null_box':0.3,
    }
    sql1 = "select id,origin_img_url,ai_status,vacancy_face_num,ai_img_url,ai_result_desc from sf_shop_shelf_everyday where ai_status = 0 "
    sql2 = "update sf_shop_shelf_everyday set ai_status = %s,vacancy_face_num = %s,ai_img_url = %s,updated_at = %s,ai_result_desc = %s where id = %s "
    def detect(self):
        while True:
            time.sleep(60)
            close_old_connections()
            try:
                file_oss_ins = oss_down_up.FileManager()
                conn = connections['alpha_ucenter']
                cursor_aucenter = conn.cursor()
                cursor_aucenter.execute(self.sql1)
                results = cursor_aucenter.fetchall()
                down_jpg = config.shelf_yolov3_params['down_jpg']
                print("待检测 图片数量：" + str(len(results)))
                if results is not None and len(results) > 0:
                    data = []
                    for ret in results:
                        id = ret[0]
                        origin_img_url = ret[1]
                        ai_status = ret[2]
                        vacancy_face_num = ret[3]
                        ai_img_url = ret[4]
                        ai_result_desc = ret[5]
                        down_http_file = origin_img_url
                        ai_filename = "".join(str(uuid.uuid4()).split("-")).lower()+".jpg"
                        down_local_file = os.path.join(down_jpg, ai_filename)
                        try:
                            # 下载文件
                            file_oss_ins.download(down_http_file,down_local_file)
                        except:
                            print("shelf bull_box detect error id = {},origin_img_url={},down jpg failed".format(id, origin_img_url))
                            traceback.print_exc()
                            ai_result_desc = "ufile down failed"
                            ai_status = 2
                            ai_img_url = ''
                            vacancy_face_num = -1,
                            updated_at = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                            data.append((ai_status, vacancy_face_num, ai_img_url, updated_at,ai_result_desc, id))
                            continue
                        up_local_file = os.path.join(down_jpg, "vis_" + ai_filename)
                        null_box_num = -1
                        try:
                            ret, detect_time, output_image, null_box_num = shelf_yolo_ins.detect(down_local_file,self.default_params)
                            output_image.save(up_local_file)
                        except Exception as e :
                            print("shelf bull_box detect error id = {},origin_img_url={},down_local_file={},check jpg failed".format(id,
                                                                                                                 origin_img_url,down_local_file))
                            traceback.print_exc()
                            ai_result_desc = "ufile check failed,e={}".format(e)
                            ai_status = 2
                            ai_img_url = ''
                            vacancy_face_num = -1,
                            updated_at = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                            data.append((ai_status, vacancy_face_num, ai_img_url, updated_at, ai_result_desc, id))
                            continue
                        date_up = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                        suf_path = "store_ass/" + str(date_up) + "/"
                        upload_ai_file = suf_path+"vis_"+ai_filename
                        try:
                            file_oss_ins.upload(upload_ai_file, up_local_file)
                        except:
                            print("shelf bull_box detect error id = {},origin_img_url={},upload jpg failed,up_local_file={}".format(id,
                                                                                                                  origin_img_url,up_local_file))
                            traceback.print_exc()
                            ai_result_desc = "ufile upload failed"
                            ai_status = 2
                            ai_img_url = ''
                            vacancy_face_num = -1,
                            updated_at = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                            data.append((ai_status, vacancy_face_num, ai_img_url, updated_at, ai_result_desc, id))
                            continue
                        vacancy_face_num = null_box_num
                        ai_status = 1
                        ai_result_desc=''
                        updated_at = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                        data.append((ai_status, vacancy_face_num, upload_ai_file, updated_at, ai_result_desc,id))
                    cursor_aucenter.executemany(self.sql2, data)
                    conn.commit()
                cursor_aucenter.close()
                conn.close()
            except:
                print ("shelf bull_box detect error ")
                traceback.print_exc()


if __name__=="__main__":
    ds_ins = DetectShelf()
    ds_ins.detect()