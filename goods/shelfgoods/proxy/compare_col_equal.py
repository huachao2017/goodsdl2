from goods.shelfgoods.bean import code
from dl import shelftradition_match
import logging
logger = logging.getLogger("detect")
from set_config import config
from goods.shelfgoods.imgsearch.aliyun.search import ImgSearch
aliyun_search_img_switch = config.common_params['aliyun_search_img_switch']
def process(check_box_ins,display_ins,shelf_img,with_in_upcs = None):
    logger.info("current level process compare_col_equal ..................")
    ck_goodscolumn_inss = check_box_ins.gbx_ins.goodscolumns
    ds_goodscolumn_inss = display_ins.gbx_ins.goodscolumns
    ck_cols = check_box_ins.gbx_ins.level_columns
    ds_cols = display_ins.gbx_ins.level_columns
    logger.info("level proxy process is compare_col_min  ck_cols=%s,ds_cols =%s" % (str(ck_cols), str(ds_cols)))
    for ck_gcs in ck_goodscolumn_inss:
        if ck_gcs == [] or ck_gcs == None :
            continue
        if ck_gcs.is_label is not None and ck_gcs.is_label == 1:  # 人工已标注的不做比对
            continue
        ck_location_column = ck_gcs.location_column
        ck_location_row = ck_gcs.location_row
        ck_box = ck_gcs.location_box
        for ds_gcs in ds_goodscolumn_inss:
            if ds_gcs == [] or ds_gcs == None:
                continue
            ds_upc = ds_gcs.upc
            ds_location_column = ds_gcs.location_column
            ds_location_row = ds_gcs.location_row
            if ck_gcs.compare_code == None and  ds_location_column == ck_location_column and ds_location_row==ck_location_row:
                target_img = shelf_img[int(ck_box[1]):int(ck_box[3]), int(ck_box[0]):int(ck_box[2])]
                if aliyun_search_img_switch:
                    search_ins = ImgSearch()
                    upcs = search_ins.search_cvimg(target_img)
                    if upcs != None and len(upcs) > 0 and ds_upc in upcs:
                        ck_gcs.compare_code = code.code_12
                        ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
                        ck_gcs.upc = ds_upc
                    elif (upcs != None and len(upcs) > 0 and ds_upc not in upcs):
                        ck_gcs.compare_code = code.code_13
                        ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
                    elif (upcs != None and len(upcs) <= 0):
                        ck_gcs.compare_code = code.code_14
                        ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
                    else:
                        ck_gcs.compare_code = code.code_15
                        ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
                else:
                    match_ins = shelftradition_match.ShelfTraditionMatch(ds_upc)
                    match_result = match_ins.detect_one_with_cv2array(target_img)
                    logger.info("ck_box box_id=%s,upc=%s,match_result=%s,ds=(%s,%s),ck=(%s,%s)" % (
                    str(ck_gcs.box_id), str(ds_upc), str(code.match_result[match_result]),str(ds_location_column), str(ds_location_row),str(ck_location_column),str(ck_location_row)))
                    ck_gcs.compare_code = code.match_result[match_result]
                    ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
                    if match_result:
                        ck_gcs.upc = ds_upc
            elif  ck_gcs.compare_code == None and  ds_location_column == ck_location_column:
                ck_gcs.compare_code = code.code_5
                ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
            # else:
            #     ck_gcs.compare_code = code.code_6
            #     ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
    return check_box_ins,display_ins







