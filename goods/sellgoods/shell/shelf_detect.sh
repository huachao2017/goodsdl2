#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
killid=`ps -ef | grep detect_shelf_service.py | grep -v grep | awk 'BEGIN{FS=" "}{print $2}' | head -1`
kill -9 $killid
nohup python3 -u /home/src/goodsdl2/goods/shelf_recognize/detect_shelf_service.py >> /data/ai/logs/detect_shelf_service.log""$today 2>&1 &