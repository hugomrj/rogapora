# app/main.py
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.router import routes
from app.config import BASE_DIR

# Definimos el middleware
# Opción 1: Middleware personalizado simple (Recomendado para tu caso)
async def https_middleware(request, call_next):
    # Si Nginx nos dice que el protocolo original fue HTTPS
    if request.headers.get("x-forwarded-proto") == "https":
        # Modificamos el scope para que Starlette crea que es HTTPS
        request.scope["scheme"] = "https"
    
    response = await call_next(request)
    return response

# Creamos la aplicación con el middleware
app = Starlette(
    debug=True, # Recuerda poner False en producción real
    routes=routes,
    middleware=[
        Middleware(https_middleware)
    ]
)

# Montamos los estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web/static")), name="static")