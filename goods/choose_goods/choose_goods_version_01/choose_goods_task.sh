#!/bin/bash
today=`date +"%Y-%m-%d"`
ps -ef | grep run_calculate_task | grep -v grep | awk '{print $2}' | xargs kill -9
nohup python3 -u /data/src/goodsdl2/goods/choose_goods/choose_goods_version_01/run_calculate_task.py >> /data/src/goodsdl2/logs/run_calculate_task.log""$today 2>&1 &
