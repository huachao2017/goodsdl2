#########################################YOLOV3-freezer##################################################################
yolov3_params={
    # last ep3408-loss42.201-val_loss42.072.h5 10:30 before
    'good_model_path' :'/home/ai/model/freezer/ep532-loss52.009-val_loss53.412.h5',
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

#########################################YOLOV3-mengniu##################################################################
mengniu_yolov3_params={
    'good_model_path' :'/home/ai/model/mengniu/ep3053-loss39.789-val_loss42.951.h5',
    'anchors_path' :'./goods/freezer/keras_yolo3/model_data/mengniu_yolo_anchors.txt',
    'classes_path' : './goods/freezer/keras_yolo3/model_data/mengniu_voc_classes.txt',
    'label_path':'./goods/freezer/keras_yolo3/model_data/mengniu_label_map.pbtxt',
    'score' :0.25,
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
    "test_data_save_path":"/data/ai/data/predict_test/test3.txt",
    "regressor_model_path" : {
        "linear": "/data/ai/model/regressor/LinearRegressionModel",
        "decision_tree": "/data/ai/model/regressor/DecisionTreeRegressionModel",
        "gb_tree": "/data/ai/model/regressor/GBTRegressionModel",
        "random_forest": "/data/ai/model/regressor/RandomForestRegressionModel",
        "keras_regress":"/data/ai/model/regressor/keras_regress/"
    },
    'sales2_old_traindata':'/data/ai/data/keras_sales2_data/',
    'keras_day_sales_model_1':'/data/ai/model/regressor/keras_regress/2019-11-26_1.h5',
    # 销量预测
    'predict_shop_ids':'(3598,1284)',
    "predict_ext_days":7,
    # 订单生成
    'order_shop_ids': [1284],
    'order_shop_hour_ids':[1284], # 门店向二批订货
    'order_shop_hours':[0,7,14,19],# 补货时间
    'shop_types':[0,1], #门店类型 0：门店 1：批发商
    'day_order_time_weekday':[1,2,3,6,7],
    'yinliao_cat_ids':[110,402,501,502,201,202,203,204,205],
     # 开店期
    "start_shop": {
        1284:20191105,
        -8888:20191105
    },
    # 订货时备货天数
    "save_goods_days":{
        1284:2.5,
        4598:3.5,
        -8888:3
    },
    # 到货间隔天数
    "get_goods_days": {
        1284: 2,
        4598:1.5,
        -8888: 5
    },

    # # 起订价规则
    # "start_price" : {
    #     1284:50000
    # },
    "ms_add_url":"http://erp.aicvs.cn/automaticOrdering/addShopBuy?erpShopId={}&erpShopType={}&batchId={}",
    "sass_order_url":"https://ao.aicvs.cn/api/goods/aiNotice?sign=c8b78f1851b58e700decf423d647de1a&batch_no={}&error_msg={}",

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
