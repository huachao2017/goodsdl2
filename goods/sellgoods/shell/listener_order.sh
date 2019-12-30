#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
killid=`ps -ef | grep listener_order.py | grep -v grep | awk 'BEGIN{FS=" "}{print $2}' | head -1`
kill -9 $killid
nohup python3 -u /data/src/goodsdl2/goods/sellgoods/salesquantity/service/order_version_6/listener_order.py >> /data/ai/logs/listener_order.log""$today 2>&1 &