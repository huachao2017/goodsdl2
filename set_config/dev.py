#########################################YOLOV3-freezer##################################################################
yolov3_params={
    # last ep3408-loss42.201-val_loss42.072.h5 10:30 before
    'good_model_path' :'/home/ai/model/freezer/ep3408-loss42.201-val_loss42.072.h5',
    'anchors_path' :'./goods/freezer/keras_yolo3/model_data/yolo_anchors.txt',
    'classes_path' : './goods/freezer/keras_yolo3/model_data/voc_classes.txt',
    'label_path':'./goods/freezer/keras_yolo3/model_data/goods_label_map.pbtxt',
    'score' :0.23,
    'iou' :0.45,
    'model_image_size' : (416, 416),
    'gpu_num' : 1,
    "diff_switch_iou":(True,0.6),
    "single_switch_iou_minscore":(True,0.0,0.28)
}

#########################################shelf_good##################################################################

aliyun_instance1={
    "AccessKeyID" : "LTAI4Ftp8inKDzFmaEWyj17P",
    "AccessKeySecret" : "mCVOzv0fABM19dTRlYlWMZdGlAoqsz",
    "region" : "cn-shanghai",
    "instance_name" : "hsimgsearch",
    "min_score" : 5,
    "min_score_top1":5,
    "search_point": "imagesearch.cn-shanghai.aliyuncs.com",
    "sleep_time" : 0.3,
}

aliyun_instance2={
    "AccessKeyID" : "LTAI4Fi33wJV958cakMBQxKZ",
    "AccessKeySecret" : "cJRZsV2ayTAhSLhZWiuzBHrgHK2uhq",
    "region" : "cn-shanghai",
    "instance_name" : "hsimgsearch1",
    "min_score" : 5,
    "min_score_top1": 5,
    "search_point": "imagesearch.cn-shanghai.aliyuncs.com",
    "sleep_time" : 0.3,
}

baidu_ai_instance1={
    "debug":True,
    "request_url" : "https://aip.baidubce.com/rest/2.0/image-classify/v1/realtime_search/product/",
    "min_score" : 0.5,
    "min_score_top1":0.5,
    "sleep_time" : 0.3,
    # "ak":"bBcxD1iD0yChCznvft3oR0sn",
    "ak":"b2ZsQXxG6ecGN5nChySaFLoE",
    # "sk":"lL3AjqaCGvmpV077t9q96dihCY2xmgTm"
    "sk":"IsVCiheGFSILn6j3vVag8hSrTEboKYDs"
}

######################################sellgoods#################################################################
shellgoods_params={
    "spark_context":"spark://10.10.11.14:7077",
    "online_model_name":"decision_tree",
    "test_data_save_path":"/home/ai/data/predict_test/test3.txt",
    "regressor_model_path" : {
        "linear": "/home/ai/model/regressor/LinearRegressionModel",
        "decision_tree": "/home/ai/model/regressor/DecisionTreeRegressionModel",
        "gb_tree": "/home/ai/model/regressor/GBTRegressionModel",
        "random_forest": "/home/ai/model/regressor/RandomForestRegressionModel"
    },
    # 销量预测
    'predict_shop_ids':'(3598,1284)',
    "predict_ext_days":7,
    # 订单生成
    'order_shop_ids': [1284],
    'order_shop_hour_ids':[1284], # 门店向二批订货
    'order_shop_hours':[0,7,14,19],# 补货时间
    'shop_types':[0,1], #门店类型 0：门店 1：批发商
    'day_order_first_classes':[''],
    # 自动陈列
    'shelf_display':[(1284,True)],
    "shelf_display_maxitems":20, # 排列单个货架最大循环次数
    "shelf_levels_max":20000,# 货架的最高层数
    "shelf_level_start_height":0,# 货架最底层起始高度 mm
    'shelf_level_redundancy_height':50,# 商品与上一层的 冗余高度 mm
    'shelf_top_level_height':200, #最顶层货架的高度距货架最高的 距离限制  mm
    'shelf_top_level_none_width': 200,#最顶层没有商品的宽度 小于该值 结束重新选品

}
# dmstore erp
erp={
    "host":"123.103.16.19",
    "port":3300,
    "database":"dmstore",
    "url":"jdbc:mysql://123.103.16.19:3300/dmstore",
    "driver":"com.mysql.jdbc.Driver",
    "user":"readonly",
    "password":"fxiSHEhui2018@)@)",
}

# ms erp
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
    "database":"ucenter",
    "url":"jdbc:mysql://udb-ucenter-m-1.xianlife.top:3306/ucenter",
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
######################################common#####################################################################
common_params={
    'freezer_check_yolov3_switch':True, # 冰柜yolo检测
    'aliyun_search_img_switch': False,# aliyun 以图搜图
    'baidu_ai_search_img_switch': True,# 百度AI 以图搜图
}
