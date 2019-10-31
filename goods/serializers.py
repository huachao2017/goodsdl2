from rest_framework import serializers
from goods.models import ShelfImage, ShelfGoods, ShelfImage2, ShelfGoods2,FreezerImage,GoodsImage

from django.conf import settings


class ShelfImageSerializer(serializers.ModelSerializer):
    source_url = serializers.SerializerMethodField()
    rect_source_url = serializers.SerializerMethodField()
    result_source_url = serializers.SerializerMethodField()
    class Meta:
        model = ShelfImage
        fields = ('pk', 'picid', 'shopid', 'shelfid', 'displayid', 'tlevel', 'picurl', 'source_url', 'rectjson', 'rect_source_url',
                  'score', 'equal_cnt', 'different_cnt', 'unknown_cnt', 'result_source_url', 'test_server', 'create_time', 'update_time')
        read_only_fields = ('create_time',)
    def get_source_url(self, shelfImage):
        request = self.context.get('request')
        if shelfImage.source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=shelfImage.source)
            return current_uri

        else:
            return None
    def get_rect_source_url(self, shelfImage):
        request = self.context.get('request')
        if shelfImage.rectsource:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=shelfImage.rectsource)
            return current_uri

        else:
            return None
    def get_result_source_url(self, shelfImage):
        request = self.context.get('request')
        if shelfImage.resultsource:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=shelfImage.resultsource)
            return current_uri

        else:
            return None


class ShelfGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfGoods
        fields = ('pk', 'upc', 'xmin', 'ymin', 'xmax', 'ymax', 'level', 'row', 'col', 'result', 'is_label', 'process_code', 'baidu_code', 'create_time', 'update_time')
        read_only_fields = ('level', 'create_time', 'update_time')


class ShelfImage2Serializer(serializers.ModelSerializer):
    source_url = serializers.SerializerMethodField()
    result_source_url = serializers.SerializerMethodField()
    class Meta:
        model = ShelfImage2
        fields = ('pk', 'shopid', 'shelfid', 'picurl', 'tlevel', 'source_url', 'result_source_url',
                  'create_time', 'update_time')
        read_only_fields = ('create_time',)
    def get_source_url(self, shelfImage):
        request = self.context.get('request')
        if shelfImage.source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=shelfImage.source)
            return current_uri

        else:
            return None
    def get_result_source_url(self, shelfImage):
        request = self.context.get('request')
        if shelfImage.resultsource:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=shelfImage.resultsource)
            return current_uri

        else:
            return None


class ShelfGoods2Serializer(serializers.ModelSerializer):
    class Meta:
        model = ShelfGoods2
        fields = ('pk', 'upc', 'xmin', 'ymin', 'xmax', 'ymax', 'level', 'process_code', 'baidu_code', 'create_time', 'update_time')
        read_only_fields = ('level','create_time',)


class FreezerImageSerializer(serializers.ModelSerializer):
    visual_url = serializers.SerializerMethodField()
    class Meta:
        model = FreezerImage
        fields = ('pk', 'deviceid', 'ret', 'source','visual_url',
                  'create_time')
        read_only_fields = ('ret', 'visual','create_time')

    def get_visual_url(self, freezerImage):
        request = self.context.get('request')
        if freezerImage.visual:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                           host=request.get_host(),
                                                           path=settings.MEDIA_URL,
                                                           visual=freezerImage.visual)
            return current_uri

        else:
            return None

class GoodsImageSerializer(serializers.ModelSerializer):

    rgb_source_url = serializers.SerializerMethodField()
    depth_source_url = serializers.SerializerMethodField()
    class Meta:
        model = GoodsImage
        fields = ('pk', 'rgb_source', 'rgb_source_url', 'depth_source', 'depth_source_url', 'table_z')
        read_only_fields = ('result','create_time',)

    def get_rgb_source_url(self, goodsImage):
        request = self.context.get('request')
        if goodsImage.source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=goodsImage.rgb_source)
            return current_uri

        else:
            return None
    def get_depth_source_url(self, goodsImage):
        request = self.context.get('request')
        if goodsImage.resultsource:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=goodsImage.depth_source)
            return current_uri

        else:
            return None
