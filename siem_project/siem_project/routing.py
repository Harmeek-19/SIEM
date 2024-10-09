from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from api.consumers import AlertConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/alerts/', AlertConsumer.as_asgi()),
    ]),
})