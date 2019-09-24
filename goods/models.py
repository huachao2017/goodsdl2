from django.db import models
import datetime
from django.conf import settings

class ShelfImage(models.Model):
    picid = models.IntegerField(default=0, db_index=True)
    shopid = models.IntegerField(default=0, db_index=True)
    shelfid = models.CharField(default=0, max_length=100, db_index=True)
    displayid = models.IntegerField(default=0)
    tlevel = models.IntegerField(default=0)
    picurl = models.CharField(max_length=200, default='0')
    source = models.CharField(max_length=200, default='0')
    rectjson = models.TextField(default='')
    rectsource = models.CharField(max_length=200, default='0')
    score = models.IntegerField(default=0)
    equal_cnt = models.IntegerField(default=0)
    different_cnt = models.IntegerField(default=0)
    unknown_cnt = models.IntegerField(default=0)
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
    create_time = models.DateTimeField('date created', auto_now_add=True,db_index=True)
    update_time = models.DateTimeField('date updated', auto_now=True)


def image_upload_source(instance, filename):
    now = datetime.datetime.now()
    return '{}/{}/{}/{}/{}_{}_{}'.format(settings.DETECT_DIR_NAME, instance.deviceid, now.strftime('%Y%m'),
                                         now.strftime('%d%H'), now.strftime('%M%S'), str(now.time()), filename)


class FreezerImage(models.Model):
    deviceid = models.CharField(max_length=20, default='0', db_index=True)
    ret = models.TextField(default='')
    source = models.ImageField(max_length=200, upload_to=image_upload_source)
    create_time = models.DateTimeField('date created', auto_now_add=True, db_index=True)

