from django.db import models
import datetime
from django.conf import settings

class ShelfImage(models.Model):
    picid = models.IntegerField(default=0, db_index=True)
    shopid = models.IntegerField(default=0, db_index=True)
    shelfid = models.CharField(default='', max_length=100, db_index=True)
    displayid = models.IntegerField(default=0)
    tlevel = models.IntegerField(default=0)
    picurl = models.CharField(max_length=200, default='')
    source = models.CharField(max_length=200, default='')
    rectjson = models.TextField(default='')
    rectsource = models.CharField(max_length=200, default='')
    score = models.IntegerField(default=0)
    equal_cnt = models.IntegerField(default=0)
    different_cnt = models.IntegerField(default=0)
    unknown_cnt = models.IntegerField(default=0)
    resultsource = models.CharField(max_length=200, default='')
    test_server = models.BooleanField(default=True)
    create_time = models.DateTimeField('date created', auto_now_add=True)
    update_time = models.DateTimeField('date updated', auto_now=True)

class ShelfGoods(models.Model):
    shelf_image = models.ForeignKey(ShelfImage, related_name="shelf_image_goods", on_delete=models.CASCADE)
    upc = models.CharField(max_length=20,default='')
    xmin = models.PositiveIntegerField(default=0)
    ymin = models.PositiveIntegerField(default=0)
    xmax = models.PositiveIntegerField(default=0)
    ymax = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=-1)
    result = models.IntegerField(default=-1)
    is_label = models.BooleanField(default=False)
    process_code = models.IntegerField(default=-1)
    col = models.IntegerField(default=-1)
    row = models.IntegerField(default=-1)
    baidu_code = models.CharField(max_length=50,default='')
    create_time = models.DateTimeField('date created', auto_now_add=True,db_index=True)
    update_time = models.DateTimeField('date updated', auto_now=True)
    def __str__(self):
        return '{}-{}:{}'.format(self.pk, self.upc, self.result)


class ShelfImage2(models.Model):
    shopid = models.IntegerField(default=0, db_index=True)
    shelfid = models.IntegerField(default=0, db_index=True)
    tlevel = models.IntegerField(default=0)
    picurl = models.CharField(max_length=200, default='0')
    source = models.CharField(max_length=200, default='')
    resultsource = models.CharField(max_length=200, default='')
    create_time = models.DateTimeField('date created', auto_now_add=True)
    update_time = models.DateTimeField('date updated', auto_now=True)

class ShelfGoods2(models.Model):
    shelf_image = models.ForeignKey(ShelfImage2, related_name="shelf_image_goods", on_delete=models.CASCADE)
    upc = models.CharField(max_length=20)
    xmin = models.PositiveIntegerField(default=0)
    ymin = models.PositiveIntegerField(default=0)
    xmax = models.PositiveIntegerField(default=0)
    ymax = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=-1)
    process_code = models.IntegerField(default=-1)
    baidu_code = models.CharField(max_length=50,default='')
    create_time = models.DateTimeField('date created', auto_now_add=True,db_index=True)
    update_time = models.DateTimeField('date updated', auto_now=True)
    def __str__(self):
        return '2_{}-{}:{}'.format(self.pk, self.upc, self.result)

def image_upload_source(instance, filename):
    now = datetime.datetime.now()
    return '{}/{}/{}/{}/{}_{}_{}'.format(settings.DETECT_DIR_NAME, 'freezer', now.strftime('%Y%m'),
                                         now.strftime('%d%H'), now.strftime('%M%S'), str(now.time()), filename)


class FreezerImage(models.Model):
    deviceid = models.CharField(max_length=20, default='0', db_index=True)
    ret = models.TextField(default='')
    source = models.ImageField(max_length=200, upload_to=image_upload_source)
    visual = models.URLField(max_length=200, default='')
    create_time = models.DateTimeField('date created', auto_now_add=True, db_index=True)

class FirstGoodsSelection(models.Model):
    shopid = models.IntegerField(db_index=True)
    batch_id = models.CharField(max_length=20)
    upc = models.CharField(max_length=20)
    name = models.CharField(max_length=50, default='')
    code = models.CharField(max_length=20)
    predict_sales_amount = models.IntegerField()
    predict_sales_num = models.FloatField(default=0.0)
    template_shop_ids = models.CharField(max_length=100)
    mch_goods_code = models.CharField(max_length=100,default='')
    mch_code = models.IntegerField(default=2)
    create_time = models.DateTimeField('date created', auto_now_add=True)

