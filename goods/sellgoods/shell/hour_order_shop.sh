#!/bin/bash
source /etc/profile
today=`date +"%Y-%m-%d"`
nohup python3 /home/src/goodsdl2/goods/sellgoods/salesquantity/service/generate_order_shop.py >> /home/ai/logs/order_shop.log""$today 2>&1 &