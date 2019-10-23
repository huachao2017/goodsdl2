import  math

#  起订量规则  上下限
def rule_start_sum(upc_ordersales):
    for upc in upc_ordersales:
        (order_sale, sale, min_stock, max_stock, stock, multiple, start_sum, start_min, start_max) = upc_ordersales[upc]
        if stock < sale:
            order_sale = start_sum
        if order_sale >  start_sum:
            order_sale = int(math.floor(float((order_sale - start_sum) / multiple))) * start_sum
        else:
            order_sale = start_sum
            if order_sale+stock < start_min:
                order_sale =  math.floor(float(start_min-stock)/multiple) * multiple
                if order_sale < start_min:
                    order_sale = order_sale
                elif order_sale > start_max:
                    order_sale = 0
                else:
                    order_sale = order_sale
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
        if sale is not None:
            if max_stock - stock > sale:
                upc_ordersales[upc] = (sale, sale, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)
            else:
                if max_stock - stock > 0:
                    upc_ordersales[upc] = (max_stock - stock, sale, min_stock, max_stock, stock,multiple,start_sum,start_min,start_max)
    return upc_ordersales