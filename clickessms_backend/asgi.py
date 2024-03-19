"""
ASGI config for clickessms_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import channels
import django
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter#added
from clickessms_backend.schema import AppGraphqlWsConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clickessms_backend.settings')

#application = get_asgi_application()

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)
    "websocket": AuthMiddlewareStack(channels.routing.URLRouter([
        django.urls.path("graphql", AppGraphqlWsConsumer.as_asgi()),
    ])
    ),
})