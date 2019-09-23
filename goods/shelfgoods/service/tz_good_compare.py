from goods.shelfgoods.local_util import tz_compare
def compare(shelf_image_id,dispaly_id,shelf_id):
    compare_ins = tz_compare.Compare(shelf_image_id,dispaly_id,shelf_id)
    ret,tz_compare_score = compare_ins.do_compare()
    return ret,tz_compare_score
