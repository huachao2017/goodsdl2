# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-10-23 16:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0017_auto_20191018_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='ai_sales_order',
            name='multiple',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ai_sales_order',
            name='start_max',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ai_sales_order',
            name='start_min',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ai_sales_order',
            name='start_sum',
            field=models.IntegerField(default=0),
        ),
    ]