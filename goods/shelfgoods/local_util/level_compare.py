from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
import logging
from goods.shelfgoods.proxy import compare_proxy_factory,level_error
logger = logging.getLogger("detect")
def compare(display_img_id,shelf_id,shelf_image_id,box_id):
    loaddata_ins = load_data.LoadData()
    level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(shelf_image_id)
    level_goods = loaddata_ins.get_tz_dispaly_goods(display_img_id)
    level_goods = level_goods[shelf_id]
    logger.info("level_boxes : " + str(level_boxes))
    logger.info("level_goods : " + str(level_goods))
    level = get_level(box_id,level_boxes)
    gbx_inss=[]
    if level is not None and level in list(level_goods.keys()):
        ckbx_stu = checkbox_structure.CheckBoxStructure(level, level_boxes[level])
        disy_stu = display_structure.DispalyStructure(level, level_goods[level])
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
            detail.append({
                'level': int(level),
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'result': compare_code,
                'process_code': process_code,
                'boxid': box_id,
                'upc': upc
            })
    score = 0.0
    if len(detail) == 0:
        score = 0.0
    else:
        score = float("%.2f" % ((equal_cnt + unknown_cnt) / len(detail)))
    logger.info("level compare detail=" + str(detail))
    return detail, score, equal_cnt, different_cnt, unknown_cnt

def get_level(box_id_0,level_boxes):
    for level in level_boxes:
        (xmin,ymin,xmax,ymax,box_id) = level_boxes[level]
        if box_id ==box_id_0:
            return level
    return None
