# 陈列设计规则

# 商品陈列排序规则0   按优先按陈列分类 排序
def sort_display_code(shelf_goods):
    display_codes = []
    for good_ins in shelf_goods:
        display_codes.append(int(good_ins.display_code))
    display_codes = list(set(display_codes))
    # 陈列分类升序排列
    display_codes.sort()
    new_shelf_goods = []
    for code in display_codes:
        for good_ins in shelf_goods:
            if int(good_ins.display_code) ==  int(code):
                new_shelf_goods.append(good_ins)

    return new_shelf_goods

# 商品陈列排序规则1   按优先高度 排序
def sort_good_height(shelf_goods):
    good_heights = []
    for good_ins in shelf_goods:
        if good_ins.is_superimpose == True:
            good_heights.append(int(good_ins.height)*good_ins.superimpose_rows)
        else:
            good_heights.append(int(good_ins.height))

    good_heights = list(set(good_heights))
    # 陈列分类降序排列
    good_heights.sort(reverse=True)
    new_shelf_goods = []
    for good_height in good_heights:
        for good_ins in shelf_goods:
            if int(good_ins.height) == int(good_height):
                new_shelf_goods.append(good_ins)
    return new_shelf_goods

# 商品陈列排序规则2   按优先体积 排序
def sort_good_volume(shelf_goods):
    good_volumes = []
    for good_ins in shelf_goods:
        if good_ins.is_superimpose == True:
            good_volumes.append(int(good_ins.height*good_ins.superimpose_rows*good_ins.width*good_ins.depth))
        else:
            good_volumes.append(int(good_ins.height * good_ins.width * good_ins.depth))
    good_volumes = list(set(good_volumes))
    # 陈列分类升序排列
    good_volumes.sort(reverse=True)
    new_shelf_goods = []
    for good_volume in good_volumes:
        for good_ins in shelf_goods:
            if int(good_ins.height*good_ins.width*good_ins.depth) == int(good_volume):
                new_shelf_goods.append(good_ins)
    return new_shelf_goods