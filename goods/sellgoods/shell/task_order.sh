#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
nohup python3 /home/src/goodsdl2/goods/sellgoods/salesquantity/service/order_version_3/task_order.py >> /home/ai/logs/task_order.log""$today 2>&1 &