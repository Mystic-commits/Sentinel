"""Reject remote browser origins and DNS rebinding at the local agent boundary."""
from urllib.parse import urlsplit
from starlette.responses import JSONResponse
from .config import settings


class LocalAccessMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] in {'http', 'websocket'}:
            headers = dict(scope.get('headers', []))
            origin = headers.get(b'origin', b'').decode()
            host = urlsplit('//'+headers.get(b'host', b'').decode()).hostname
            allowed = host in {'localhost', '127.0.0.1', '::1'}
            allowed = allowed and (not origin or origin in settings.allowed_origins)
            if not allowed:
                if scope['type'] == 'websocket':
                    await send({'type': 'websocket.close', 'code': 1008})
                else:
                    await JSONResponse({'detail': 'Local access only'}, status_code=403)(scope, receive, send)
                return
        await self.app(scope, receive, send)
