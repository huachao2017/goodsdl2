#!/bin/bash
today=`date +"%Y-%m-%d"`
ps -ef | grep workflow_deamon | grep -v grep | awk '{print $2}' | xargs kill -9
nohup python3 -u /home/src/goodsdl2/goods/shelfdisplay/workflow_deamon_process.py >> /home/src/goodsdl2/logs/shelfdisplay.log""$today 2>&1 &
