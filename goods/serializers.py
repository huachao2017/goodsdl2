from rest_framework import serializers
from goods.models import ShelfImage, ShelfGoods, ShelfImage2, ShelfGoods2,FreezerImage,GoodsImage,ShelfDisplayDebug,ShelfDisplayDebugGoods,AllWorkFlowBatch
import os
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
    output_url = serializers.SerializerMethodField()
    class Meta:
        model = GoodsImage
        fields = ('pk', 'rgb_source', 'rgb_source_url', 'depth_source', 'depth_source_url', 'output_url', 'table_z', 'result', 'create_time')
        read_only_fields = ('result','create_time',)

    def get_rgb_source_url(self, goodsImage):
        request = self.context.get('request')
        if goodsImage.rgb_source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=goodsImage.rgb_source)
            return current_uri

        else:
            return None
    def get_depth_source_url(self, goodsImage):
        request = self.context.get('request')
        if goodsImage.depth_source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=goodsImage.depth_source)
            return current_uri

        else:
            return None

    def get_output_url(self, goodsImage):
        request = self.context.get('request')
        if goodsImage.rgb_source:
            image_dir, image_name = os.path.split(str(goodsImage.rgb_source))
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                                   host=request.get_host(),
                                                                   path=settings.MEDIA_URL,
                                                                   visual=os.path.join(image_dir,'_output_{}'.format(image_name)))
            return current_uri

        else:
            return None

class AllWorkFlowBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllWorkFlowBatch
        fields = ('pk', 'batch_id', 'uc_shopid', 'type',
                  'select_goods_status',
                  'select_goods_calculate_time',
                  'auto_display_status',
                  'auto_display_calculate_time',
                  'order_goods_status',
                  'order_goods_calculate_time',
                  'create_time','update_time')
        read_only_fields = ('create_time','update_time')

class ShelfDisplayDebugGoodsSerializer(serializers.ModelSerializer):
    goods_tree_source_url = serializers.SerializerMethodField()
    class Meta:
        model = ShelfDisplayDebugGoods
        fields = ('pk', 'category', 'goods_tree_source','goods_tree_source_url',
                  'create_time')

    def get_goods_tree_source_url(self, shelf_display_debug_goods):
        request = self.context.get('request')
        if shelf_display_debug_goods.goods_tree_source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                           host=request.get_host(),
                                                           path=settings.MEDIA_URL,
                                                           visual=shelf_display_debug_goods.goods_tree_source)
            return current_uri

        else:
            return None

class ShelfDisplayDebugSerializer(serializers.ModelSerializer):
    image_problem_goods = ShelfDisplayDebugGoodsSerializer(many=True, read_only=True)
    display_source_url = serializers.SerializerMethodField()
    category_intimacy_source_url = serializers.SerializerMethodField()
    class Meta:
        model = ShelfDisplayDebug
        fields = ('pk', 'batch_id', 'uc_shopid', 'tz_id', 'json_ret', 'display_source','display_source_url', 'category_intimacy_source','category_intimacy_source_url',
                  'image_problem_goods', 'create_time')

    def get_display_source_url(self, shelf_display_debug):
        request = self.context.get('request')
        if shelf_display_debug.display_source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                           host=request.get_host(),
                                                           path=settings.MEDIA_URL,
                                                           visual=shelf_display_debug.display_source)
            return current_uri

        else:
            return None
    def get_category_intimacy_source_url(self, shelf_display_debug):
        request = self.context.get('request')
        if shelf_display_debug.category_intimacy_source:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                           host=request.get_host(),
                                                           path=settings.MEDIA_URL,
                                                           visual=shelf_display_debug.category_intimacy_source)
            return current_uri

        else:
            return None
