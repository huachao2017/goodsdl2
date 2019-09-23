from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
from goods.shelfgoods.proxy import compare_proxy_factory,level_error

import logging
logger = logging.getLogger("detect")


class Compare:
    shelf_image_id = None
    display_id = None
    shelf_id = None
    def __init__(self,shelf_image_id,display_id,shelf_id):
        self.shelf_image_id = shelf_image_id
        self.display_id = display_id
        self.shelf_id = shelf_id

    def do_compare(self):
        loaddata_ins = load_data.LoadData()
        level_goods = loaddata_ins.get_tz_dispaly_goods(self.display_id)
        box_ids, shelf_img_ids, xmins, ymins, xmaxs, ymaxs, levels, shelf_img = loaddata_ins.get_ai_goods(self.shelf_image_id)
        if level_goods != None and box_ids != None and shelf_img != None and level_goods[self.shelf_id] != None:
            return self.for_dcompare(box_ids,levels,xmins, ymins, xmaxs, ymaxs,shelf_img,level_goods[self.shelf_id])
        else:
            logger.error("load data failed ,display_id=%s,shelf_image_id=%s"%(self.display_id,self.shelf_image_id))
            return None,None,None,None,None

    def for_dcompare(self,box_ids,box_levels,xmins, ymins, xmaxs, ymaxs,shelf_img,level_goods):
        level_boxes = self.get_check_level_boxes(box_ids,box_levels,xmins, ymins, xmaxs, ymaxs)
        gbx_inss = []
        for level in level_boxes:
            if level in list(level_goods.keys()):
                for levelj in level_goods:
                    if int(level) == int(levelj):
                       ckbx_stu = checkbox_structure.CheckBoxStructure(level,level_boxes[level])
                       disy_stu = display_structure.DispalyStructure(levelj,level_goods[levelj])
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
                    compare_code=3
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
                    'code':compare_code,
                    'process_code':process_code,
                    'boxid':box_id,
                    'upc':upc
                            })
        score=float("%.2f" % (equal_cnt+unknown_cnt)/len(detail))
        return detail,score,equal_cnt,different_cnt,unknown_cnt

    def get_check_level_boxes(self,box_ids,box_levels,xmins, ymins, xmaxs, ymaxs):
        levels=list(set(box_levels))
        level_boxes = {}
        for level in levels:
            level_boxes[level]=[]
        for level in levels:
            for box_id,box_level, xmin, ymin, xmax, ymax in zip(box_ids,box_levels, xmins, ymins, xmaxs, ymaxs):
                if level == box_level:
                    level_boxes[level].append((xmin, ymin, xmax, ymax,box_id))
        return level_boxes



