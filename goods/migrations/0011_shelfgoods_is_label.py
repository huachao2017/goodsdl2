# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-10-08 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0010_shelfimage_test_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelfgoods',
            name='is_label',
            field=models.BooleanField(default=False),
        ),
    ]
