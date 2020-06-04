from goods.freezer.keras_yolo3.util import iou_util


#没有交叠的目标商品 阈值应该比较高（主要解决冰柜中，孤立商品多检的问题）
def  single_filter(iou,min_score,classes,scores,boxes):
    single_flag = []
    for i in range(len(classes)):
        flg = True
        for j in range(len(classes)):
            if i != j:
                if iou_util.IOU(boxes[i], boxes[j])>iou:
                    flg=False
        if flg and scores[i] <= min_score:
            single_flag.append(True)
        else:
            single_flag.append(False)
    p_classes, p_scores, p_boxes = [],[],[]
    for fg,cls,sce,bx in zip(single_flag,classes,scores,boxes):
        if fg == False:
            p_classes.append(cls)
            p_scores.append(sce)
            p_boxes.append(bx)
    return p_classes, p_scores, p_boxes


#存在交叠的目标商品，选择阈值较高的那个（yolov3中，对交叠的同一类目标做了最大IOU限制，而不同类的目标没有做处理，造成一定多检现象）
def diff_fiter(iou,classes,scores,boxes):
    diff_flag = []
    for i in range(len(classes)):
        flag = False
        for j in range(len(classes)):
            if classes[i] != classes[j]:
                if iou_util.IOU(boxes[i], boxes[j]) > iou:
                    if scores[i] < scores[j]:
                        flag = True
                        break
        diff_flag.append(flag)
    p_classes, p_scores, p_boxes = [], [], []
    for fg, cls, sce, bx in zip(diff_flag, classes, scores, boxes):
        if fg == False:
            p_classes.append(cls)
            p_scores.append(sce)
            p_boxes.append(bx)
    return p_classes, p_scores, p_boxes


# 货架空位识别， 判断空位在货架内部 （默认不小于两个点，在内部）
def point_in_shelf(classes,scores,boxes,default_point_nums = 2):
    shelf_boxes = []
    shelf_clzes = []
    shelf_scores = []
    null_boxes = []
    null_boxes_scores = []
    for (clz,box,score) in zip(classes,boxes,scores):
        if clz == 'shelf':
            shelf_boxes.append(box)
            shelf_clzes.append(clz)
            shelf_scores.append(score)
        if clz == 'null_box':
            null_boxes.append(box)
            null_boxes_scores.append(score)
    new_boxes = []
    new_clzes = []
    new_scores = []
    for i in range(len(null_boxes)):
        xmin,ymin,xmax,ymax = null_boxes[i]
        score = null_boxes_scores[i]
        A = (xmin,ymin)
        B = (xmax,ymin)
        C = (xmin,ymax)
        D = (xmax,ymax)
        flag = False
        for (shelf_xmin,shelf_ymin,shelf_xmax,shelf_ymax) in shelf_boxes:
            point_nums = 0
            if A[0] >= shelf_xmin and A[1] <= shelf_ymax :
                point_nums += 1
            if B[0] >= shelf_xmin and B[1] <= shelf_ymax:
                point_nums += 1
            if C[0] >= shelf_xmin and C[1] <= shelf_ymax:
                point_nums += 1
            if D[0] >= shelf_xmin and D[1] <= shelf_ymax:
                point_nums += 1
            if point_nums >= default_point_nums:
                flag = True
                break
        if flag:
            new_boxes.append([xmin,ymin,xmax,ymax])
            new_clzes.append('null_box')
            new_scores.append(score)
    new_boxes.extend(shelf_boxes)
    new_clzes.extend(shelf_clzes)
    new_scores.extend(shelf_scores)
    return new_clzes,new_scores,new_boxes