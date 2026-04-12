# app/routes/web.py
from starlette.routing import Router
from app.config import templates, custom_route # Importamos el decorador

router = Router()

# Usamos el decorador pasando el 'router' local como primer argumento
@custom_route(router, "/")
async def login(request):
    return templates.TemplateResponse(request=request, name="login.html")

@custom_route(router, "/demo")
async def demo(request):
    return templates.TemplateResponse(request=request, name="demo.html")

@custom_route(router, "/guardar", methods=["POST"])
async def guardar(request):
    # Lógica de POST
    pass