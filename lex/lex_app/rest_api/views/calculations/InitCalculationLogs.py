import time

from django.db.models import Max
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from lex.lex_app.logging.CalculationLog import CalculationLog
from lex_app.LexLogger.LexLogger import LexLogLevel, LexLogger
from django.core.cache import caches

class InitCalculationLogs(APIView):
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:

            calculation_id = request.query_params['calculation_id']
            calculation_record = request.query_params['calculation_record']
            redis_cache = caches['redis']
            cache_key = f"{calculation_record}_{calculation_id}"
            cache_value = redis_cache.get(cache_key)

            return JsonResponse({"logs": cache_value})
        except Exception as e:
            print(e)
            return JsonResponse({"logs": ""})
