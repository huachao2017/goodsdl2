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
    "search_point": "imagesearch.cn-shanghai.aliyuncs.com",
    "sleep_time" : 0.3,
}

aliyun_instance2={
    "AccessKeyID" : "LTAI4Fi33wJV958cakMBQxKZ",
    "AccessKeySecret" : "cJRZsV2ayTAhSLhZWiuzBHrgHK2uhq",
    "region" : "cn-shanghai",
    "instance_name" : "hsimgsearch1",
    "min_score" : 5,
    "search_point": "imagesearch.cn-shanghai.aliyuncs.com",
    "sleep_time" : 0.3,
}

######################################common#####################################################################
common_params={
    'freezer_check_yolov3_switch':True, # 冰柜yolo检测
    'aliyun_search_img_switch': True,# aliyun 以图搜图
}
