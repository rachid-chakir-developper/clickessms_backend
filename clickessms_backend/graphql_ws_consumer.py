import channels_graphql_ws
from channels_graphql_ws.scope_as_context import ScopeAsContext

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