# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-10-14 17:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0014_shelfgoods_baidu_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShelfGoods2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upc', models.CharField(max_length=20)),
                ('xmin', models.PositiveIntegerField(default=0)),
                ('ymin', models.PositiveIntegerField(default=0)),
                ('xmax', models.PositiveIntegerField(default=0)),
                ('ymax', models.PositiveIntegerField(default=0)),
                ('level', models.IntegerField(default=-1)),
                ('process_code', models.IntegerField(default=-1)),
                ('baidu_code', models.CharField(default='', max_length=50)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date created')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='date updated')),
            ],
        ),
        migrations.CreateModel(
            name='ShelfImage2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopid', models.IntegerField(db_index=True, default=0)),
                ('shelfid', models.IntegerField(db_index=True, default=0)),
                ('tlevel', models.IntegerField(default=0)),
                ('picurl', models.CharField(default='0', max_length=200)),
                ('source', models.CharField(default='', max_length=200)),
                ('resultsource', models.CharField(default='', max_length=200)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='date updated')),
            ],
        ),
        migrations.AddField(
            model_name='shelfgoods2',
            name='shelf_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shelf_image_goods', to='goods.ShelfImage2'),
        ),
    ]