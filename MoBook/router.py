# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import artifact.routing
import chat.routing
import notif.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
            URLRouter(
                    chat.routing.websocket_urlpatterns +
                    notif.routing.websocket_urlpatterns +
                    artifact.routing.websocket_urlpatterns
            )
    ),
})
