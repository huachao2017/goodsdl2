import time
import datetime
class SalesPredict:
    def generate_data(self,all_data=False):
        if all_data:
            sql1 =1



    def get_date(self):
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        wd = datetime.datetime.now().weekday() + 1

        #当前周一的时间
        week_one__date = str(
            (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                days=-(wd-1))).strftime("%Y-%m-%d"))

        #获取12周以前的周一时间
        start_date =  str(
            (datetime.datetime.strptime(week_one__date, "%Y-%m-%d") + datetime.timedelta(
                days=-12*7)).strftime("%Y-%m-%d"))
        return start_date,week_one__date