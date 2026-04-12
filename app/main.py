# app/main.py
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from app.router import routes
from app.config import BASE_DIR

app = Starlette(debug=True, routes=routes)

# Montamos los estáticos usando la ruta base de config.py
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "web/static")), name="static")