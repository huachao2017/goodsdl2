from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
import logging
logger = logging.getLogger("detect")
def get_upc(display_img_id,shelf_id,shelf_image_id,box_id):
    loaddata_ins = load_data.LoadData()
    level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(shelf_image_id)
    level_goods = loaddata_ins.get_tz_dispaly_goods(display_img_id)
    level_goods = level_goods[shelf_id]
    gbx_inss = []
    logger.info("get_upc box_id="+str(box_id))
    logger.info("level_boxes : " + str(level_boxes))
    logger.info("level_goods : " + str(level_goods))
    for level in level_boxes:
        if level in list(level_goods.keys()):
            for levelj in level_goods:
                if int(level) == int(levelj):
                    ckbx_stu = checkbox_structure.CheckBoxStructure(level, level_boxes[level])
                    disy_stu = display_structure.DispalyStructure(levelj, level_goods[levelj])
                    ckbx_goodscolumn_inss  = ckbx_stu.gbx_ins.goodscolumns
                    disy_goodscolumn_inss = disy_stu.gbx_ins.goodscolumns
                    for ckbx_goodscolumn_ins in ckbx_goodscolumn_inss:
                        if ckbx_goodscolumn_ins.box_id == box_id:
                            for disy_goodscolumn_ins in disy_goodscolumn_inss:
                                if disy_goodscolumn_ins.location_column == ckbx_goodscolumn_ins.location_column and disy_goodscolumn_ins.location_row == ckbx_goodscolumn_ins.location_row:
                                    logger.info("get_upc col=%s,row=%s,upc=%s"%(str(disy_goodscolumn_ins.location_column),str(disy_goodscolumn_ins.location_column),str(disy_goodscolumn_ins.upc)))
                                    return disy_goodscolumn_ins.upc
    logger.info("get_upc failed !!!!")
    return None


