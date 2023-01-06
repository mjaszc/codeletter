from . import consumers
from django.urls import path


websocket_urlpatterns = [
    path(
        "notifications/",
        consumers.NotificationConsumer.as_asgi(),
    )
]
