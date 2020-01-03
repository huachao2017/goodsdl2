#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
killid=`ps -ef | grep alarm_order_util.py | grep -v grep | awk 'BEGIN{FS=" "}{print $2}' | head -1`
kill -9 $killid
nohup python3 -u /data/src/goodsdl2/goods/sellgoods/salesquantity/local_util/alarm_order_util.py >> /data/ai/logs/alarm_order_util.log""$today 2>&1 &