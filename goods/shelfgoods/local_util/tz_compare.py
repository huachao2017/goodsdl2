from goods.shelfgoods.local_util import load_data
from goods.shelfgoods.bean import checkbox_structure,display_structure,code
from goods.shelfgoods.proxy import compare_proxy_factory,level_error

import logging
logger = logging.getLogger("detect")


class Compare:
    shelf_image_id = None
    display_id = None
    def __init__(self,shelf_image_id,display_id):
        self.shelf_image_id = shelf_image_id
        self.display_id = display_id

    def do_compare(self):
        loaddata_ins = load_data.LoadData()
        shelf_id, level_goods = loaddata_ins.get_tz_dispaly_goods(self.display_id)
        box_id, shelf_img_id, xmin, ymin, xmax, ymax, new_level, shelf_img = loaddata_ins.get_ai_goods(self.shelf_image_id)
        if level_goods != None and box_id != None and shelf_img != None:
            return self.for_dcompare(new_level,xmin, ymin, xmax, ymax,shelf_img,level_goods)
        else:
            logger.error("load data failed ,display_id=%s,shelf_image_id=%s"%(self.display_id,self.shelf_image_id))
            return None

    def for_dcompare(self,box_level,xmin, ymin, xmax, ymax,shelf_img,level_goods):
        level_boxes = self.get_check_level_boxes(box_level,xmin, ymin, xmax, ymax)
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
        ret = []
        for gbx_ins in gbx_inss:
            level = gbx_ins.level
            for good_col in gbx_ins.goodscolumns:
                (xmin,ymin,xmax,ymax) = good_col.location_box
                compare_code = None
                for key in code.filter_code:
                    if good_col.compare_code is not None and good_col.compare_code in code.filter_code[key]:
                        compare_code = key
                if compare_code==None or good_col.compare_code == None:
                    compare_code=3
                ret.append({
                    'level':int(level),
                    'xmin':xmin,
                    'ymin':ymin,
                    'xmax':xmax,
                    'ymax':ymax,
                    'code':compare_code,
                            })
        return ret

    def get_check_level_boxes(self,box_level,xmin, ymin, xmax, ymax):
        levels=list(set(box_level))
        level_boxes = {}
        for level in levels:
            level_boxes[level]=[]
        for level in levels:
            for leveli, xmini, ymini, xmaxi, ymaxi in zip(box_level, xmin, ymin, xmax, ymax):
                if level == leveli:
                    level_boxes[level].append((xmini, ymini, xmaxi, ymaxi))

        return level_boxes



