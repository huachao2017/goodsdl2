import tushare as ts
import datetime


def train():
    """
    训练
    :return:
    """
    ts.set_token("7ce740ae891be080049da0f3a3d173099ba4ab80d3555b6d2e7baf87")
    pro = ts.pro_api()


    begin = datetime.date(2006, 8, 7)
    end = datetime.date(2020, 1, 1)
    d = begin
    delta = datetime.timedelta(days=1)
    news_dict = {}
    while d <= end:
        print(d.strftime("%Y%m%d"))
        df = pro.cctv_news(date=str(d.strftime("%Y%m%d")))
        daily_all_news = ""
        for index, row in df.iterrows():
            daily_all_news += row[1]
            daily_all_news += ","
            daily_all_news += row[2]
            daily_all_news += ","

        news_dict[str(d.strftime("%Y%m%d"))] = daily_all_news
        daily_all_news = daily_all_news.replace('"',',').replace("'",",")
        print(daily_all_news)
        d += delta
        break



if __name__ == '__main__':
    train()