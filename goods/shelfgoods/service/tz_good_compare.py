from goods.shelfgoods.local_util import tz_compare
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
