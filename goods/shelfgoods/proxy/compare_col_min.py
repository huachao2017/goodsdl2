from goods.shelfgoods.bean import code
from dl import shelftradition_match
import logging
logger = logging.getLogger("detect")
def process(check_box_ins,display_ins,shelf_img):
    logger.info("level proxy process is compare_col_min ..................")
    ck_goodscolumn_inss = check_box_ins.goodscolumns
    ds_goodscolumn_inss = display_ins.goodscolumns
    ck_cols = check_box_ins.level_columns
    ds_cols = display_ins.level_columns
    col_goods={}
    col_compare_l = {}
    for i in range(ds_cols-ck_cols+1):
        ck_goodscolumn_inss_copy = ck_goodscolumn_inss.copy()
        ds_goodscolumn_inss_copy = ds_goodscolumn_inss.copy()
        sum_model_true,col_l = sum_compare_model_true(ck_goodscolumn_inss_copy,ds_goodscolumn_inss_copy,i,shelf_img)
        col_goods[i] = sum_model_true
        col_compare_l[i] = col_l
    a = sorted(col_goods.items(), key=lambda x: x[1], reverse=True)
    col_good_i = a[0][0]
    logger.info("level proxy process is compare_col_min  col_good_i = "+str(col_good_i))
    check_box_ins = process_good_col(ck_goodscolumn_inss,col_compare_l[col_good_i])
    return check_box_ins, display_ins

def process_good_col(check_box_ins,col_compare_l):
    ck_goodscolumn_inss = check_box_ins.goodscolumns
    for ck_gcs in ck_goodscolumn_inss:
        if ck_gcs == [] or ck_gcs == None :
            continue
        ck_location_column = ck_gcs.location_column
        ck_location_row = ck_gcs.location_row
        ck_box = ck_gcs.location_box
        for i in range(len(col_compare_l)):
            (col,row,result) = col_compare_l[i]
            if ck_gcs.compare_code == None and ck_location_column==col and ck_location_row==row:
                ck_gcs.compare_code=code.match_result[result]
                ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
    for ck_gcs in ck_goodscolumn_inss:
        if ck_gcs == [] or ck_gcs == None :
            continue
        if ck_gcs.compare_code==None:
            ck_gcs.compare_code=code.code_7
            ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
    return check_box_ins


def sum_compare_model_true(ck_goodscolumn_inss,ds_goodscolumn_inss,i,shelf_img):
    sum_true = 0
    compare_re_l=[]
    for ck_gcs in ck_goodscolumn_inss:
        if ck_gcs == [] or ck_gcs == None:
            continue
        ck_location_column = ck_gcs.location_column
        ck_location_row = ck_gcs.location_row
        ck_box = ck_gcs.location_box
        ds_rows = get_col_display_max(ds_goodscolumn_inss, ck_location_column)
        if ds_rows > 0:
            for ds_gcs in ds_goodscolumn_inss:
                if ds_gcs == [] or ds_gcs == None:
                    continue
                ds_upc = ds_gcs.upc
                ds_location_column = ds_gcs.location_column - i
                ds_location_row = ds_gcs.location_row
                if ck_gcs.compare_code == None and ds_location_column == ck_location_column and ds_location_row == ck_location_row:
                    target_img = shelf_img[int(ck_box[1]):int(ck_box[3]), int(ck_box[0]):int(ck_box[2])]
                    match_ins = shelftradition_match.ShelfTraditionMatch(ds_upc)
                    match_result = match_ins.detect_one_with_cv2array(target_img)
                    compare_re_l.append((ck_location_column,ck_location_row,match_result))
                    if match_result == True:
                        sum_true+=1
    return sum_true,compare_re_l


def get_col_display_max(ds_goodscolumn_inss,col):
    rows = []
    for ds_gcs in ds_goodscolumn_inss:
        ds_upc = ds_gcs.upc
        ds_location_column = ds_gcs.location_column
        ds_location_row = ds_gcs.location_row
        if col == ds_location_column:
            rows.append(ds_location_row)
    return rows
