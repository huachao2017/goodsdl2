# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-11-26 19:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0030_shelfdisplaydebug_json_ret'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllWorkFlowBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(max_length=20)),
                ('uc_shopid', models.IntegerField()),
                ('select_goods_status', models.IntegerField(default=0)),
                ('auto_display_status', models.IntegerField()),
                ('order_goods_status', models.IntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
            ],
        ),
        migrations.AddField(
            model_name='shelfdisplaydebug',
            name='batch_id',
            field=models.CharField(default='0', max_length=20),
        ),
        migrations.AddField(
            model_name='shelfdisplaydebug',
            name='uc_shopid',
            field=models.IntegerField(db_index=True, default=806),
        ),
        migrations.AlterField(
            model_name='firstgoodsselection',
            name='batch_id',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='goodsselectionhistory',
            name='batch_id',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='shelfdisplaydebug',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created'),
        ),
    ]
