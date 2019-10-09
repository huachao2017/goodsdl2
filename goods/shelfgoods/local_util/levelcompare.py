from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
import logging
from goods.shelfgoods.proxy import compare_proxy_factory,level_error
logger = logging.getLogger("detect")
def compare(display_img_id,shelf_id,shelf_image_id,box_id):
    loaddata_ins = load_data.LoadData()
    level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(shelf_image_id)
    level_goods = loaddata_ins.get_tz_dispaly_goods(display_img_id)
    level_boxes_result = loaddata_ins.get_ai_goods_result(shelf_image_id)
    level_goods = level_goods[shelf_id]
    logger.info("level_boxes : " + str(level_boxes))
    logger.info("level_goods : " + str(level_goods))
    level = get_level(box_id,level_boxes)
    gbx_inss=[]
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
            for key in level_boxes_result:
                if level == key:
                    for value in list(level_boxes_result[key]):
                        (xmin1, ymin1, xmax1, ymax1, box_id1, result1, upc1) = value
                        if result1 == 0 and box_id == box_id1:
                            compare_code = 0
                            process_code = code.code_11
                            upc = upc1
                        elif result1 == 1 and box_id == box_id1:
                            compare_code = 1
                            process_code = code.code_11
                            upc = upc1
            if compare_code == None or process_code == None:
                compare_code = 2
            if compare_code == 0:
                equal_cnt += 1
            if compare_code == 1:
                different_cnt += 1
            if compare_code == 2:
                unknown_cnt += 1
            detail.append({
                'level': int(level),
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'result': compare_code,
                'process_code': process_code,
                'col': good_col.location_column,
                'row': good_col.location_row,
                'boxid': box_id,
                'upc': upc
            })
    for key in level_boxes_result:
        if level == key:
            (xmin,ymin,xmax,ymax,box_id,result,upc) = level_boxes_result[key]
            if result is None or result == -1 :
                result = 2
            if result == 0:
                equal_cnt += 1
            if result == 1:
                different_cnt += 1
            if result == 2:
                unknown_cnt += 1
            detail.append({
                'level': int(key),
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'result': result,
                'process_code': code.code_11,
                'col': None,
                'row': None,
                'boxid': box_id,
                'upc': upc
            })
    logger.info("level compare detail=" + str(detail))
    return detail, equal_cnt, different_cnt, unknown_cnt

def get_level(box_id_0,level_boxes):
    for level in level_boxes:
        boxes_l = level_boxes[level]
        for box in boxes_l:
            (xmin, ymin, xmax, ymax,box_id) =box
            if box_id ==box_id_0:
                return level
    return None
