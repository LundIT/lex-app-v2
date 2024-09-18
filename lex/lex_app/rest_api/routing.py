from django.urls import path

from lex.lex_app.rest_api.consumers.BackendHealthConsumer import BackendHealthConsumer
from lex.lex_app.rest_api.consumers.CalculationLogConsumer import CalculationLogConsumer
from lex.lex_app.rest_api.consumers.UpdateCalculationStatusConsumer import UpdateCalculationStatusConsumer
from lex.lex_app.rest_api.consumers.CalculationsConsumer import CalculationsConsumer
from lex_app.rest_api.consumers.LogConsumer import LogConsumer

websocket_urlpatterns = [
    path('ws/logs', LogConsumer.as_asgi() , name='logs'),

    path('ws/health', BackendHealthConsumer.as_asgi(),
                 name='backend-health'),
    path('ws/calculations', CalculationsConsumer.as_asgi(),
                 name='calculations'),
    path('ws/calculation_logs/<str:calculationId>', CalculationLogConsumer.as_asgi(),
         name='calculation-logs'),
    path('ws/calculation_status_update', UpdateCalculationStatusConsumer.as_asgi(),
         name='calculation-status-update'),

]
