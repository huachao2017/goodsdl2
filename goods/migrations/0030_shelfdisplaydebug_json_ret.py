# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-11-21 19:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0029_shelfdisplaydebug_shelfdisplaydebuggoods'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelfdisplaydebug',
            name='json_ret',
            field=models.TextField(default=''),
        ),
    ]
