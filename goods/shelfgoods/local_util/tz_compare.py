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
    upcs = None
    def __init__(self,shelf_image_id,display_id,shelf_id,upcs):
        self.shelf_image_id = shelf_image_id
        self.display_id = display_id
        self.shelf_id = shelf_id
        self.upcs = upcs

    def do_compare(self):
        try:
            loaddata_ins = load_data.LoadData()
            level_goods = loaddata_ins.get_tz_dispaly_goods(self.display_id)
            level_boxes, shelf_img_id, shelf_img = loaddata_ins.get_ai_goods(self.shelf_image_id)
            if level_boxes is not None and shelf_img_id is not None and shelf_img is not None and level_goods[self.shelf_id] is not None:
                return self.for_dcompare(level_boxes,shelf_img,level_goods[self.shelf_id],self.upcs)
            else:
                logger.error("load data failed ,display_id=%s,shelf_image_id=%s"%(self.display_id,self.shelf_image_id))
                return None,None,None,None
        except:
            logger.error(traceback.format_exc())
            return None, None, None, None

    def for_dcompare(self,level_boxes,shelf_img,level_goods,upcs):
        # level_boxes = self.get_check_level_boxes(box_ids,box_levels,xmins, ymins, xmaxs, ymaxs)
        gbx_inss = []
        logger.info("level_boxes : "+str(level_boxes))
        logger.info("level_goods : "+str(level_goods))
        for level in level_boxes:
            if level in list(level_goods.keys()):
                for levelj in level_goods:
                    if int(level) == int(levelj):
                       ckbx_stu = checkbox_structure.CheckBoxStructure(level, level_boxes[level])
                       logger.info ("ckbx_stu :" )
                       logger.info('\n'.join(['%s:%s' % item for item in ckbx_stu.__dict__.items()]))
                       disy_stu = display_structure.DispalyStructure(levelj, level_goods[levelj])
                       logger.info("disy_stu :")
                       logger.info('\n'.join(['%s:%s' % item for item in disy_stu.__dict__.items()]))
                       proxy_ins = compare_proxy_factory.ProxyFactory(ckbx_stu,disy_stu,shelf_img,upcs)
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
                if good_col.process_code is not None and good_col.process_code == -1:
                    good_col.process_code = good_col.compare_code
                result = -1
                if good_col.process_code in code.filter_code[0]:
                    result = 0
                if good_col.process_code in code.filter_code[1]:
                    result = 1
                if good_col.process_code in code.filter_code[2]:
                    result = 2
                if good_col.process_code  == code.code_11:
                    result = good_col.result
                if result == 0 :
                    equal_cnt+=1
                if result == 1 :
                    different_cnt+=1
                if result == 2:
                    unknown_cnt+=1
                detail.append({
                    'level':int(level),
                    'xmin':xmin,
                    'ymin':ymin,
                    'xmax':xmax,
                    'ymax':ymax,
                    'result':result,
                    'process_code':good_col.process_code,
                    'boxid':good_col.box_id,
                    'col':good_col.location_column,
                    'row':good_col.location_row,
                    'upc':good_col.upc
                            })
        logger.info("for_dcompare detail="+str(detail))
        return detail,equal_cnt,different_cnt,unknown_cnt




