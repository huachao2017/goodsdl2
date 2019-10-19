#!/bin/bash
today=`date +"%Y-%m-%d"`
nohup python3 /home/src/goodsdl2/goods/sellgoods/salesquantity/service/day_train_service.py >> /home/ai/logs/sales_predict.log""$today 2>&1 &