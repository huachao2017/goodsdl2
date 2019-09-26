from rest_framework import serializers
from goods.models import ShelfImage, ShelfGoods, FreezerImage



class ShelfImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfImage
        fields = ('pk', 'picid', 'shopid', 'shelfid', 'displayid', 'tlevel', 'picurl', 'source', 'rectjson', 'rectsource',
                  'score', 'equal_cnt', 'different_cnt', 'unknown_cnt', 'resultsource', 'test_server', 'create_time', 'update_time')
        read_only_fields = ('create_time',)


class ShelfGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfGoods
        fields = ('pk', 'upc', 'xmin', 'ymin', 'xmax', 'ymax', 'level', 'result', 'create_time', 'update_time')
        read_only_fields = ('level', 'result', 'create_time', 'update_time')


class FreezerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezerImage
        fields = ('pk', 'deviceid', 'ret', 'source',
                  'create_time')
        read_only_fields = ('ret', 'create_time',)

