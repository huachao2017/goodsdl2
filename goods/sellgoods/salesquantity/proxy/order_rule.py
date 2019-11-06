import  math

#  起订量规则  上下限
def rule_start_sum(upc_ordersales):
    for upc in upc_ordersales:
        (order_sale, sale, min_stock, max_stock, stock, multiple, start_sum, start_min, start_max) = upc_ordersales[upc]
        # 订货第一目标为达到上限
        if stock - sale <= start_max:  #  28
            order_sale = start_max - (stock - sale)
        # 订货数必须满足起订量的要求
        if order_sale != start_sum:
            if order_sale > start_sum:  # 28 > 24   #
                # 订货量大于起订量，那么只能定倍数，如订货量为5，起订量为3，那么有两个选择：3和6
                min_order_sale = math.floor(float((order_sale/start_sum))) * start_sum
                max_order_sale = math.ceil(float((order_sale/start_sum))) * start_sum

            else:
                # 订货量小于等于起订量，有两个选择：0或者起订量
                min_order_sale = 0
                max_order_sale = start_sum

            if max_order_sale > start_max:
                # 如果上面的选择大于上限，则需二次判断
                if min_order_sale < start_min:
                    # 如果下面的选择小于下限，曾优先用超出的上限
                    order_sale = max_order_sale
                else:
                    # 如果下面的选择大于等于下限，则可选择下面的选择
                    order_sale = min_order_sale
            else:
                # 没有上面的选择小于等于上限，则选择上面的选择
                order_sale = max_order_sale

        upc_ordersales[upc] = (order_sale, sale, min_stock, max_stock, stock, multiple, start_sum, start_min, start_max)
    return upc_ordersales




#  是否首次下单规则
def rule_isAndNotFir(max_stock,min_stock,stock,upc_ordersales,upc,sale,multiple,start_sum,isfir=False):
    start_min = max(int(max_stock/2),min_stock)
    start_max = max_stock
    if isfir:
        if max_stock - min_stock <= 0:
            upc_ordersales[upc] = (max_stock, 0, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)
        else:
            if max_stock - stock > 0:
                upc_ordersales[upc] = (max_stock - stock, 0, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)

    else:
        if sale != 0 and sale != None :
            if max_stock - stock > sale:
                upc_ordersales[upc] = (sale, sale, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)
            else:
                if max_stock - stock > 0:
                    upc_ordersales[upc] = (max_stock - stock, sale, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)
    return upc_ordersales