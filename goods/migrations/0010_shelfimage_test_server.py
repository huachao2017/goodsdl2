# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-09-26 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0009_shelfimage_resultsource'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelfimage',
            name='test_server',
            field=models.BooleanField(default=True),
        ),
    ]
