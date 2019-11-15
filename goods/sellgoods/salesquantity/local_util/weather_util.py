"""

'weather_url' => 'https://api.jisuapi.com/weather/query?appkey=e22d1fbac88700a0',
'weather_url2' => 'https://api.jisuapi.com/weather2/query?appkey=e22d1fbac88700a0',

"""
import django
import os
import time
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections
import requests
import demjson
from goods.models import ai_weather

old_weather_url = 'https://api.jisuapi.com/weather2/query'
now_weather_url = 'https://api.jisuapi.com/weather/query'
def get_old_weather(start_date=None,cron=False):
    """

    :param start_date:起始时间  该时间必须小于等于当前日期
    :param end_date:截止时间 该时间必须小于等于当前日期
    :return:
    """

    #reponse = requests.get(old_weather_url,params={'appkey':'e22d1fbac88700a0','city':'','date':''})
    cursor_dmstore = connections['dmstore'].cursor()
    cursor_ai = connections['default'].cursor()
    #
    # cursor.execute('select id, mch_id from uc_shop where mch_shop_code = {}'.format(shopid))
    # (uc_shopid, mch_id) = cursor.fetchone()
    cursor_ai.execute('select MIN(create_date),MAX(create_date) from goods_ai_weather')
    (min_create_date,max_create_date) = cursor_ai.fetchone()

    cursor_dmstore.execute('select DISTINCT(owned_city) from shop where owned_city != "天津新区" ')
    results = cursor_dmstore.fetchall()
    print (results[0])

    default_min_date = '2019-11-14'
    if min_create_date is None and max_create_date is None:
        i=0
        while True:
            end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
            start_date1 = str(
                (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                    days=-i)).strftime("%Y-%m-%d"))
            i+=1
            if start_date1 == default_min_date:
                return
            if start_date is not None and start_date1 == start_date:
                return
            for city in results:
                if city[0] == '':
                    continue
                weather_ins = get_old_weather_http(city[0],start_date1)
                if weather_ins is not None:
                    ai_weather.objects.create(
                        city=weather_ins.city,
                        create_date=weather_ins.create_date,
                        weather_type =weather_ins.weather_type,
                        temphigh = int(weather_ins.temphigh),
                        templow = int(weather_ins.templow),
                        windspeed = float(weather_ins.windspeed),
                        winddirect = weather_ins.winddirect,
                        windpower = float(str(weather_ins.windpower).strip("级")),
                        city_id = int(weather_ins.city_id)
                    )

    elif min_create_date is not None and start_date is not None:
        date1 = datetime.datetime.strptime(min_create_date, "%Y-%m-%d").time()
        date2 = datetime.datetime.strptime(start_date, "%Y-%m-%d").time()
        if date2 < date1:
            i=0
            while True:
                start_date1 = str(
                    (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(
                        days=i)).strftime("%Y-%m-%d"))
                i+=1
                if min_create_date == start_date1:
                    return
                for city in results:
                    if city[0] == '':
                        continue
                    weather_ins = get_old_weather_http(city[0], start_date1)
                    if weather_ins is not None:
                        ai_weather.objects.create(
                            city=weather_ins.city,
                            create_date=weather_ins.create_date,
                            weather_type=weather_ins.weather_type,
                            temphigh=int(weather_ins.temphigh),
                            templow=int(weather_ins.templow),
                            windspeed=float(weather_ins.windspeed),
                            winddirect=weather_ins.winddirect,
                            windpower=float(str(weather_ins.windpower).strip("级")),
                            city_id=int(weather_ins.city_id)
                        )
    elif cron:
        end_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        start_date1 = str(
            (datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(
                days=-1)).strftime("%Y-%m-%d"))
        for city in results:
            if city[0] == '':
                continue
            weather_ins = get_old_weather_http(city[0], start_date1)
            if weather_ins is not None:
                ai_weather.objects.create(
                    city=weather_ins.city,
                    create_date=weather_ins.create_date,
                    weather_type=weather_ins.weather_type,
                    temphigh=int(weather_ins.temphigh),
                    templow=int(weather_ins.templow),
                    windspeed=float(weather_ins.windspeed),
                    winddirect=weather_ins.winddirect,
                    windpower=float(str(weather_ins.windpower).strip("级")),
                    city_id=int(weather_ins.city_id)
                )



def get_old_weather_http(city,date):
    print ("%s , %s" % (city,date))
    city=str(city).strip("市")
    for i in range(1,10):
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            param = old_weather_url + "?appkey=e22d1fbac88700a0&city=" + city + '&date=' + date
            reponse = requests.get(param,headers=headers).text
            print (param)
            print (reponse)
            reponse = demjson.decode(reponse)
            print (reponse)
            if reponse['status'] == 0 :
                weather_ins = Weather()
                weather_ins.create_date = reponse['result']['date']
                weather_ins.weather_type = reponse['result']['weather']
                weather_ins.temphigh = reponse['result']['temphigh']
                weather_ins.templow = reponse['result']['templow']
                weather_ins.windspeed = reponse['result']['windspeed']
                weather_ins.winddirect = reponse['result']['winddirect']
                weather_ins.windpower = reponse['result']['windpower']
                weather_ins.city = city
                weather_ins.city_id = reponse['result']['cityid']
                return weather_ins
        except:
            print ("获取天气失败")
            time.sleep(1)
            continue
    return None

class Weather:
    city=None
    create_date=None
    weather_type=None
    temphigh=None
    templow=None
    windspeed=None
    winddirect=None
    windpower=None
    city_id=None



if __name__=='__main__':
    get_old_weather(start_date=2018-11-15,cron=False)
    #get_old_weather(start_date=None,cron=True)