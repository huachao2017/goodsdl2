# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-11-13 16:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0024_firstgoodsselection_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firstgoodsselection',
            name='predict_sales_num',
            field=models.FloatField(default=0.0),
        ),
    ]