# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-11-18 10:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0025_auto_20191113_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='ai_weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=2000)),
                ('create_date', models.CharField(max_length=200)),
                ('weather_type', models.CharField(max_length=2000)),
                ('temphigh', models.CharField(max_length=200)),
                ('templow', models.CharField(max_length=200)),
                ('windspeed', models.CharField(max_length=200)),
                ('winddirect', models.CharField(max_length=255)),
                ('windpower', models.CharField(max_length=200)),
                ('city_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryAreaRatio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_id', models.IntegerField(unique=True)),
                ('ratio', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='CategoryIntimacy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_ids', models.CharField(max_length=200, unique=True)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryLevelRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat_id', models.IntegerField(unique=True)),
                ('score', models.IntegerField(default=0)),
            ],
        ),
    ]
