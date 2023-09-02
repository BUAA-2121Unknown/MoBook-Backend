import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoBook.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# import module earlier from ASGI application initialization may result
# in App not ready exception
import artifact.routing
import chat.routing
import notif.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                    URLRouter(
                            chat.routing.websocket_urlpatterns +
                            notif.routing.websocket_urlpatterns +
                            artifact.routing.websocket_urlpatterns
                    )
            )
    ),
})
