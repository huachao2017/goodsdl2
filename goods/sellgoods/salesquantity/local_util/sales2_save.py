from goods.sellgoods.salesquantity.utils import mysql_util
from set_config import config
ai = config.ai
def write_file(salesold_inss,n):
    with open("tmp_sales_week.txt_"+str(n), 'a') as f:
        for salesold_ins in salesold_inss:
            # 103
            pristr = ("%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s,%s,%s," \
                      "%s,%s,%s") % (
                         str(salesold_ins.shop_id),
                         str(salesold_ins.upc),
                         str(salesold_ins.goods_id),
                         str(salesold_ins.first_cate_id),
                         str(salesold_ins.second_cate_id),
                         str(salesold_ins.third_cate_id),
                         str(salesold_ins.goods_name),
                         str(salesold_ins.price),
                         str(salesold_ins.city),

                         # 销量数据维度
                         str(salesold_ins.sale_1),  # 周一
                         str(salesold_ins.sale_2),  # 周二
                         str(salesold_ins.sale_3),
                         str(salesold_ins.sale_4),
                         str(salesold_ins.sale_5),
                         str(salesold_ins.sale_6),
                         str(salesold_ins.sale_7),

                         str(salesold_ins.sale_1_2_avg),  # 两个周1 平均销量
                         str(salesold_ins.sale_2_2_avg),  #
                         str(salesold_ins.sale_3_2_avg),  #
                         str(salesold_ins.sale_4_2_avg),  #
                         str(salesold_ins.sale_5_2_avg),  #
                         str(salesold_ins.sale_6_2_avg),  #
                         str(salesold_ins.sale_7_2_avg),  #

                         str(salesold_ins.sale_1_4_avg),  # 4个周1 平均销量
                         str(salesold_ins.sale_2_4_avg),  #
                         str(salesold_ins.sale_3_4_avg),  #
                         str(salesold_ins.sale_4_4_avg),  #
                         str(salesold_ins.sale_5_4_avg),  #
                         str(salesold_ins.sale_6_4_avg),  #
                         str(salesold_ins.sale_7_4_avg),  #

                         str(salesold_ins.sale_1_8_avg),  # 8个周1 平均销量
                         str(salesold_ins.sale_2_8_avg),  #
                         str(salesold_ins.sale_3_8_avg),  #
                         str(salesold_ins.sale_4_8_avg),  #
                         str(salesold_ins.sale_5_8_avg),  #
                         str(salesold_ins.sale_6_8_avg),  #
                         str(salesold_ins.sale_7_8_avg),  #

                         str(salesold_ins.sale_1_12_avg),  # 12个周1 平均销量
                         str(salesold_ins.sale_2_12_avg),  #
                         str(salesold_ins.sale_3_12_avg),  #
                         str(salesold_ins.sale_4_12_avg),  #
                         str(salesold_ins.sale_5_12_avg),  #
                         str(salesold_ins.sale_6_12_avg),  #
                         str(salesold_ins.sale_7_12_avg),  #

                         str(salesold_ins.sale_1week_avg_in),  # 1周 周中平均销量
                         str(salesold_ins.sale_1week_avg_out),  # 1周 周末平均销量
                         str(salesold_ins.sale_2week_avg_in),  # 2周 周中平均销量
                         str(salesold_ins.sale_2week_avg_out),  # 2周 周末平均销量
                         str(salesold_ins.sale_4week_avg_in),  # 4周 周中平均销量
                         str(salesold_ins.sale_4week_avg_out),  # 4周 周末平均销量
                         str(salesold_ins.sale_8week_avg_in),  # 8周 周中平均销量
                         str(salesold_ins.sale_8week_avg_out),  # 8周 周末平均销量
                         str(salesold_ins.sale_12week_avg_in),  # 12周 周中平均销量
                         str(salesold_ins.sale_12week_avg_out),  # 12周 周末平均销量

                         # 天气维度
                         str(salesold_ins.templow_1),
                         str(salesold_ins.temphigh_1),
                         str(salesold_ins.weather_type_1),
                         str(salesold_ins.windpower_1),
                         str(salesold_ins.winddirect_1),
                         str(salesold_ins.windspeed_1),

                         str(salesold_ins.templow_2),
                         str(salesold_ins.temphigh_2),
                         str(salesold_ins.weather_type_2),
                         str(salesold_ins.windpower_2),
                         str(salesold_ins.winddirect_2),
                         str(salesold_ins.windspeed_2),

                         str(salesold_ins.templow_3),
                         str(salesold_ins.temphigh_3),
                         str(salesold_ins.weather_type_3),
                         str(salesold_ins.windpower_3),
                         str(salesold_ins.winddirect_3),
                         str(salesold_ins.windspeed_3),

                         str(salesold_ins.templow_4),
                         str(salesold_ins.temphigh_4),
                         str(salesold_ins.weather_type_4),
                         str(salesold_ins.windpower_4),
                         str(salesold_ins.winddirect_4),
                         str(salesold_ins.windspeed_4),

                         str(salesold_ins.templow_5),
                         str(salesold_ins.temphigh_5),
                         str(salesold_ins.weather_type_5),
                         str(salesold_ins.windpower_5),
                         str(salesold_ins.winddirect_5),
                         str(salesold_ins.windspeed_5),

                         str(salesold_ins.templow_6),
                         str(salesold_ins.temphigh_6),
                         str(salesold_ins.weather_type_6),
                         str(salesold_ins.windpower_6),
                         str(salesold_ins.winddirect_6),
                         str(salesold_ins.windspeed_6),

                         str(salesold_ins.templow_7),
                         str(salesold_ins.temphigh_7),
                         str(salesold_ins.weather_type_7),
                         str(salesold_ins.windpower_7),
                         str(salesold_ins.winddirect_7),
                         str(salesold_ins.windspeed_7),

                         # 时间维度
                         str(salesold_ins.week_i_1),
                         str(salesold_ins.season_1),
                         str(salesold_ins.week_type_1),
                         str(salesold_ins.month_1),
                         str(salesold_ins.holiday_type_1),

                         str(salesold_ins.week_i_2),
                         str(salesold_ins.season_2),
                         str(salesold_ins.week_type_2),
                         str(salesold_ins.month_2),
                         str(salesold_ins.holiday_type_2),

                         str(salesold_ins.week_i_3),
                         str(salesold_ins.season_3),
                         str(salesold_ins.week_type_3),
                         str(salesold_ins.month_3),
                         str(salesold_ins.holiday_type_3),

                         str(salesold_ins.week_i_4),
                         str(salesold_ins.season_4),
                         str(salesold_ins.week_type_4),
                         str(salesold_ins.month_4),
                         str(salesold_ins.holiday_type_4),

                         str(salesold_ins.week_i_5),
                         str(salesold_ins.season_5),
                         str(salesold_ins.week_type_5),
                         str(salesold_ins.month_5),
                         str(salesold_ins.holiday_type_5),

                         str(salesold_ins.week_i_6),
                         str(salesold_ins.season_6),
                         str(salesold_ins.week_type_6),
                         str(salesold_ins.month_6),
                         str(salesold_ins.holiday_type_6),

                         str(salesold_ins.week_i_7),
                         str(salesold_ins.season_7),
                         str(salesold_ins.week_type_7),
                         str(salesold_ins.month_7),
                         str(salesold_ins.holiday_type_7),
                         # 地域维度
                         str(salesold_ins.city_id),
                         str(salesold_ins.week_i_1_date)
                     )
            f.write(pristr + "\n")


