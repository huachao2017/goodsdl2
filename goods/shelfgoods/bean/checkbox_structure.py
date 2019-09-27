from goods.shelfgoods.bean import goods_box
from goods.shelfgoods.bean.check_box_col_bean import CheckBoxCol
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
            (xmin1, ymin1, xmax1, ymax1, box_id1) = box1
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
            (xmin1, ymin1, xmax1, ymax1, box_id1) = a2[i][1]
            columns_col.append((xmin1, ymin1, xmax1, ymax1, box_id1,i,0))
        columns_row = []
        for box1, i in zip(value, range(len(value))):
            (xmin1, ymin1, xmax1, ymax1, box_id1) = box1
            row1=None
            col1=None
            for ccol in columns_col:
                (xmin2, ymin2, xmax2, ymax2, box_id2,col2,row2) = ccol
                x_iou = get_iou((xmin1, xmax1), (xmin2, xmin2))
                if box_id1 != box_id2 and x_iou > self.x_iou_min:
                    row1=row2+1
                    col1=col1
                    columns_row.append((xmin1, ymin1, xmax1, ymax1, box_id1,col1,row1))
        columns_col.extend(columns_row)
        columns_col_dict = {}
        for i in range(a2):
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

        for key in columns_col_dict:
            gc_ins = goods_box.GoodsColumn()
            (xmin, ymin, xmax, ymax, box_id, col, row) = columns_col_dict[key]
            gc_ins.location_column = col
            gc_ins.location_row = row
            gc_ins.location_box = (xmin, ymin, xmax, ymax)
            gc_ins.box_id = box_id
            colmunboxes.append(gc_ins)
        return len(columns),colmunboxes


    def get_goods_box_info(self,value):
        cb_cols = []
        for box1,i in zip(value,range(len(value))):
            (xmin1, ymin1, xmax1, ymax1,box_id1) = box1
            ymin1 = 5000 - ymin1
            ymax1 = 5000 - ymax1
            cb_col_ins = CheckBoxCol()
            cb_col_ins.value_index = i
            cb_col_ins.xmin = xmin1
            cb_col_ins.xmax = xmax1
            cb_col_ins.c_ymin = ymin1
            cb_col_ins.c_ymax = ymax1
            cb_col_ins.box_id = box_id1
            cb_cols = self.add_cb_col(cb_col_ins,cb_cols)
        # logger.info("wei add none "+str(len(cb_cols)))
        # for cb_col in cb_cols:
        #     logger.info("wei add none " + str(cb_col.col))
        #添加空列
        # cb_cols = self.add_none_col(cb_cols)  # 方法存在问题  对列值造成变大
        # logger.info("add none " + str(len(cb_cols)))
        # for cb_col in cb_cols:
        #     logger.info("add none " + str(cb_col.col))
        cols = []
        colmunboxes=[]
        for cb_col in cb_cols:
            cols.append(cb_col.col)
            gc_ins = goods_box.GoodsColumn()
            gc_ins.location_column = cb_col.col
            gc_ins.location_row = cb_col.row
            (xmin, ymin, xmax, ymax, box_id) = value[cb_col.value_index]
            gc_ins.location_box = (xmin, ymin, xmax, ymax)
            gc_ins.box_id = box_id
            logger.info("col " + str(cb_col.col))
            logger.info("row " + str(cb_col.row))
            colmunboxes.append(gc_ins)
        columns = max(cols)+1
        logger.info("columns " + str(len(cb_cols)))
        return columns, colmunboxes

    # 加入cb_cols
    def add_cb_col(self,cb_col_ins,cb_cols):
        if len(cb_cols) == 0 :
            cb_col_ins.col = 0
            cb_col_ins.row = 0
            cb_cols.append(cb_col_ins)
        else:
            cb_col_ins.col,cb_cols = self.get_col(cb_col_ins,cb_cols)
            cb_col_ins.row,cb_cols = self.get_row(cb_col_ins,cb_cols)
            cb_cols.append(cb_col_ins)
        return cb_cols

    def add_none_col(self,cb_cols):
        sort_col = {}
        for cb_col in cb_cols:
            if cb_col.row == 0:
                sort_col[cb_col.col] = cb_col
        if len(list(sort_col.keys()))== 0 or len(list(sort_col.keys())) == 1:
            return cb_cols
        a2 = sorted(sort_col.items(), key=lambda x: x[0])
        cols = []
        for key in a2:
            cols.append(key[1])
        indexs = {}
        sum_t = 0
        for i in range(len(cols)):
            if i+1 <= len(cols)-1:
                avg_weight = (cols[i].xmax - cols[i].xmin) + (cols[i+1].xmax - cols[i+1].xmin) / 2
                t = int(cols[i + 1].xmin - cols[i].xmax / avg_weight)
                if t>= 0 and float(cols[i + 1].xmin - cols[i].xmax / avg_weight) - t > self.none_col:
                    t+=1
                    sum_t+=t
                    indexs[i+1] = i+1+sum_t

        for cb_col in cb_cols:
            for key in indexs:
                if cb_col.col == key:
                    cb_col.col = indexs[key]
        return cb_cols







    def get_row(self,cb_col_ins,cb_cols):
        row_sort = {}
        rows = []
        for cb_col in cb_cols:
            if cb_col.col == cb_col_ins.col:
                row_sort[cb_col.row] = cb_col
                rows.append(cb_col.row)
        a2 = sorted(row_sort.items(), key=lambda x: x[0])
        get_row = None
        for key in a2:
            row = key[0]
            cb_col = key[1]
            if (cb_col_ins.c_ymin+cb_col_ins.c_ymax)/2 > (cb_col.c_ymin+cb_col.c_ymax)/2:
                get_row = cb_col.row+1
        # 处理 三种情况  1 get_row 最下行   2 get_row 中间行  3 get_row 最上行
        if get_row == None:  # 最xihang
            for cb_col in cb_cols:
                if cb_col.col == cb_col_ins.col:
                    cb_col.row += 1
            return 0,cb_cols
        elif get_row > min(rows) and get_row <= max(rows):
            for cb_col in cb_cols:
                if (cb_col.c_ymin+cb_col.c_ymax) / 2 > (
                        cb_col_ins.c_ymin + cb_col_ins.c_ymax) / 2 and cb_col.row >= get_row and cb_col.col == cb_col_ins.col:
                    cb_col.row += 1
            return get_row, cb_cols
        else:
            return get_row, cb_cols


    def get_col(self,cb_col_ins,cb_cols):
        col_sort = {}
        for cb_col in cb_cols:
            if cb_col.row == 0:
                x_iou = get_iou((cb_col_ins.xmin,cb_col_ins.xmax),(cb_col.xmin,cb_col.xmax))
                y_iou = get_iou((cb_col_ins.c_ymin,cb_col_ins.c_ymax),(cb_col.c_ymin,cb_col.c_ymax))
                if x_iou > self.x_iou_min and y_iou <  self.y_iou_max : # 相同列
                    return cb_col.col,cb_cols
                else: #不同列
                    col_sort[cb_col.col] = cb_col

        a2 = sorted(col_sort.items(), key=lambda x: x[0])
        get_col = None
        cols = []
        for key in a2:
            col = key[0]
            cols.append(col)
            cb_col = key[1]
            if (cb_col_ins.xmin+cb_col_ins.xmax)/2 > (cb_col.xmin+cb_col.xmax)/2:
                get_col = cb_col.col + 1

        # 处理 三种情况  1 get_col 最左列   2 get_col 中间列  3 get_col 最右列
        if get_col == None:#最左列
            for cb_col in cb_cols:
                cb_col.col +=1
            return 0,cb_cols
        elif get_col > min(cols) and get_col <= max(cols):
            for cb_col in cb_cols:
                if (cb_col.xmin+cb_col.xmax)/2 > (cb_col_ins.xmin+cb_col_ins.xmax)/2  and cb_col.col >= get_col:
                    cb_col.col += 1
            return get_col,cb_cols
        else:
            return get_col,cb_cols

def get_iou(x1,x2):
    (x1_min,x1_max) = x1
    (x2_min, x2_max) = x2
    x_min = min(x1_min,x2_min)
    x_max = max(x1_max,x2_max)
    x_b = x_max - x_min
    x_j = x1_max-x1_min+x2_max-x2_min - x_b
    return float(x_j/(x_b+0.001))

