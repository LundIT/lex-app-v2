from django.urls import path

from . import views

urlpatterns = [
    path('health', views.HealthCheck.as_view(), name='health_view')
]