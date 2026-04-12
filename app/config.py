# app/config.py
from starlette.templating import Jinja2Templates
from pathlib import Path
from starlette.routing import Route

# Detectamos la ruta base del proyecto automáticamente
BASE_DIR = Path(__file__).parent.parent

# Instancia única de Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "web"))


# Este es el decorador global
def custom_route(router, path, methods=["GET"]):
    def decorator(func):
        router.routes.append(Route(path, endpoint=func, methods=methods))
        return func
    return decorator