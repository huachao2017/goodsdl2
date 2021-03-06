# Generated by Django 2.2.4 on 2019-08-15 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShelfImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopid', models.IntegerField(db_index=True, default=0)),
                ('shelfid', models.IntegerField(db_index=True, default=0)),
                ('picurl', models.CharField(default='0', max_length=200)),
                ('image_name', models.CharField(default='', max_length=200)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
            ],
        ),
        migrations.CreateModel(
            name='ShelfGoods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopid', models.IntegerField(db_index=True, default=0)),
                ('shelfid', models.IntegerField(db_index=True, default=0)),
                ('score1', models.FloatField(default=0.0)),
                ('score2', models.FloatField(default=0.0)),
                ('upc', models.CharField(max_length=20)),
                ('xmin', models.PositiveIntegerField(default=0)),
                ('ymin', models.PositiveIntegerField(default=0)),
                ('xmax', models.PositiveIntegerField(default=0)),
                ('ymax', models.PositiveIntegerField(default=0)),
                ('level', models.IntegerField(default=-1)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date created')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='date updated')),
                ('shelf_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shelf_image_goods', to='goods.ShelfImage')),
            ],
        ),
    ]
