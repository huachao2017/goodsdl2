from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
from goods.shelfgoods.proxy import compare_proxy_factory,level_error
import demjson
import logging
logger = logging.getLogger("detect")

import traceback
class Compare:
    shelf_image_id = None
    display_id = None
    shelf_id = None
    def __init__(self,shelf_image_id,display_id,shelf_id):
        self.shelf_image_id = shelf_image_id
        self.display_id = display_id
        self.shelf_id = shelf_id

    def do_compare(self):
        try:
            loaddata_ins = load_data.LoadData()
            level_goods = loaddata_ins.get_tz_dispaly_goods(self.display_id)
            level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(self.shelf_image_id)
            if level_boxes is not None and shelf_img_id is not None and shelf_img is not None and level_goods[self.shelf_id] is not None:
                return self.for_dcompare(level_boxes,shelf_img,level_goods[self.shelf_id])
            else:
                logger.error("load data failed ,display_id=%s,shelf_image_id=%s"%(self.display_id,self.shelf_image_id))
                return None,None,None,None,None
        except:
            logger.error(traceback.format_exc())
            return None, None, None, None, None

    def for_dcompare(self,level_boxes,shelf_img,level_goods):
        # level_boxes = self.get_check_level_boxes(box_ids,box_levels,xmins, ymins, xmaxs, ymaxs)
        gbx_inss = []
        logger.info("level_boxes : "+str(level_boxes))
        logger.info("level_goods : "+str(level_goods))
        for level in level_boxes:
            if level in list(level_goods.keys()):
                for levelj in level_goods:
                    if int(level) == int(levelj):
                       ckbx_stu = checkbox_structure.CheckBoxStructure(level, level_boxes[level])
                       # logger.info("ckbx_stu : " + str(demjson.encode(ckbx_stu)))
                       print ("ckbx_stu :" )
                       print('\n'.join(['%s:%s' % item for item in ckbx_stu.__dict__.items()]))
                       disy_stu = display_structure.DispalyStructure(levelj, level_goods[levelj])
                       print("disy_stu :")
                       print('\n'.join(['%s:%s' % item for item in disy_stu.__dict__.items()]))
                       # logger.info("disy_stu : " + str(demjson.encode(disy_stu)))
                       proxy_ins = compare_proxy_factory.ProxyFactory(ckbx_stu,disy_stu,shelf_img)
                       gbx_ins = proxy_ins.process()
                       gbx_inss.append(gbx_ins)
            else:
                gbx_ins = level_error.process(level,level_boxes[level])
                gbx_inss.append(gbx_ins)
        detail = []
        equal_cnt = 0
        different_cnt = 0
        unknown_cnt = 0
        for gbx_ins in gbx_inss:
            level = gbx_ins.level
            for good_col in gbx_ins.goodscolumns:
                (xmin,ymin,xmax,ymax) = good_col.location_box
                box_id = good_col.box_id
                compare_code = None
                process_code = good_col.compare_code
                upc = good_col.upc
                for key in code.filter_code:
                    if good_col.compare_code is not None and good_col.compare_code in code.filter_code[key]:
                        compare_code = key
                if compare_code==None or good_col.compare_code == None:
                    compare_code=2
                if compare_code == 0:
                    equal_cnt+=1
                if compare_code == 1:
                    different_cnt+=1
                if compare_code == 2:
                    unknown_cnt+=1
                detail.append({
                    'level':int(level),
                    'xmin':xmin,
                    'ymin':ymin,
                    'xmax':xmax,
                    'ymax':ymax,
                    'result':compare_code,
                    'process_code':process_code,
                    'boxid':box_id,
                    'col':good_col.location_column,
                    'row':good_col.location_row,
                    'upc':upc
                            })
        logger.info("for_dcompare detail="+str(detail))
        return detail,equal_cnt,different_cnt,unknown_cnt




