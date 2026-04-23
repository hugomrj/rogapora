# app/config.py
# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates
from starlette.routing import Route

# 1. Cargamos el .env
load_dotenv()

# 2. Rutas base y Templates
# Mantenemos esto aquí porque lo usan casi todos los controladores web
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web"))

# 3. Decorador global para rutas
# Es una utilidad de configuración de la app, así que se queda aquí
def custom_route(router, path, methods=["GET"]):
    def decorator(func):
        router.routes.append(Route(path, endpoint=func, methods=methods))
        return func
    return decorator

# 4. Variables de entorno (opcional)
# Puedes centralizar las variables aquí para que otros módulos las importen fácilmente
DEBUG = os.getenv("DEBUG", "False") == "True"