shellgoods_params={
    "spark_context":"spark://192.168.1.60:7077",
    "online_model_name":"linear",
    "test_data_save_path":"D:\\opt\\data\\linear\\predict_test\\test3.txt",
    "regressor_model_path" : {
        "linear": "D:\\opt\\code\\model\\regressor\\LinearRegressionModel2",
        "decision_tree": "D:\\opt\\code\\model\\regressor\\DecisionTreeRegressionModel",
        "gb_tree": "D:\\opt\\code\\model\\regressor\\GBTRegressionModel",
        "random_forest": "D:\\opt\\code\\model\\regressor\\RandomForestRegressionModel",
        "keras_regress":"D:\\opt\\code\\model\\regressor\\keras_regress\\"
    },
    'sales2_old_traindata': 'D:\\opt\\data\\goods\\sales2_old\\',
    'predict_shop_ids': '(3598,1284)',
    "predict_ext_days": 7,
    'order_shop_ids': [1284],
    'order_shop_isfirst': [(1284, False)],
    'shelf_display': [(1284, True)],
    "shelf_display_maxitems": 20,  # 排列单个货架最大循环次数
    "shelf_levels_max": 20000,  # 货架的最高层数
    "shelf_level_start_height": 0,  # 货架最底层起始高度 cm
    'shelf_level_redundancy_height': 8,  # 商品与上一层的 冗余高度 cm
    'shelf_top_level_height': 20,  # 最顶层货架的高度距货架最高的 距离限制  cm
    'shelf_top_level_none_width': 20,  # 最顶层没有商品的宽度 小于该值 结束重新选品
}

#########################################YOLOV3-shelf##################################################################
shelf_yolov3_params={
    'good_model_path' :'D:\\opt\\code\\model\\shelf\\ep1360-loss7.398-val_loss8.272.h5',
    'anchors_path' :'D:\\opt\\code\\github\\goodsdl2\\goods\\freezer\\keras_yolo3\\model_data\\shelf_yolo_anchors.txt',
    'classes_path' : 'D:\\opt\\code\\github\\goodsdl2\\goods\\freezer\\keras_yolo3\\model_data\\shelf_voc_classes.txt',
    'label_path':'D:\\opt\\code\\github\\goodsdl2\\goods\\freezer\\keras_yolo3\\model_data\\shelf_label_map.pbtxt',
    'score' :0.2,
    'iou' :0.45,
    'model_image_size' : (416, 416),
    'gpu_num' : 1,
    "diff_switch_iou":(False,0.6),
    "single_switch_iou_minscore":(False,0.0,0.28),
    "down_jpg":"D:\\opt\\data\\ai_data\\shelf\\down\\",
    "up_http":"http://lximages.xianlife.com",
    "up_jpg":"/g1/2020/1315/",
}


#erp_online
erp={
    "host":"123.103.16.19",
    "port":3300,
    "database":"dmstore",
    "url":"jdbc:mysql://123.103.16.19:3300/dmstore",
    "driver":"com.mysql.jdbc.Driver",
    "user":"readonly",
    "password":"fxiSHEhui2018@)@)",
}

erp_dev={
    "host":"192.168.1.52",
    "port":3306,
    "database":"dmstore",
    "url":"jdbc:mysql://192.168.1.52:3306/dmstore",
    "driver":"com.mysql.jdbc.Driver",
    "user":"work",
    "password":"UQrwsfpVZ12pvv24",
}

ms={
    "host": "10.19.68.63",
    "port": 3306,
    "database": "ls_diamond",
    "url": "jdbc:mysql://10.19.68.63:3306/ls_diamond",
    "driver": "com.mysql.jdbc.Driver",
    "user": "diamond_ro",
    "password": "IW2MPdRYeliKdgue",
}

#ucenter_online
ucenter = {
    "host":"udb-ucenter-m-1.xianlife.top",
    "port":3306,
    "database":"center",
    "url":"jdbc:mysql://udb-ucenter-m-1.xianlife.top:3306/center",
    "driver":"com.mysql.jdbc.Driver",
    "user":"fx_ro",
    "password":"G8wN4RuZ2tJAuDa9",
}

#ai_onlline
ai = {
    "host":"10.19.68.63",
    "port":3306,
    "database":"goodsdl",
    "url":"jdbc:mysql://123.103.16.19:3306/goodsdl",
    "driver":"com.mysql.jdbc.Driver",
    "user":"gpu_rw",
    "password":"jyrMnQR1NdAKwgT4",
}







crontab_sqoop_import = {
    "dmstore":{
        "env_info":["123.103.16.19","3300","readonly","fxiSHEhui2018@)@)","dmstore"],
        "tables":['shop_goods','payment','payment_detail']
    }
}