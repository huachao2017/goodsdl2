import tushare as ts
import datetime,time
from django.db import connections

conn = connections['default']
cursor = conn.cursor()
insert_sql = "insert into cctv_news(date,title,content) values ('{}','{}','{}')"
def train():
    """
    训练
    :return:
    """
    ts.set_token("7ce740ae891be080049da0f3a3d173099ba4ab80d3555b6d2e7baf87")
    pro = ts.pro_api()


    begin = datetime.date(2006, 6, 1)
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
            daily_news_title += row[1]
            daily_news_title += ","
            daily_news_content += row[2]
            daily_news_content += ","
        # news_dict[str(d.strftime("%Y%m%d"))] = daily_all_news
        cursor.execute(insert_sql.format(date_str,daily_news_title,daily_news_content))
        time.sleep(13)
        d += delta





if __name__ == '__main__':
    train()