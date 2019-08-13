import logging
import subprocess
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("django")

class Test(APIView):
    def get(self, request):
        print(request.query_params)
        import sys
        path = sys.path
        return Response({'Test': path})


