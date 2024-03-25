import glob
import os
import ast
import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey


class DataAPI(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request, file_name):
        file_name = re.sub(r'(?<!\\)_', '/', file_name)
        file_name = file_name.replace("\\", "")

        folder_root = "./generic_app/submodels/"
        file_content = open(folder_root + file_name, "r").read()

        return JsonResponse({'file_content': file_content})

    def post(self, request, file_name):
        file_n = file_name
        file_name = re.sub(r'(?<!\\)_', '/', file_name)
        file_name = file_name.replace("\\", "")

        folder_root = "./generic_app/submodels/"

        file_handler = open(folder_root + file_name, "w")
        file_handler.write(ast.literal_eval(request.body.decode('utf-8'))['content'])
        file_handler.close()

        return HttpResponse("OK!")


class DataListAPI(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get(self, request):
        folder_content_outer = glob.glob("./generic_app/submodels/*/")
        folder_content_outer = [elem for elem in folder_content_outer if not elem.startswith("./generic_app/submodels/_") and not elem.startswith("./generic_app/submodels/.")]

        folder_content = [elem.lstrip("generic_app/submodels/") for elem in glob.glob('generic_app/submodels/**/*.py', recursive=True)]

        # folder_content = glob.glob(folder_content_outer[0] + "*.py")
        # folder_content = [elem.split("/")[-1] for elem in folder_content]
        return JsonResponse({'folder_content': folder_content})


class AuthMethodAPI(View):
    authentication_classes = []

    def get(self, request):
        return JsonResponse({'auth_method': settings.USED_AUTH_BACKEND})


class VsCodePassword(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    @classmethod
    def get_vscode_password(cls):
        try:
            file_handler = open("/app/code-server-config/config.yaml", "r")
            file_content = file_handler.read()
            file_content = file_content.split("\n")
            vscode_password = list(filter(lambda x: x.startswith("password"), file_content))[0].split(": ")[1]
            return vscode_password
        except FileNotFoundError as e:
            return ''

    def get(self, request):

        vscode_password = VsCodePassword.get_vscode_password()
        if vscode_password:
            return JsonResponse({'found': True, 'vscode_password': vscode_password})
        else:
            return JsonResponse({'found': False, 'vscode_password': ''})


class HealthCheck(View):
    authentication_classes = []

    def get(self, request):
        return JsonResponse({"status": "Healthy :)"})
