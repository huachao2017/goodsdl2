import json
import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goods.shelfdisplay.generate_shelf_dispaly import generate_displays
logger = logging.getLogger("django")

class AutoDisplay(APIView):
    def get(self,request):
        try:
            shopid = int(request.query_params['shopid'])
            tzid = int(request.query_params['tzid'])
        except Exception as e:
            logger.error('Shelf auto display error:{}'.format(e))
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

        taizhang = generate_displays(shopid, tzid)
        ret = json.dumps(taizhang.to_json())

        return Response(ret, status=status.HTTP_200_OK)

