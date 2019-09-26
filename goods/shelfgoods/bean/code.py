result_code={
    1:'model_compare_true',
    2:'model_compare_false',
    3:'model_compare_none',
    4:'fiter_wz_box_none',
    5:'equal_col_box_many',
    6:'display_col_none',
    7:"min_display_col_notcompare",
    8:"max_display_col_notcompare",
    9:"level_error",
    10:"is_fitting",
    11:"from database",
}

code_5 = 5 # 相等列中，检测框多的
code_6 = 6 # 相等列中，陈列设计是空列
code_7 = 7 # 小于陈列设计中， 该值未进入比较
code_8 = 8 # 大于陈列设计中，该值未进入比较
code_9 = 9 # 有错层 不进行比较
code_10 = 10 # 黑盒子 不进入比较
code_11 = 11 # 从数据库获取的result
match_result={
    True:1,
    False:2,
    None:3,
}

filter_code ={
    0:[1],
    1:[2,5,6,7,8],
    2:[3,4,10]
}