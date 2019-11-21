import json
import logging
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from goods.shelfdisplay.generate_shelf_dispaly import generate_displays
import urllib.request
from django.db import connections
from .serializers import *


logger = logging.getLogger("django")

class ShelfDisplayDebugViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    queryset = ShelfDisplayDebug.objects.order_by('-id')
    serializer_class = ShelfDisplayDebugSerializer

class AutoDisplay(APIView):
    def get(self,request):
        tz_id = None
        try:
            uc_shopid = int(request.query_params['ucshopid'])
            # if 'tzid' in request.query_params['tzid']:
            tz_id = int(request.query_params['tzid'])
        except Exception as e:
            logger.error('Shelf auto display error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        taizhangid_list = []
        if tz_id is not None:
            taizhangid_list.append(tz_id)
        # else:
        #     cursor = connections['ucenter'].cursor()
        #
        #     # 获取所有台账
        #     try:
        #         cursor.execute(
        #             "select t.id, t.shelf_id, t.shelf_count, t.third_cate_ids from sf_shop_taizhang st, sf_taizhang t where st.taizhang_id=t.id and st.shop_id = {}".format(
        #                 uc_shopid))
        #         taizhang_infos = cursor.fetchall()
        #         for taizhang_info in taizhang_infos:
        #             taizhangid_list.append(taizhang_info[0])
        #     except:
        #         print('获取台账失败：{}！'.format(uc_shopid))
        #         raise ValueError('taizhang error:{}'.format(uc_shopid))
        #     finally:
        #         cursor.close()

        url = "https://autodisplay:xianlife2018@taizhang.aicvs.cn/api/autoDisplay"
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json"
        }
        for taizhangid in taizhangid_list:
            taizhang = generate_displays(uc_shopid, taizhangid)
            json_info = json.dumps(taizhang.to_json())
            data = bytes(json_info, 'utf8')
            request = urllib.request.Request(url=url, data=data, headers=headers)

            response = urllib.request.urlopen(request)
            print(response.read().decode())

        return Response('OK', status=status.HTTP_200_OK)

