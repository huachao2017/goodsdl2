class SalesOld:
    #基本数据维度
    shop_id = 0
    upc = 0
    goods_id = 0
    first_cate_id = 0
    second_cate_id = 0
    third_cate_id = 0
    goods_name = 0
    price = 0.0
    city = ''
    # 冗余维度字段
    create_date = ''
    # 当天的销量
    num = 0
    sale_i = []  # 12 个周的平均销量
    sale_i_avg_in = [] #12 个周的平均周中销量
    sale_i_avg_out = [] #12 个周的平均周末销量
    # 天气维度
    templow = 0
    temphigh = 0
    weather_type = 0
    windpower = 0
    winddirect = 0
    windspeed = 0

    # 时间维度
    week_i= 0
    week_i_date=''
    season = 0
    week_type = 0
    month = 0
    holiday_type = 0

    # 地域维度
    city_id = 0
    y_labels = []  #下一到14天销量