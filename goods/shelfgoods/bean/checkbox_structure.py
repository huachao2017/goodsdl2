from goods.shelfgoods.bean import goods_box


class CheckBoxStructure:
    x_iou_min = 0.8  # 横向 偏差iou大于阈值  判定为一个列
    y_iou_max = 0.2  # 且 纵向 偏差iou小于阈值  判定为一个列
    none_col = 0.88  # 空列 左右的占两个框 与该均值的 比  > 该阈值 认为中间存在空列
    gbx_ins=None
    def __init__(self,level,value):
        columns, columnboxs = self.get_goods_box_info(value)
        self.gbx_ins = goods_box.GoodsBox(int(level), columns, columnboxs)

    def get_goods_box_info(self,value):
        columns = 0
        iou_t = []
        lefts = {}
        bottoms = {}
        columnboxs = []
        for box1,i in zip(value,range(len(value))):
            (xmin1, ymin1, xmax1, ymax1) = box1
            lefts[i] = xmin1
            bottoms[i] = 5000 - ymin1
            for box2,j in zip(value,range(len(value))):
                (xmin2, ymin2, xmax2, ymax2) = box2
                if i != j :
                    x_iou = get_iou((xmin1,xmax1),(xmin2,xmax2))
                    y_iou = get_iou((ymin1,ymax1),(ymin2,ymax2))
                    if x_iou > self.x_iou_min and y_iou < self.y_iou_max:
                        iou_t.append((i,j))

        if len(iou_t) > 0: # 有堆叠的商品
            columns, columnboxs = self.process_goods_col(iou_t,value,bottoms)
        else:
            a2 = sorted(lefts.items(), key=lambda x: x[1])
            columns = len(list(a2))
            for key,col in zip(a2,range(len(a2))):
                gc_ins = goods_box.GoodsColumn()
                gc_ins.location_column = col
                gc_ins.location_row = 0
                gc_ins.location_box = value[key[0]]
                columnboxs.append(gc_ins)
        return columns, columnboxs

    def process_goods_col(self,iou_t,value,bottoms):
        cols = [[list(iou_t[0])]]
        new_cols = []
        for key in iou_t[1:]:
            (i,j) = key
            flag = False
            for col in cols:
                if i in col or j in col:
                    col.append(i)
                    col.append(j)
                    flag = True

            if flag == False:
                cols.append([i,j])

        for col in cols:
            col_dis = list(set(col))
            new_cols.append(col_dis)

        col_data=[]
        new_cols2 = []
        for col in new_cols:
            for col_1 in col:
                if col_1 in col_data:
                    col.remove(col_1)
                else:
                    col_data.extend(col)
            new_cols2.append(col)

        col_left={}
        for col,key in zip(new_cols2,range(len(new_cols2))):
            xmin = value[col[0]][0]
            col_left[key] = xmin
        a2 = sorted(col_left.items(), key=lambda x: x[1])

        new_cols3 = []
        for key in a2:
            new_cols3.append(new_cols2[key[0]])

        # 按从每层的低部 ，往上排列
        new_cols4 = []
        for col in new_cols3:
            rows = []
            ymins = {}
            for col1 in col:
                ymin = bottoms[col1]
                ymins[col1] = ymin
            ymins_row = sorted(col_left.items(), key=lambda x: x[1])
            for ymins_key in ymins_row:
                rows.append(ymins_key[0])
            new_cols4.append(rows)

        # 取每一层的第0个框
        col_min_max = {}
        for col,i in zip(new_cols4,range(len(new_cols4))):
            xmin,xmax = value[col[0]][0], value[col[0]][2]
            col_min_max[i] = (xmin,xmax)
        new_cols5 = self.add_none_col(col_min_max,new_cols4)
        colmunboxes = []
        columns = len(new_cols5)
        for i,col in zip(new_cols5,range(len(new_cols5))):
            if len(col) > 0 :
                for j,col1 in zip(col,range(len(col))):
                    gc_ins = goods_box.GoodsColumn()
                    gc_ins.location_column = i
                    gc_ins.location_row = j
                    gc_ins.location_box = value[col1]
                    colmunboxes.append(gc_ins)
            else:
                continue
        return columns,colmunboxes

    # 添加空列
    def add_none_col(self,col_min_max,new_cols4):
        new_cols5 = []
        keys = list(col_min_max.keys())
        for i,key in zip(range(len(keys)),keys):
            xmin1,xmax1 = col_min_max[key]
            int_s = 0
            if i+1 < len(keys)-1:
                key_j = keys[i+1]
                xmin2,xmax2 = col_min_max[key_j]
                avg_weight = ((xmax2-xmin2)+(xmax1-xmin1)) / 2
                int_s = int((xmin2 - xmin1)/avg_weight)
                float_s = float((xmin2 - xmin1)/avg_weight)
                if float_s - int_s > self.none_col:
                    int_s = int_s+1
            if int_s > 0 :
                for j in range(int_s):
                    new_cols5.append([])
            else:
                new_cols5.append(new_cols4[key])
        return new_cols5






def get_iou(x1,x2):
    (x1_min,x1_max) = x1
    (x2_min, x2_max) = x2
    x_min = min(x1_min,x2_min)
    x_max = max(x1_max,x2_max)
    x_b = x_max - x_min
    x_j = x1_max-x1_min+x2_max-x2_min - x_b
    return float(x_j/x_b)

