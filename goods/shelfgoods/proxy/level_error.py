from goods.shelfgoods.bean import goods_box
from goods.shelfgoods.bean import code
def process(level,boxes):
    good_cols = []
    for box in boxes:
        good_col_ins = goods_box.GoodsColumn()
        (xmin,ymin,xmax,ymax,box_id) = box
        good_col_ins.location_box = (xmin,ymin,xmax,ymax)
        good_col_ins.box_id = box_id
        good_col_ins.compare_code = code.code_9
        good_col_ins.compare_result = code.result_code[code.code_9]
        good_cols.append(good_col_ins)
    goodbox_ins = goods_box.GoodsBox(level,0,good_cols)
    return goodbox_ins