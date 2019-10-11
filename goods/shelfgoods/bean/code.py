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
    12:"from aliyun success",
    13:"from aliyun failed",
    14:"from aliyun wz",
    15:"from aliyun error",
    16:"error index"

}

code_5 = 5 # 相等列中，检测框多的
code_6 = 6 # 相等列中，陈列设计是空列
code_7 = 7 # 小于陈列设计中， 该值未进入比较
code_8 = 8 # 大于陈列设计中，该值未进入比较
code_9 = 9 # 有错层 不进行比较
code_10 = 10 # 黑盒子 不进入比较
code_11 = 11 # 从数据库获取的result
code_12 = 12 # 阿里云返回 正确比较结果
code_13 = 13 # 阿里云没有比对上
code_14 = 14 #阿里云没有搜索到
code_15 = 15 #阿里云搜索时有错
code_16 = 16 #陈列设计没有对上
code_17 = 17 #未知错误 未对框生成col 和 row

match_result={
    True:1,
    False:2,
    None:3,
}

filter_code ={
    0:[1,12],
    1:[2,5,6,7,8,13,16],
    2:[3,4,9,10,14,15]
}