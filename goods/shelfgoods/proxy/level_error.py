from goods.shelfgoods.bean import goods_box
from goods.shelfgoods.bean import code
def process(level,boxes):
    good_cols = []
    for box in boxes:
        good_col_ins = goods_box.GoodsColumn()
        good_col_ins.location_box = box
        good_col_ins.compare_code = code.code_9
        good_col_ins.compare_result = code.result_code[code.code_9]
        good_cols.append(good_col_ins)
    goodbox_ins = goods_box.GoodsBox(level,0,good_cols)
    return goodbox_ins