def save_db(salesold_inss):
    mysql_ins = mysql_util.MysqlUtil(ai)
    sql = "insert into goods_ai_sales_dim (shop_id," \
          "upc," \
          "goods_id," \
          "first_cate_id," \
          "second_cate_id," \
             "third_cate_id,"\
             "goods_name,"\
             "price,"\
             "city,"\
           "sale_1,"\
            "sale_2,"\
            "sale_3,"\
            "sale_4,"\
            "sale_5,"\
            "sale_6,"\
            "sale_7,"\
            "sale_1_2_avg,"\
            "sale_2_2_avg,"\
            "sale_3_2_avg,"\
             "sale_4_2_avg,"\
             "sale_5_2_avg,"\
             "sale_6_2_avg,"\
            "sale_7_2_avg,"\
             "sale_1_4_avg,"\
            "sale_2_4_avg,"\
            "sale_3_4_avg,"\
            "sale_4_4_avg,"\
            "sale_5_4_avg,"\
            "sale_6_4_avg,"\
           "sale_7_4_avg,"\
            "sale_1_8_avg,"\
            "sale_2_8_avg,"\
            "sale_3_8_avg,"\
             "sale_4_8_avg,"\
            "sale_5_8_avg,"\
            "sale_6_8_avg,"\
           "sale_7_8_avg,"\
             "sale_1_12_avg,"\
            "sale_2_12_avg,"\
             "sale_3_12_avg,"\
            "sale_4_12_avg,"\
             "sale_5_12_avg,"\
            "sale_6_12_avg,"\
            "sale_7_12_avg,"\
            "sale_1week_avg_in,"\
            "sale_1week_avg_out,"\
             "sale_2week_avg_in,"\
            "sale_2week_avg_out,"\
            "sale_4week_avg_in,"\
             "sale_4week_avg_out,"\
            "sale_8week_avg_in,"\
            "sale_8week_avg_out,"\
             "sale_12week_avg_in,"\
             "sale_12week_avg_out,"\
             "templow_1,"\
            "temphigh_1,"\
             "weather_type_1,"\
            "windpower_1,"\
             "winddirect_1,"\
            "windspeed_1,"\
           "templow_2,"\
            "temphigh_2,"\
             "weather_type_2,"\
            "windpower_2,"\
             "winddirect_2,"\
            "windspeed_2,"\
             "templow_3,"\
             "temphigh_3,"\
             "weather_type_3,"\
             "windpower_3,"\
             "winddirect_3,"\
             "windspeed_3,"\
             "templow_4,"\
             "temphigh_4,"\
            "weather_type_4,"\
            "windpower_4,"\
            "winddirect_4,"\
             "windspeed_4,"\
            "templow_5,"\
             "temphigh_5,"\
            "weather_type_5,"\
             "windpower_5,"\
           "winddirect_5,"\
             "windspeed_5,"\
             "templow_6,"\
             "temphigh_6,"\
            "weather_type_6,"\
             "windpower_6,"\
             "winddirect_6,"\
             "windspeed_6,"\
             "templow_7,"\
             "temphigh_7,"\
            "weather_type_7,"\
             "windpower_7,"\
             "winddirect_7,"\
            "windspeed_7,"\
             "week_i_1,"\
             "season_1,"\
             "week_type_1,"\
             "month_1,"\
             "holiday_type_1,"\
             "week_i_2,"\
             "season_2,"\
             "week_type_2,"\
             "month_2,"\
             "holiday_type_2,"\
             "week_i_3,"\
             "season_3,"\
             "week_type_3,"\
             "month_3,"\
             "holiday_type_3,"\
            "week_i_4,"\
             "season_4,"\
            "week_type_4,"\
             "month_4,"\
             "holiday_type_4,"\
             "week_i_5,"\
             "season_5,"\
             "week_type_5,"\
             "month_5,"\
            "holiday_type_5,"\
            "week_i_6,"\
             "season_6,"\
             "week_type_6,"\
             "month_6,"\
             "holiday_type_6,"\
            "week_i_7,"\
             "season_7,"\
            "week_type_7,"\
             "month_7,"\
            "holiday_type_7,"\
           "city_id,"\
            "week_i_1_date) value (%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s,%s,%s," \
          "%s,%s,%s)"
    data = []
    for salesold_ins in salesold_inss:
        try:
            data.append((
                float(salesold_ins.shop_id),
                float(salesold_ins.upc),
                float(salesold_ins.goods_id),
                float(salesold_ins.first_cate_id),
                float(salesold_ins.second_cate_id),
                float(salesold_ins.third_cate_id),
                float(salesold_ins.goods_name),
                float(salesold_ins.price),
                str(salesold_ins.city),

                # 销量数据维度
                float(salesold_ins.sale_1),  # 周一
                float(salesold_ins.sale_2),  # 周二
                float(salesold_ins.sale_3),
                float(salesold_ins.sale_4),
                float(salesold_ins.sale_5),
                float(salesold_ins.sale_6),
                float(salesold_ins.sale_7),

                float(salesold_ins.sale_1_2_avg),  # 两个周1 平均销量
                float(salesold_ins.sale_2_2_avg),  #
                float(salesold_ins.sale_3_2_avg),  #
                float(salesold_ins.sale_4_2_avg),  #
                float(salesold_ins.sale_5_2_avg),  #
                float(salesold_ins.sale_6_2_avg),  #
                float(salesold_ins.sale_7_2_avg),  #

                float(salesold_ins.sale_1_4_avg),  # 4个周1 平均销量
                float(salesold_ins.sale_2_4_avg),  #
                float(salesold_ins.sale_3_4_avg),  #
                float(salesold_ins.sale_4_4_avg),  #
                float(salesold_ins.sale_5_4_avg),  #
                float(salesold_ins.sale_6_4_avg),  #
                float(salesold_ins.sale_7_4_avg),  #

                float(salesold_ins.sale_1_8_avg),  # 8个周1 平均销量
                float(salesold_ins.sale_2_8_avg),  #
                float(salesold_ins.sale_3_8_avg),  #
                float(salesold_ins.sale_4_8_avg),  #
                float(salesold_ins.sale_5_8_avg),  #
                float(salesold_ins.sale_6_8_avg),  #
                float(salesold_ins.sale_7_8_avg),  #

                float(salesold_ins.sale_1_12_avg),  # 12个周1 平均销量
                float(salesold_ins.sale_2_12_avg),  #
                float(salesold_ins.sale_3_12_avg),  #
                float(salesold_ins.sale_4_12_avg),  #
                float(salesold_ins.sale_5_12_avg),  #
                float(salesold_ins.sale_6_12_avg),  #
                float(salesold_ins.sale_7_12_avg),  #

                float(salesold_ins.sale_1week_avg_in),  # 1周 周中平均销量
                float(salesold_ins.sale_1week_avg_out),  # 1周 周末平均销量
                float(salesold_ins.sale_2week_avg_in),  # 2周 周中平均销量
                float(salesold_ins.sale_2week_avg_out),  # 2周 周末平均销量
                float(salesold_ins.sale_4week_avg_in),  # 4周 周中平均销量
                float(salesold_ins.sale_4week_avg_out),  # 4周 周末平均销量
                float(salesold_ins.sale_8week_avg_in),  # 8周 周中平均销量
                float(salesold_ins.sale_8week_avg_out),  # 8周 周末平均销量
                float(salesold_ins.sale_12week_avg_in),  # 12周 周中平均销量
                float(salesold_ins.sale_12week_avg_out),  # 12周 周末平均销量

                # 天气维度
                float(salesold_ins.templow_1),
                float(salesold_ins.temphigh_1),
                float(salesold_ins.weather_type_1),
                float(salesold_ins.windpower_1),
                float(salesold_ins.winddirect_1),
                float(salesold_ins.windspeed_1),

                float(salesold_ins.templow_2),
                float(salesold_ins.temphigh_2),
                float(salesold_ins.weather_type_2),
                float(salesold_ins.windpower_2),
                float(salesold_ins.winddirect_2),
                float(salesold_ins.windspeed_2),

                float(salesold_ins.templow_3),
                float(salesold_ins.temphigh_3),
                float(salesold_ins.weather_type_3),
                float(salesold_ins.windpower_3),
                float(salesold_ins.winddirect_3),
                float(salesold_ins.windspeed_3),

                float(salesold_ins.templow_4),
                float(salesold_ins.temphigh_4),
                float(salesold_ins.weather_type_4),
                float(salesold_ins.windpower_4),
                float(salesold_ins.winddirect_4),
                float(salesold_ins.windspeed_4),

                float(salesold_ins.templow_5),
                float(salesold_ins.temphigh_5),
                float(salesold_ins.weather_type_5),
                float(salesold_ins.windpower_5),
                float(salesold_ins.winddirect_5),
                float(salesold_ins.windspeed_5),

                float(salesold_ins.templow_6),
                float(salesold_ins.temphigh_6),
                float(salesold_ins.weather_type_6),
                float(salesold_ins.windpower_6),
                float(salesold_ins.winddirect_6),
                float(salesold_ins.windspeed_6),

                float(salesold_ins.templow_7),
                float(salesold_ins.temphigh_7),
                float(salesold_ins.weather_type_7),
                float(salesold_ins.windpower_7),
                float(salesold_ins.winddirect_7),
                float(salesold_ins.windspeed_7),

                # 时间维度
                float(salesold_ins.week_i_1),
                float(salesold_ins.season_1),
                float(salesold_ins.week_type_1),
                float(salesold_ins.month_1),
                float(salesold_ins.holiday_type_1),

                float(salesold_ins.week_i_2),
                float(salesold_ins.season_2),
                float(salesold_ins.week_type_2),
                float(salesold_ins.month_2),
                float(salesold_ins.holiday_type_2),

                float(salesold_ins.week_i_3),
                float(salesold_ins.season_3),
                float(salesold_ins.week_type_3),
                float(salesold_ins.month_3),
                float(salesold_ins.holiday_type_3),

                float(salesold_ins.week_i_4),
                float(salesold_ins.season_4),
                float(salesold_ins.week_type_4),
                float(salesold_ins.month_4),
                float(salesold_ins.holiday_type_4),

                float(salesold_ins.week_i_5),
                float(salesold_ins.season_5),
                float(salesold_ins.week_type_5),
                float(salesold_ins.month_5),
                float(salesold_ins.holiday_type_5),

                float(salesold_ins.week_i_6),
                float(salesold_ins.season_6),
                float(salesold_ins.week_type_6),
                float(salesold_ins.month_6),
                float(salesold_ins.holiday_type_6),

                float(salesold_ins.week_i_7),
                float(salesold_ins.season_7),
                float(salesold_ins.week_type_7),
                float(salesold_ins.month_7),
                float(salesold_ins.holiday_type_7),
                # 地域维度
                float(salesold_ins.city_id),
                str(salesold_ins.week_i_1_date)
            ))
        except:
            print ("format error")
            continue
    try:
        mysql_ins.insert_many_sql(data, sql)
    except :
        print("insert db error")


