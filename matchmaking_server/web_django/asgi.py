"""
ASGI config for web_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_django.settings")

django_asgi_app = get_asgi_application()

import matchmaking.routing  # <-- importer après get_asgi_application

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        matchmaking.routing.websocket_urlpatterns
    ),
})
