import  math


"""
    起订量及上限下限规则
    param:sales_order_ins 订货对象
    param:isfir 是否首次下单
    return 订单对象
"""
def rule_start_sum(sales_order_inss):
    for sales_order_ins in sales_order_inss :
        # 订货第一目标为达到上限
        if sales_order_ins.stock - sales_order_ins.predict_sale <= sales_order_ins.start_max:  #  28
            sales_order_ins.order_sale = sales_order_ins.start_max - (sales_order_ins.stock - sales_order_ins.predict_sale)

        # 如果订货量<起定量且库存+预计销量>=下限就不定
        if sales_order_ins.order_sale < sales_order_ins.start_sum and sales_order_ins.stock + sales_order_ins.predict_sale >= sales_order_ins.start_min:
            sales_order_ins.order_sale = 0
        else:
            # 订货数必须满足起订量的要求
            if sales_order_ins.order_sale != sales_order_ins.start_sum:
                if sales_order_ins.order_sale > sales_order_ins.start_sum:  # 28 > 24   #
                    # 订货量大于起订量，那么只能定倍数，如订货量为5，起订量为3，那么有两个选择：3和6
                    min_order_sale = math.floor(float((sales_order_ins.order_sale/sales_order_ins.start_sum))) * sales_order_ins.start_sum
                    max_order_sale = math.ceil(float((sales_order_ins.order_sale/sales_order_ins.start_sum))) * sales_order_ins.start_sum

                else:
                    # 订货量小于等于起订量，有两个选择：0或者起订量
                    min_order_sale = 0
                    max_order_sale = sales_order_ins.start_sum

                if max_order_sale+sales_order_ins.stock > sales_order_ins.start_max:
                    # 如果上面的选择大于上限，则需二次判断
                    if min_order_sale+sales_order_ins.stock < sales_order_ins.start_min:
                        # 如果下面的选择小于下限，曾优先用超出的上限
                        sales_order_ins.order_sale = max_order_sale
                    else:
                        # 如果下面的选择大于等于下限，则可选择下面的选择
                        sales_order_ins.order_sale = min_order_sale
                else:
                    # 没有上面的选择小于等于上限，则选择上面的选择
                    sales_order_ins.order_sale = max_order_sale
    return sales_order_inss



"""
    首次下单规则
    param:sales_order_ins 订货对象
    return 订单对象
"""
def rule_isAndNotFir(sales_order_ins):
    if sales_order_ins.predict_sale != None and sales_order_ins.predict_sale > 0 :  # 优先保证订货空间能容纳订货量
        if sales_order_ins.max_stock - sales_order_ins.stock > sales_order_ins.predict_sale:  # 剩余空间大于销量 订销量
            sales_order_ins.order_sale = sales_order_ins.predict_sale
        else:
            if sales_order_ins.max_stock - sales_order_ins.stock  > 0: # 剩余空间小于销量 订剩余空间
                sales_order_ins.order_sale = sales_order_ins.max_stock - sales_order_ins.stock
    else:
        if sales_order_ins.max_stock - sales_order_ins.stock > 0:
            sales_order_ins.predict_sale = 0
            sales_order_ins.order_sale = sales_order_ins.max_stock - sales_order_ins.stock
    if sales_order_ins.order_sale <= 0 :
        return None
    return sales_order_ins



