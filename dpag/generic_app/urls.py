from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('api/data/<str:file_name>', csrf_exempt(views.DataAPI.as_view()), name='dataapi'),
    path('api/data_list/', views.DataListAPI.as_view(), name='datalistapi'),
    path('api/auth_method/', views.AuthMethodAPI.as_view(), name='auth_methodapi'),
    path('api/vscode', views.VsCodePassword.as_view(), name='vscode_password'),
    path('health', views.HealthCheck.as_view(), name='health_view')
]