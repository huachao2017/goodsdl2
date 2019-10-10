from goods.shelfgoods.local_util import tz_compare,levelcompare,upc_util
#upcs = ['','']  or None
def compare(shelf_image_id,dispaly_id,shelf_id,upcs=None):
    compare_ins = tz_compare.Compare(shelf_image_id,dispaly_id,shelf_id,upcs)
    detail, equal_cnt, different_cnt, unknown_cnt = compare_ins.do_compare()
    ret=None
    if detail is not None:
        score = get_score(equal_cnt, unknown_cnt, different_cnt)
        ret = {
            "score":score,
            "equal_cnt":equal_cnt,
            "different_cnt":different_cnt,
            "unknown_cnt":unknown_cnt,
            "detail":detail
        }
    return ret


def level_compare(display_img_id,shelf_id,shelf_image_id,box_id):
    detail, equal_cnt, different_cnt, unknown_cnt = levelcompare.compare(display_img_id,shelf_id,shelf_image_id,box_id)
    ret = None
    if detail is not None:
        score = get_score(equal_cnt, unknown_cnt, different_cnt)
        ret = {
            "score": score,
            "equal_cnt": equal_cnt,
            "different_cnt": different_cnt,
            "unknown_cnt": unknown_cnt,
            "detail": detail
        }
    return ret


def get_upc(display_img_id,shelf_id,shelf_image_id,box_id):
    upc = upc_util.get_upc(display_img_id,shelf_id,shelf_image_id,box_id)
    return upc


def get_score(equal_cnt,unknown_cnt,different_cnt):
    score = int(float("%.2f" % ((equal_cnt + unknown_cnt) / (equal_cnt+unknown_cnt+different_cnt))) * 100)
    return score