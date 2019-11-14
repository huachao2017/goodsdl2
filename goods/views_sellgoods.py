import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goods.sellgoods.salesquantity.service import generate_order_shop

logger = logging.getLogger("django")
class Test(APIView):
    def get(self, request):
        print(request.query_params)
        import sys
        path = sys.path
        return Response({'Test': path})

class SellGoodsViewSet(APIView):
    def get(self,request):
        shop_id = request.query_params['shop_id']
        generate_order_shop.generate(shopid = shop_id)
        print ("shop_id=%s, notify_shop_order_generate success..."% str(shop_id))
        return Response(status=status.HTTP_200_OK)

