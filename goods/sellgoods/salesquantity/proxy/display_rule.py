# 陈列设计规则
import functools
# 先按code  在按 高度
def many_sort(good_a, good_b):
    if int(good_a.display_code) > int(good_b.display_code):
        return -1
    elif int(good_a.display_code) < int(good_b.display_code):
        return 1
    else:
        good_height_a = 0
        good_height_b = 0
        if good_a.is_superimpose == True:
            good_height_a = int(good_a.height)*good_a.superimpose_rows
        else:
            good_height_a = int(good_a.height)

        if good_b.is_superimpose == True:
            good_height_b = int(good_b.height)*good_b.superimpose_rows
        else:
            good_height_b = int(good_b.height)
        if good_height_a > good_height_b:
            return 1
        else:
            return -1

def sort_code_and_height(shelf_goods):
    return sorted(shelf_goods, key=functools.cmp_to_key(mycmp=many_sort))

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