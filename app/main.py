# app/main.py
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from app.router import routes
from app.config import BASE_DIR

app = Starlette(debug=True, routes=routes)

# Imprime las rutas cargadas al iniciar el servidor
print("--- Rutas Registradas ---")
for route in app.router.routes:
    # Si es un Mount, exploramos sus rutas internas
    if hasattr(route, "app") and hasattr(route.app, "routes"):
        print(f"Mount: {route.path}")
        for sub_route in route.app.routes:
            print(f"  -> {sub_route.path}")
    else:
        print(f"Directa: {route.path}")


# Montamos los estáticos usando la ruta base de config.py
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web/static")), name="static")