# Generated by Django 2.0 on 2019-12-13 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0039_remove_allworkflowbatch_erp_warehouse_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='allworkflowbatch',
            name='erp_warehouse_id',
            field=models.IntegerField(default=0),
        ),
    ]
