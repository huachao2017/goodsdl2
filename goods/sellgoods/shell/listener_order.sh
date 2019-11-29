#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
killid = `ps -ef | grep listener_order | awk 'BEGIN{FS=" "}{print $2}' | head -1`
kill -9 $killid
nohup python3 /home/src/goodsdl2/goods/sellgoods/salesquantity/service/order_version_4/listener_order.py >> /home/ai/logs/listener_order.log""$today 2>&1 &