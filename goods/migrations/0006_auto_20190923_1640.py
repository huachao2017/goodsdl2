# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-09-23 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0005_auto_20190918_1916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shelfgoods',
            name='score1',
        ),
        migrations.RemoveField(
            model_name='shelfgoods',
            name='score2',
        ),
        migrations.RemoveField(
            model_name='shelfgoods',
            name='shelfid',
        ),
        migrations.RemoveField(
            model_name='shelfgoods',
            name='shopid',
        ),
        migrations.AddField(
            model_name='shelfgoods',
            name='result',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='different_cnt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='displayid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='equal_cnt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='source',
            field=models.CharField(default='0', max_length=200),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='tlevel',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='unknown_cnt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shelfimage',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='date updated'),
        ),
    ]
