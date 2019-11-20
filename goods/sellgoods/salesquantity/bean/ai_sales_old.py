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
    num = 0

    # 销量数据维度
    sale_1 = 0 # 周一
    sale_2 = 0 # 周二
    sale_3 = 0
    sale_4 = 0
    sale_5 = 0
    sale_6 = 0
    sale_7 = 0

    sale_1_2_avg = 0 # 两个周1 平均销量
    sale_2_2_avg = 0  #
    sale_3_2_avg = 0  #
    sale_4_2_avg = 0  #
    sale_5_2_avg = 0  #
    sale_6_2_avg = 0  #
    sale_7_2_avg = 0  #


    sale_1_4_avg = 0 # 4个周1 平均销量
    sale_2_4_avg = 0  #
    sale_3_4_avg = 0  #
    sale_4_4_avg = 0  #
    sale_5_4_avg = 0  #
    sale_6_4_avg = 0  #
    sale_7_4_avg = 0  #

    sale_1_8_avg = 0 # 8个周1 平均销量
    sale_2_8_avg = 0  #
    sale_3_8_avg = 0  #
    sale_4_8_avg = 0  #
    sale_5_8_avg = 0  #
    sale_6_8_avg = 0  #
    sale_7_8_avg = 0  #

    sale_1_12_avg = 0 # 12个周1 平均销量
    sale_2_12_avg = 0  #
    sale_3_12_avg = 0  #
    sale_4_12_avg = 0  #
    sale_5_12_avg = 0  #
    sale_6_12_avg = 0  #
    sale_7_12_avg = 0  #

    sale_1week_avg_in = 0 # 1周 周中平均销量
    sale_1week_avg_out = 0  #1周 周末平均销量
    sale_2week_avg_in = 0  # 2周 周中平均销量
    sale_2week_avg_out = 0  # 2周 周末平均销量
    sale_4week_avg_in = 0  # 4周 周中平均销量
    sale_4week_avg_out = 0  # 4周 周末平均销量
    sale_8week_avg_in = 0  # 8周 周中平均销量
    sale_8week_avg_out = 0  # 8周 周末平均销量
    sale_12week_avg_in = 0  # 12周 周中平均销量
    sale_12week_avg_out = 0  # 12周 周末平均销量

    # 天气维度
    templow_1 = 0
    temphigh_1 = 0
    weather_type_1 = 0
    windpower_1 = 0
    winddirect_1 = 0
    windspeed_1 = 0

    templow_2 = 0
    temphigh_2 = 0
    weather_type_2 = 0
    windpower_2 = 0
    winddirect_2 = 0
    windspeed_2 = 0

    templow_3 = 0
    temphigh_3 = 0
    weather_type_3 = 0
    windpower_3 = 0
    winddirect_3 = 0
    windspeed_3 = 0

    templow_4 = 0
    temphigh_4 = 0
    weather_type_4 = 0
    windpower_4 = 0
    winddirect_4 = 0
    windspeed_4 = 0

    templow_5 = 0
    temphigh_5 = 0
    weather_type_5 = 0
    windpower_5 = 0
    winddirect_5 = 0
    windspeed_5 = 0

    templow_6 = 0
    temphigh_6 = 0
    weather_type_6 = 0
    windpower_6 = 0
    winddirect_6 = 0
    windspeed_6 = 0

    templow_7 = 0
    temphigh_7 = 0
    weather_type_7 = 0
    windpower_7 = 0
    winddirect_7 = 0
    windspeed_7 = 0

    # 时间维度
    week_i = []
    season = []
    week_type = []
    month = []
    holiday_type = []

    week_i_1 = 0
    week_i_1_date=''
    season_1 = 0
    week_type_1 = 0
    month_1 = 0
    holiday_type_1 = 0

    week_i_2 = 0
    season_2 = 0
    week_type_2 = 0
    month_2 = 0
    holiday_type_2 = 0

    week_i_3 = 0
    season_3 = 0
    week_type_3 = 0
    month_3 = 0
    holiday_type_3 = 0

    week_i_4 = 0
    season_4 = 0
    week_type_4 = 0
    month_4 = 0
    holiday_type_4 = 0

    week_i_5 = 0
    season_5 = 0
    week_type_5 = 0
    month_5 = 0
    holiday_type_5 = 0

    week_i_6 = 0
    season_6 = 0
    week_type_6 = 0
    month_6 = 0
    holiday_type_6 = 0

    week_i_7 = 0
    season_7 = 0
    week_type_7 = 0
    month_7 = 0
    holiday_type_7 = 0
    # 地域维度
    city_id = 0