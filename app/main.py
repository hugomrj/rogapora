# app/main.py
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.router import routes
from app.config import BASE_DIR

# 1. Definimos el Middleware como una clase
class ProxyHTTPSFix(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Si Nginx envía la cabecera x-forwarded-proto https
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        
        response = await call_next(request)
        return response

# 2. Creamos la aplicación
app = Starlette(debug=True, routes=routes)

# 3. Añadimos el middleware usando el método add_middleware
app.add_middleware(ProxyHTTPSFix)

# 4. Montamos los estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web/static")), name="static")