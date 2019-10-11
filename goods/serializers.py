from rest_framework import serializers
from goods.models import ShelfImage, ShelfGoods, FreezerImage

from django.conf import settings


class ShelfImageSerializer(serializers.ModelSerializer):
    rect_source_url = serializers.SerializerMethodField()
    result_source_url = serializers.SerializerMethodField()
    class Meta:
        model = ShelfImage
        fields = ('pk', 'picid', 'shopid', 'shelfid', 'displayid', 'tlevel', 'picurl', 'source', 'rectjson', 'rect_source_url',
                  'score', 'equal_cnt', 'different_cnt', 'unknown_cnt', 'result_source_url', 'test_server', 'create_time', 'update_time')
        read_only_fields = ('create_time',)
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
        fields = ('pk', 'upc', 'xmin', 'ymin', 'xmax', 'ymax', 'level', 'row', 'col', 'result', 'is_label', 'process_code', 'create_time', 'update_time')
        read_only_fields = ('level', 'create_time', 'update_time')


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
