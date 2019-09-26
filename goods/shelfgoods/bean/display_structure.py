from goods.shelfgoods.bean import goods_box

#  未考虑 空列的影响 。
class DispalyStructure():
    gbx_ins = None
    bottom_max = 20
    # 获取陈列设计二维排序结构
    def __init__(self,level,value):
        columns, columns_info,bottom_max = self.get_goods_box_columns(value)
        print (columns)
        print (columns_info)
        goodscolumns = self.get_goods_box_location(value,columns_info,bottom_max)
        self.gbx_ins = goods_box.GoodsBox(int(level), columns, goodscolumns)


    def get_goods_box_columns(self,value):
        columns = 0
        columns_info = {}
        bottoms= []
        for upc_box in value:
            (upc, is_fitting, bottom, left, width, height) = upc_box
            bottoms.append(bottom)
        bottom_max = max(bottoms)


        for upc_box in value:
            (upc,is_fitting,bottom,left,width,height) =upc_box
            if bottom_max - int(bottom) <=self.bottom_max:
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
            if bottom_max - int(bottom)  <= self.bottom_max:
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
        a2=list(a2)
        print (a2)
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




