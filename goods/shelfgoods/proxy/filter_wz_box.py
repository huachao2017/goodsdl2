from goods.shelfgoods.bean import code
import logging
logger = logging.getLogger("detect")
def process(check_box_ins,display_ins,shelf_img):
    logger.info("current level process filter_wz_box ..................")
    ck_goodscolumn_inss = check_box_ins.gbx_ins.goodscolumns
    ds_goodscolumn_inss = display_ins.gbx_ins.goodscolumns
    for ck_gcs in ck_goodscolumn_inss:
        if ck_gcs == [] or ck_gcs == None :
            continue
        ck_location_column = ck_gcs.location_column
        ck_location_row = ck_gcs.location_row
        ds_rows = get_col_display_max(ds_goodscolumn_inss,ck_location_column)
        if len(ds_rows) > 0:
            for ds_gcs in ds_goodscolumn_inss:
                if ds_gcs == [] or ds_gcs == None:
                    continue
                ds_location_column = ds_gcs.location_column
                ds_location_row = ds_gcs.location_row
                ds_is_fitting = ds_gcs.is_fitting
                if ck_gcs.compare_code == None and  ds_location_column == ck_location_column and ds_location_row==ck_location_row and ds_is_fitting == 1:
                    ck_gcs.compare_code = code.code_10
                    ck_gcs.compare_result = code.result_code[ck_gcs.compare_code]
    return check_box_ins,display_ins


def get_col_display_max(ds_goodscolumn_inss,col):
    rows = []
    for ds_gcs in ds_goodscolumn_inss:
        ds_upc = ds_gcs.upc
        ds_location_column = ds_gcs.location_column
        ds_location_row = ds_gcs.location_row
        if col == ds_location_column:
            rows.append(ds_location_row)
    return rows






