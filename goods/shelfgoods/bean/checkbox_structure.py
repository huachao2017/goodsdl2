from goods.shelfgoods.bean import goods_box
from goods.shelfgoods.bean.check_box_col_bean import CheckBoxCol
from goods.shelfgoods.bean import code
import logging
logger = logging.getLogger("detect")
class CheckBoxStructure:
    x_iou_min = 0.6  # 横向 偏差iou大于阈值  判定为一个列
    y_iou_max = 0.2  # 且 纵向 偏差iou小于阈值  判定为一个列

    none_col = 0.88  # 空列 左右的占两个框与该均值的 比  > 该阈值 认为中间存在空列
    gbx_ins=None
    def __init__(self,level,value):
        columns, columnboxs = self.get_column(value)
        self.gbx_ins = goods_box.GoodsBox(int(level), columns, columnboxs)


    def get_column(self,value):
        columns = []
        colmunboxes=[]
        for box1, i in zip(value, range(len(value))):
            (xmin1, ymin1, xmax1, ymax1, box_id1,result1,upc1,is_label1,col1,row1,process_code1) = box1
            if len(columns)<1:
                columns.append(box1)
            else:
                falg = False
                for column in columns:
                    x_iou = get_iou((xmin1,xmax1),(column[0],column[2]))
                    if x_iou > self.x_iou_min: # xiang tong
                        falg=True
                if falg == False:
                    columns.append(box1)
        sort_column = {}
        for key in columns:
            sort_column[key[0]] = key
        a2 = sorted(sort_column.items(), key=lambda x: x[0])
        columns_col = []
        for i in range(len(a2)):
            (xmin1, ymin1, xmax1, ymax1, box_id1,result1,upc1,is_label1,col1,row1,process_code1) = a2[i][1]
            columns_col.append((xmin1, ymin1, xmax1, ymax1, box_id1,i,0))
        columns_row = []
        for box1, i in zip(value, range(len(value))):
            (xmin1, ymin1, xmax1, ymax1, box_id1,result1,upc1,is_label1,col1,row1,process_code1) = box1
            row1=None
            col1=None
            for ccol in columns_col:
                (xmin2, ymin2, xmax2, ymax2, box_id2,col2,row2) = ccol
                x_iou = get_iou((xmin1, xmax1), (xmin2, xmin2))
                if box_id1 != box_id2 and x_iou >= self.x_iou_min:
                    row1=row2+1
                    col1=col2
                    columns_row.append((xmin1, ymin1, xmax1, ymax1, box_id1,col1,row1))
        logger.info("columns_row" + str(len(columns_row)))
        columns_col.extend(columns_row)
        logger.info("ckbox len1:"+str(len(columns_col)))
        columns_col_dict = {}
        for i in range(len(a2)):
            columns_row_sort = {}
            for ccol in columns_col:
                (xmin, ymin, xmax, ymax, box_id, col, row) = ccol
                if col==i:
                    columns_row_sort[box_id] = ymin
            a3 = sorted(columns_row_sort.items(), key=lambda x: x[1])
            for j in range(len(a3)):
                for ccol1 in columns_col:
                    (xmin1, ymin1, xmax1, ymax1, box_id1, col1, row1) = ccol1
                    if box_id1 == a3[j][0]:
                        row1=j
                        columns_col_dict[box_id1] = (xmin1, ymin1, xmax1, ymax1, box_id1, col1, row1)
        logger.info ("ckbox len2:"+str(len(columns_col_dict.keys())))
        for box1, i in zip(value, range(len(value))):
            (xmin1, ymin1, xmax1, ymax1, box_id1, result1, upc1, is_label1, col1, row1, process_code1) = box1
            falg = False
            gc_ins = goods_box.GoodsColumn()
            for key in columns_col_dict:
                (xmin, ymin, xmax, ymax, box_id, col, row) = columns_col_dict[key]
                if box_id1 == box_id:
                    gc_ins.location_column = col
                    gc_ins.location_row = row
                    gc_ins.location_box = (xmin, ymin, xmax, ymax)
                    gc_ins.box_id = box_id
                    falg = True
                    gc_ins.upc = upc1
                    gc_ins.process_code = process_code1
                    gc_ins.is_label = is_label1
                    gc_ins.result = result1
            if falg == False:
                gc_ins.location_column = col1
                gc_ins.location_row = row1
                gc_ins.location_box = (xmin1, ymin1, xmax1, ymax1)
                gc_ins.box_id = box_id1
                gc_ins.upc = upc1
                gc_ins.process_code = code.code_18
                gc_ins.is_label = is_label1
                gc_ins.result = result1
            colmunboxes.append(gc_ins)


        return len(columns),colmunboxes

def get_iou(x1,x2):
    (x1_min, x1_max) = x1
    (x2_min, x2_max) = x2
    x_min = min(x1_min, x2_min)
    x_max = max(x1_max, x2_max)
    x_b = x_max - x_min
    x_j = x1_max - x1_min + x2_max - x2_min - x_b
    return float(x_j / (x_b + 0.001))