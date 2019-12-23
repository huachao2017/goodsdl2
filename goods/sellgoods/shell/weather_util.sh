#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
killid=`ps -ef | grep weather_util | grep -v grep | awk 'BEGIN{FS=" "}{print $2}' | head -1`
kill -9 $killid
nohup python3 -u /home/src/goodsdl2/goods/sellgoods/salesquantity/local_util/weather_util.py >> /home/ai/logs/weather_util.log""$today 2>&1 &