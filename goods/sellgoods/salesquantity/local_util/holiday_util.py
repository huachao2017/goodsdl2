import json
import requests
import time
import datetime
def get_data(date='2018-10-15'):
    try:
        server_url = "http://www.easybots.cn/api/holiday.php?d="
        req = requests.get(server_url + date)
        vop_data = json.loads(req.text)
        date = date.split("-")[0]+date.split("-")[1]+date.split("-")[2]
        return vop_data[date]
    except:
        return 0

def process():
    date = '2021-11-19'
    for i in range(1200):
        start_date_i = str(
            (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(
                days=-i)).strftime("%Y-%m-%d"))
        type = get_data(date)
        if type is None:
            type = 0
        print (start_date_i+","+str(type))
        time.sleep(0.5)

if __name__=='__main__':
    process()