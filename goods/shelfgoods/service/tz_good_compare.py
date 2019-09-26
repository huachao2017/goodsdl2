from goods.shelfgoods.local_util import tz_compare,level_compare,upc_util
def compare(shelf_image_id,dispaly_id,shelf_id):
    compare_ins = tz_compare.Compare(shelf_image_id,dispaly_id,shelf_id)
    detail, score, equal_cnt, different_cnt, unknown_cnt = compare_ins.do_compare()
    ret=None
    if detail is not None:
        ret = {
            "score":score,
            "equal_cnt":equal_cnt,
            "different_cnt":different_cnt,
            "unknown_cnt":unknown_cnt,
            "detail":detail
        }
    return ret


def level_compare(display_img_id,shelf_id,shelf_image_id,box_id):
    detail, score, equal_cnt, different_cnt, unknown_cnt = level_compare.compare(display_img_id,shelf_id,shelf_image_id,box_id)
    ret = None
    if detail is not None:
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


def get_score(equal_cnt,unknown_cnt,sum_cnt):
    score = float("%.2f" % ((equal_cnt + unknown_cnt) / sum_cnt))
    return score