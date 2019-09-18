from rest_framework import serializers
from goods.models import ShelfImage, ShelfGoods, FreezerImage



class ShelfImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfImage
        fields = ('pk', 'shopid', 'shelfid', 'picurl', 'rectjson', 'image_name',
                  'create_time')
        read_only_fields = ('create_time',)


class ShelfGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfGoods
        fields = ('pk', 'shopid', 'shelfid', 'score1', 'score2', 'upc', 'xmin', 'ymin', 'xmax', 'ymax', 'level', 'create_time', 'update_time')
        read_only_fields = ('shopid', 'shelfid', 'score1', 'score2', 'level','create_time',)


class FreezerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezerImage
        fields = ('pk', 'deviceid', 'ret', 'source',
                  'create_time')
        read_only_fields = ('ret', 'create_time',)

