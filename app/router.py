# app/router.py
from starlette.routing import Mount
from app.routes import web

routes = [
    Mount("/", app=web.router),
]