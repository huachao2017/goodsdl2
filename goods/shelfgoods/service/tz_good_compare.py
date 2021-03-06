from goods.shelfgoods.local_util import tz_compare,upc_util
#upcs = ['','']  or None
from goods.shelfgoods.imgsearch.utils import search_upc
def compare(shelf_image_id,dispaly_id,shelf_id,upcs=None):
    compare_ins = tz_compare.Compare(shelf_image_id,dispaly_id,shelf_id,upcs)
    detail, equal_cnt, different_cnt, unknown_cnt = compare_ins.do_compare()
    ret=None
    if detail is not None:
        # score = get_score(equal_cnt, unknown_cnt, different_cnt)
        score = int(float("%.2f" % ((equal_cnt + unknown_cnt) / (equal_cnt + unknown_cnt + different_cnt))) * 100)
        ret = {
            "score":score,
            "equal_cnt":equal_cnt,
            "different_cnt":different_cnt,
            "unknown_cnt":unknown_cnt,
            "detail":detail
        }
    return ret

def get_upc(display_img_id,shelf_id,shelf_image_id,box_id):
    upc = upc_util.get_upc(display_img_id,shelf_id,shelf_image_id,box_id)
    return upc

def search_upc_from_api(xmin,ymin,xmax,ymax,cvimg,api="baidu"):
    upc,process_code = search_upc.search(xmin,ymin,xmax,ymax,cvimg,api="baidu")
    return upc,process_code