class GoodsSelectionHistory(models.Model):
    shopid = models.IntegerField(db_index=True)
    batch_id = models.CharField(max_length=20)
    upc = models.CharField(max_length=20)
    name = models.CharField(max_length=50, default='')
    code = models.CharField(max_length=20)
    predict_sales_amount = models.IntegerField()
    predict_sales_num = models.FloatField(default=0.0)
    template_shop_ids = models.CharField(max_length=100)
    mch_goods_code = models.CharField(max_length=100,default='')
    mch_code = models.IntegerField(default=2)
    create_time = models.DateTimeField('date created')


class ai_sales_goods(models.Model):
    shopid = models.IntegerField()
    class_three_id = models.IntegerField()
    nextday_predict_sales = models.IntegerField()
    next_day = models.CharField(max_length=32)
    upc = models.CharField(max_length=20)
    day = models.CharField(max_length=20)
    day_sales = models.IntegerField()
    nextdays_predict_sales = models.TextField()
    day_week = models.IntegerField()
    create_time = models.DateTimeField('date created', auto_now_add=True, db_index=True)

class ai_sales_order(models.Model):
    shopid = models.IntegerField()
    erp_shop_type = models.IntegerField(default=0) #0为门店，1为批发商
    upc = models.CharField(max_length=20)
    order_sale = models.IntegerField() #订货量
    predict_sale = models.IntegerField() #预测销量
    min_stock = models.IntegerField() #最小库存
    max_stock = models.IntegerField() #最大库存
    stock = models.IntegerField() #真实库存
    multiple = models.IntegerField(default=0) #ms步长
    start_sum = models.IntegerField(default=0) #起订量
    start_min = models.IntegerField(default=0) #下限
    start_max = models.IntegerField(default=0) #上限
    create_date = models.CharField(max_length=20)
    create_time = models.DateTimeField('date created', auto_now_add=True, db_index=True)
    goods_name = models.CharField(max_length=100, default='')



class ai_weather(models.Model):
    city = models.CharField(max_length=2000)# 城市名
    create_date = models.CharField(max_length=200) #日期
    weather_type = models.CharField(max_length=2000)# 天气类型
    temphigh = models.CharField(max_length=200) #最高温度
    templow = models.CharField(max_length=200) #最低温度
    windspeed = models.CharField(max_length=200) #风速
    winddirect = models.CharField(max_length=255) #风向
    windpower = models.CharField(max_length=200) #风力
    city_id = models.CharField(max_length=200) #城市id

def goods_image_upload_source(instance, filename):
    now = datetime.datetime.now()
    return '{}/{}/{}/{}/{}_{}_{}'.format(settings.DETECT_DIR_NAME, 'goodsWH', now.strftime('%Y%m'),
                                         now.strftime('%d%H'), now.strftime('%M%S'), str(now.time()), filename)

class GoodsImage(models.Model):
    rgb_source = models.ImageField(max_length=200, upload_to=goods_image_upload_source)
    depth_source = models.ImageField(max_length=200, upload_to=goods_image_upload_source)
    table_z = models.IntegerField(default=0)
    result = models.TextField()
    create_time = models.DateTimeField('date created', auto_now_add=True,db_index=True)

class AllWorkFlowBatch(models.Model):
    batch_id = models.CharField(max_length=20, unique=True)
    uc_shopid = models.IntegerField()
    type = models.IntegerField(default=0) # 0选品-陈列-首次订货，1日常非日配订货，2日常日配订货，3补货
    select_goods_status = models.IntegerField(default=0) # 0未发起，1需计算，2正在计算，3计算结束，4计算失败
    select_goods_calculate_time = models.IntegerField(default=0) # 选品计算总时间（秒）
    auto_display_status = models.IntegerField(default=0) # 0未发起，1需计算，2正在计算，3计算结束，4计算失败
    auto_display_calculate_time = models.IntegerField(default=0) # 陈列计算总时间（秒）
    order_goods_status = models.IntegerField(default=0) # 0未发起，1需计算，2正在计算，3计算结束，4计算失败
    order_goods_calculate_time = models.IntegerField(default=0) # 订货计算总时间（秒）
    create_time = models.DateTimeField('date created', auto_now_add=True)
    update_time = models.DateTimeField('date updated', auto_now=True)

class ShelfDisplayDebug(models.Model):
    batch_id = models.CharField(max_length=20,default='0')
    uc_shopid = models.IntegerField(db_index=True,default=806)
    tz_id = models.IntegerField()
    json_ret = models.TextField(default='')
    display_source = models.CharField(max_length=200, default='')
    category_intimacy_source = models.CharField(max_length=200, default='')
    create_time = models.DateTimeField('date created', auto_now_add=True)

class ShelfDisplayDebugGoods(models.Model):
    shelf_display_debug = models.ForeignKey(ShelfImage2, related_name="shelf_display_debug_goods", on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    goods_tree_source = models.CharField(max_length=200, default='')
