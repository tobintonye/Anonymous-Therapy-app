"""
ASGI config for easetalkprojectapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from easetalk import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easetalkprojectapp.settings')

# initialize the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Handles traditional HTTP requests
    "websocket": AuthMiddlewareStack(
         URLRouter(
            routing.websocket_urlpatterns # WebSocket requests go through here
        )
    ),
})

