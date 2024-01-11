"""
ASGI config for DjangoProcessAdminGeneric project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""
import os


from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import atexit
import asyncio
import ProcessAdminRestApi.routing
from ProcessAdminRestApi.consumers.BackendHealthConsumer import BackendHealthConsumer
from ProcessAdminRestApi.consumers.CalculationLogConsumer import CalculationLogConsumer
from ProcessAdminRestApi.consumers.CalculationNotificationConsumer import CalculationNotificationConsumer
from ProcessAdminRestApi.consumers.MonitoringConsumer import MonitoringConsumer
from ProcessAdminRestApi.consumers.NotificationsConsumer import NotificationsConsumer
from ProcessAdminRestApi.consumers.UpdateCalculationStatusConsumer import UpdateCalculationStatusConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProcessAdminGeneric.settings")
django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(ProcessAdminRestApi.routing.websocket_urlpatterns))
        ),
    }
)
def on_server_shutdown(*args, **kwargs):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(BackendHealthConsumer.disconnect_all())
    loop.run_until_complete(CalculationLogConsumer.disconnect_all())
    loop.run_until_complete(CalculationNotificationConsumer.disconnect_all())
    loop.run_until_complete(MonitoringConsumer.disconnect_all())
    loop.run_until_complete(UpdateCalculationStatusConsumer.disconnect_all())
    loop.run_until_complete(NotificationsConsumer.disconnect_all())

atexit.register(on_server_shutdown)
