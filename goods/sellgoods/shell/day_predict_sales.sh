#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
nohup python3 /data/src/goodsdl2/goods/sellgoods/salesquantity/service/day_train_service.py >> /data/ai/logs/sales_predict.log""$today 2>&1 &