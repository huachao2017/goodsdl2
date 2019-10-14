from goods.shelfgoods.imgsearch.aliyun.search import ImgSearch
from goods.shelfgoods.imgsearch.baidu_ai.search import ImgSearch_02
import cv2
from goods.shelfgoods.bean import code
import logging
logger = logging.getLogger("detect")
# api  :  baidu  ali
def search(xmin,ymin,xmax,ymax,img_file,api="baidu"):
    try:
        shelf_img = cv2.imread(img_file)
        target_img = shelf_img[int(ymin):int(ymax), int(xmin):int(xmax)]
        search_ins = None
        if api=='ali':
            search_ins = ImgSearch()
        elif api == 'baidu':
            search_ins = ImgSearch_02()
        upc,process_code = search_ins.search_cvimg_top1(target_img)
        return upc,process_code
    except:
        logger.error("upc get top1 failed")
        return None,code.code_21



