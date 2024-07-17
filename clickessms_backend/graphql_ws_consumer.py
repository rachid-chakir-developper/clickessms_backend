import channels_graphql_ws
from channels_graphql_ws.scope_as_context import ScopeAsContext
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from graphql_jwt.utils import jwt_decode
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        return user

    except User.DoesNotExist:
        return AnonymousUser()

class SGIGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    # Uncomment to send keepalive message every 42 seconds.
    # send_keepalive_every = 42

    # Uncomment to process requests sequentially (useful for tests).
    # strict_ordering = True

    async def on_connect(self, payload):
        """New client connection handler."""
        # You can `raise` from here to reject the connection.
        print("New client connected!")
        context = ScopeAsContext(self.scope)
        if 'JWT' in payload:
            # Decode the token
            decoded_data = jwt_decode(payload['JWT'])

            # Inject the user
            context.user = await get_user(username=decoded_data['username'])

        else:
            context.user = AnonymousUser
        context.build_absolute_uri = self.build_absolute_uri
        try:
            headers = self.scope.get('headers', [])
            for key, value in headers:
                if key == b'host':
                    context.host = value.decode().split(':')
                    if context.host:
                        print(f"Domaine actuel : {context.host}")
        except:
            pass
        await super().on_connect(payload)
        

    def build_absolute_uri(self, path):
        server = self.scope["server"]
        the_host = self.scope["host"]
        if the_host:
            if the_host[0]:
                host = the_host[0]
            else:
                 host = server[0]
            if the_host[1]:
                scheme = "https" if the_host[1] == "443" else "http"
                port = "" if the_host[1] in ["443", '80', '8080'] else f":{the_host[1]}"
            else:
                scheme = "https" if server[1] == "443" else "http"
                port = "" if server[1] in ["443", '80', '8080'] else f":{server[1]}"
        else:
            # Construct an absolute URL based on the scope
            scheme = "https" if server[1] == "443" else "http"
            port = "" if server[1] in ["443", '80', '8080'] else f":{server[1]}"
            host = server[0] 
        return f"{scheme}://{host}{port}{path}"