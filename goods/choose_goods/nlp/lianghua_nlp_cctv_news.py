import tushare as ts
import datetime,time
from django.db import connections
import pymysql
# conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)

# # conn = connections['default']
# cursor = conn.cursor()


def train():
    """
    训练
    :return:
    """
    insert_sql = "insert into cctv_news(date,title,content) values ('{}','{}','{}')"
    ts.set_token("7ce740ae891be080049da0f3a3d173099ba4ab80d3555b6d2e7baf87")
    pro = ts.pro_api()


    begin = datetime.date(2009, 6, 15)
    end = datetime.date(2020, 2, 22)
    d = begin
    delta = datetime.timedelta(days=1)
    # news_dict = {}
    while d <= end:
        print(d.strftime("%Y%m%d"))
        date_str = str(d.strftime("%Y%m%d"))
        df = pro.cctv_news(date=date_str)
        daily_news_title = ""
        daily_news_content = ""
        for index, row in df.iterrows():
            daily_news_title += str(row[1])
            daily_news_title += ","
            daily_news_content += str(row[2])
            daily_news_content += ","
        # news_dict[str(d.strftime("%Y%m%d"))] = daily_all_news
        daily_news_title.replace('"',',').replace("'",",")
        daily_news_content = daily_news_content.replace('"',',').replace("'",",")
        cursor.execute(insert_sql.format(date_str,daily_news_title,daily_news_content))
        conn.commit()
        time.sleep(13)
        d += delta

def train_02():
    """
    训练
    :return:
    """
    conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)

    # conn = connections['default']
    cursor = conn.cursor()
    insert_sql = "insert into cctv_news(date,title,content,src) values ('{}','{}','{}','{}')"

    ts.set_token("7ce740ae891be080049da0f3a3d173099ba4ab80d3555b6d2e7baf87")
    pro = ts.pro_api()

    start_date = datetime.date(2009, 6, 15)
    end = datetime.date(2020, 2, 22)
    # d = begin
    delta = datetime.timedelta(days=1)
    end_date = start_date + delta
    # news_dict = {}
    while start_date <= end:
        # print(start_date.strftime("%Y-%m-%d %H:%M:%S"))
        # print(end_date.strftime("%Y-%m-%d %H:%M:%S"))
        # date_str = str(d.strftime("%Y-%m-%d %H:%M:%S"))
        # df = pro.cctv_news(date=date_str)

        df = pro.major_news(src='新浪财经',start_date=start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date=end_date.strftime("%Y-%m-%d %H:%M:%S"),fields='title,content')
        # print(df.loc[0])

        daily_news_title = ""
        daily_news_content = ""
        for index, row in df.iterrows():
            daily_news_title += str(row[0])
            daily_news_title += ","
            daily_news_content += str(row[1])
            daily_news_content += ","
        # news_dict[str(d.strftime("%Y%m%d"))] = daily_all_news
        daily_news_title = daily_news_title.replace('"',',').replace("'",",")
        daily_news_content = daily_news_content.replace('"',',').replace("'",",")
        cursor.execute(insert_sql.format(start_date.strftime("%Y%m%d"),daily_news_title,daily_news_content,'新浪财经'))
        conn.commit()
        time.sleep(31)
        start_date += delta
        end_date += delta





if __name__ == '__main__':
    # train()
    train_02()