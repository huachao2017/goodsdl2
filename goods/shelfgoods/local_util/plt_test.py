from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
import logging
from goods.shelfgoods.proxy import compare_proxy_factory,level_error
logger = logging.getLogger("detect")
import time
def show_checkbox(display_img_id,shelf_id,shelf_image_id,box_id):
    loaddata_ins = load_data.LoadData()
    level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(shelf_image_id)
    level_goods = loaddata_ins.get_tz_dispaly_goods(display_img_id)
    level_boxes_result = loaddata_ins.get_ai_goods_result(shelf_image_id)
    level_goods = level_goods[shelf_id]
    logger.info("level_boxes : " + str(level_boxes))
    logger.info("level_goods : " + str(level_goods))
    level = get_level(box_id, level_boxes)
    gbx_inss = []
    if level is not None and level in list(level_goods.keys()):
        ckbx_stu = checkbox_structure.CheckBoxStructure(level, level_boxes[level])
        logger.info("ckbx_stu :")
        logger.info('\n'.join(['%s:%s' % item for item in ckbx_stu.__dict__.items()]))
        disy_stu = display_structure.DispalyStructure(level, level_goods[level])
        logger.info("disy_stu :")
        logger.info('\n'.join(['%s:%s' % item for item in disy_stu.__dict__.items()]))
        proxy_ins = compare_proxy_factory.ProxyFactory(ckbx_stu, disy_stu, shelf_img)
        gbx_ins = proxy_ins.process()
        gbx_inss.append(gbx_ins)
    elif level is not None and level not in list(level_goods.keys()):
        gbx_ins = level_error.process(level, level_boxes[level])
        gbx_inss.append(gbx_ins)
    detail = []
    equal_cnt = 0
    different_cnt = 0
    unknown_cnt = 0
    for gbx_ins in gbx_inss:
        level = gbx_ins.level
        for good_col in gbx_ins.goodscolumns:
            (xmin, ymin, xmax, ymax) = good_col.location_box
            box_id = good_col.box_id
            compare_code = None
            process_code = good_col.compare_code
            upc = good_col.upc
            for key in code.filter_code:
                if good_col.compare_code is not None and good_col.compare_code in code.filter_code[key]:
                    compare_code = key
            if compare_code == None or good_col.compare_code == None:
                compare_code = 2
            if compare_code == 0:
                equal_cnt += 1
            if compare_code == 1:
                different_cnt += 1
            if compare_code == 2:
                unknown_cnt += 1
            shelf_img=bboxes_draw_on_img(shelf_img,good_col.location_box,str(good_col.location_column)+"_"+str(good_col.location_row)+"_"+str(compare_code))
    # cv2.imshow(shelf_img)
    cv2.imwrite("/home/ai/data/test_shelf/"+str(time.time())+".jpg",shelf_img)

def get_level(box_id_0,level_boxes):
    for level in level_boxes:
        boxes_l = level_boxes[level]
        for box in boxes_l:
            (xmin, ymin, xmax, ymax,box_id) =box
            if box_id ==box_id_0:
                return level
    return None

import cv2
def bboxes_draw_on_img(img, bbox, col_row_code,thickness=2):
        color = (255, 255, 255)
        p1 = (int(bbox[0] ), int(bbox[1]))
        p2 = (int(bbox[2]), int(bbox[3]))
        cv2.rectangle(img, p1[::-1], p2[::-1], color, thickness)
        # Draw text...
        s = '%s' % (col_row_code)
        p1 = (p1[0]-2, p1[1])
        cv2.putText(img, s, p1[::-1], cv2.FONT_HERSHEY_DUPLEX, 0.4, color, 1)
        return img

if __name__=='__main__':
    display_img_id= 136
    shelf_id = "DJ-008-91-001"
    shelf_image_id = 170
    box_id = 3272
    show_checkbox(display_img_id,shelf_id,shelf_image_id,box_id)