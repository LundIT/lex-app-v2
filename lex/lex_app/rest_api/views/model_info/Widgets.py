from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from django.http import JsonResponse
from django.db import models

class Widgets(APIView):
    http_method_names = ['get']
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, *args, **kwargs):
        from lex.lex_app.ProcessAdminSettings import processAdminSite, adminSite

        return JsonResponse({"widget_structure": processAdminSite.widget_structure})
