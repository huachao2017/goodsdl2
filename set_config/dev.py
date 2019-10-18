#########################################YOLOV3-freezer##################################################################
yolov3_params={
    'good_model_path' :'/home/ai/model/freezer/ep3408-loss42.201-val_loss42.072.h5',
    'anchors_path' :'./goods/freezer/keras_yolo3/model_data/yolo_anchors.txt',
    'classes_path' : './goods/freezer/keras_yolo3/model_data/voc_classes.txt',
    'label_path':'./goods/freezer/keras_yolo3/model_data/goods_label_map.pbtxt',
    'score' :0.25,
    'iou' :0.45,
    'model_image_size' : (416, 416),
    'gpu_num' : 1,
    "diff_switch_iou":(True,0.6),
    "single_switch_iou_minscore":(True,0.0,0.3)
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
    'predict_shop_ids':'(3598,1284)',
    "predict_ext_days":7,
    'order_shop_ids':'(1284)'
}
erp={
    "host":"123.103.16.19",
    "port":3300,
    "database":"goodsdl",
    "url":"jdbc:mysql://123.103.16.19:3300/dmstore",
    "driver":"com.mysql.jdbc.Driver",
    "user":"readonly",
    "password":"fxiSHEhui2018@)@)",
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
######################################common#####################################################################
common_params={
    'freezer_check_yolov3_switch':True, # 冰柜yolo检测
    'aliyun_search_img_switch': False,# aliyun 以图搜图
    'baidu_ai_search_img_switch': True,# 百度AI 以图搜图
}
