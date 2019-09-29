from goods.shelfgoods.bean import goods_box

#  未考虑 空列的影响 。
class DispalyStructure():
    gbx_ins = None
    bottom_max = 20
    x_iou_min = 0.6  # 横向 偏差iou大于阈值  判定为一个列
    y_iou_max = 0.2  # 且 纵向 偏差iou小于阈值  判定为一个列
    # 获取陈列设计二维排序结构
    def __init__(self,level,value):
        # columns, columns_info,bottom_max = self.get_goods_box_columns(value)
        # goodscolumns = self.get_goods_box_location(value,columns_info,bottom_max)
        columns,goodscolumns = self.get_column(value)
        self.gbx_ins = goods_box.GoodsBox(int(level), columns, goodscolumns)


    def get_columns(self,value):
        columns = []
        colmunboxes = []

        for upc_box, i in zip(value, range(len(value))):
            (upc, is_fitting, bottom, left, width, height) = upc_box
            xmin1 = left
            ymin1 = bottom
            xmax1 = left+width
            ymax1 =  bottom+height
            box_id1 = i
            box1 = (xmin1, ymin1, xmax1, ymax1, box_id1)
            if len(columns) < 1:
                columns.append(box1)
            else:
                falg = False
                for column in columns:
                    x_iou = get_iou((xmin1, xmax1), (column[0], column[2]))
                    if x_iou > self.x_iou_min:  # xiang tong
                        falg = True
                if falg == False:
                    columns.append(box1)
        sort_column = {}
        for key in columns:
            sort_column[key[0]] = key
        a2 = sorted(sort_column.items(), key=lambda x: x[0])
        columns_col = []
        for i in range(len(a2)):
            (xmin1, ymin1, xmax1, ymax1, box_id1) = a2[i][1]
            columns_col.append((xmin1, ymin1, xmax1, ymax1, box_id1, i, 0))
        columns_row = []
        for box1, i in zip(value, range(len(value))):
            (upc, is_fitting, bottom, left, width, height) = upc_box
            xmin1 = left
            ymin1 = bottom
            xmax1 = left + width
            ymax1 = bottom + height
            box_id1 = i
            box1 = (xmin1, ymin1, xmax1, ymax1, box_id1)
            row1 = None
            col1 = None
            for ccol in columns_col:
                (xmin2, ymin2, xmax2, ymax2, box_id2, col2, row2) = ccol
                x_iou = get_iou((xmin1, xmax1), (xmin2, xmin2))
                if box_id1 != box_id2 and x_iou > self.x_iou_min:
                    row1 = row2 + 1
                    col1 = col1
                    columns_row.append((xmin1, ymin1, xmax1, ymax1, box_id1, col1, row1))
        columns_col.extend(columns_row)
        columns_col_dict = {}
        for i in range(len(a2)):
            columns_row_sort = {}
            for ccol in columns_col:
                (xmin, ymin, xmax, ymax, box_id, col, row) = ccol
                if col == i:
                    columns_row_sort[box_id] = ymin
            a3 = sorted(columns_row_sort.items(), key=lambda x: x[1],reverse=True)
            for j in range(len(a3)):
                for ccol1 in columns_col:
                    (xmin1, ymin1, xmax1, ymax1, box_id1, col1, row1) = ccol1
                    if box_id1 == a3[j][0]:
                        row1 = j
                        columns_col_dict[box_id1] = (xmin1, ymin1, xmax1, ymax1, box_id1, col1, row1)

        for key in columns_col_dict:
            gc_ins = goods_box.GoodsColumn()
            (xmin, ymin, xmax, ymax, box_id, col, row) = columns_col_dict[key]

            for box1, i in zip(value, range(len(value))):
                (upc, is_fitting, bottom, left, width, height) = upc_box
                if i == box_id:
                    gc_ins.is_fitting = is_fitting
                    gc_ins.location_left = left
                    gc_ins.location_bottom = bottom
                    gc_ins.location_height = height
                    gc_ins.location_weight = width
                    gc_ins.upc = upc
            gc_ins.location_column = col
            gc_ins.location_row = row
            gc_ins.location_box = (xmin, ymin, xmax, ymax)
            gc_ins.box_id = box_id
            colmunboxes.append(gc_ins)
        return len(columns), colmunboxes




    def get_goods_box_columns(self,value):
        columns = 0
        columns_info = {}
        bottoms= []
        for upc_box in value:
            (upc, is_fitting, bottom, left, width, height) = upc_box
            bottoms.append(bottom+height)
        bottom_max = max(bottoms)


        for upc_box in value:
            (upc,is_fitting,bottom,left,width,height) =upc_box
            if bottom_max - int(bottom)-int(height) <=self.bottom_max:
                # columns_info['left_start_location'] = left
                # columns_info['min_width'] = width
                columns_info[columns] = (left,width)
                columns += 1
        return columns,columns_info,bottom_max

    def get_goods_box_location(self,value,columns_info,bottom_max):
        goodscolumns = []
        box_id_0 =0
        for upc_box in value:
            (upc,is_fitting, bottom, left, width, height) = upc_box
            goodscolumn_ins = goods_box.GoodsColumn()
            if bottom_max - int(bottom) - int(height)  <= self.bottom_max:
                for i in columns_info:
                    if left == columns_info[i][0] and width == columns_info[i][1] :
                        goodscolumn_ins.upc = upc
                        goodscolumn_ins.is_fitting = is_fitting
                        goodscolumn_ins.location_column = i
                        goodscolumn_ins.location_row = 0
                        goodscolumn_ins.location_left = left
                        goodscolumn_ins.location_bottom = bottom
                        goodscolumn_ins.box_id = box_id_0
            else:
                goodscolumn_ins.upc = upc
                goodscolumn_ins.is_fitting = is_fitting
                goodscolumn_ins.location_column = self.get_column(left,width,columns_info)
                goodscolumn_ins.location_left = left
                goodscolumn_ins.location_row = self.get_row(goodscolumns,bottom,goodscolumn_ins.location_column)
                goodscolumn_ins.location_bottom = bottom
                goodscolumn_ins.box_id = box_id_0
            goodscolumns.append(goodscolumn_ins)
            box_id_0+=1
        return goodscolumns
    def get_row(self,goodscolumns,bottom,column):
        bottoms= []
        for i in range(len(goodscolumns)):
            gc_ins = goodscolumns[i]
            if column == gc_ins.location_column:
                bottoms.append(gc_ins.location_bottom)
        bottoms.append(bottom)
        bottoms = sorted(bottoms)
        for i in range(len(bottoms)):
            if bottom == bottoms[i]:
                return i
        return 0
    def get_column(self,left,width,columns_info):
        column_iou = {}
        for key in columns_info:
            (i_left, i_width) = columns_info[key]
            x1 = (left, width)
            x2 = (i_left, i_width)
            x_iou = get_x_iou(x1, x2)
            column_iou[key] = x_iou
        a2 = sorted(column_iou.items(), key=lambda x: x[1],reverse=True)
        a2 = list(a2)
        return a2[0][0]

def get_x_iou(x1,x2):
    (x1_left,x1_width) = x1
    (x2_left, x2_width) = x1
    x1_max = x1_left+x1_width
    x2_max = x2_left+x2_width
    x_min = min(x1_left,x2_left)
    x_max = max(x1_max,x2_max)
    x_b = x_max - x_min
    x_j = x1_width+x2_width - x_b
    return float(x_j/(x_b+0.001))


def get_iou(x1,x2):
    (x1_min,x1_max) = x1
    (x2_min, x2_max) = x2
    x_min = min(x1_min,x2_min)
    x_max = max(x1_max,x2_max)
    x_b = x_max - x_min
    x_j = x1_max-x1_min+x2_max-x2_min - x_b
    return float(x_j/(x_b+0.001))




