shellgoods_params={
    "spark_context":"spark://192.168.1.60:7077",
    "online_model_name":"linear",
    "test_data_save_path":"D:\\opt\\data\\linear\\predict_test\\test3.txt",
    "regressor_model_path" : {
        "linear": "D:\\opt\\code\\model\\regressor\\LinearRegressionModel2",
        "decision_tree": "D:\\opt\\code\\model\\regressor\\DecisionTreeRegressionModel",
        "gb_tree": "D:\\opt\\code\\model\\regressor\\GBTRegressionModel",
        "random_forest": "D:\\opt\\code\\model\\regressor\\RandomForestRegressionModel"
    },
    'predict_shop_ids':'(3598)',
    "predict_ext_days":7,
    'order_shop_ids': [1284],
    'order_shop_isfirst':[(1284,True)]
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