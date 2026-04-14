# app/routes/web.py
from starlette.routing import Router
from app.config import templates, custom_route
from app.services.lead_service import LeadService # Importamos el decorador
from starlette.requests import Request

router = Router()

# Usamos el decorador pasando el 'router' local como primer argumento
@custom_route(router, "/")
async def login(request):
    return templates.TemplateResponse(request=request, name="login.html")

@custom_route(router, "/panel")
async def demo(request):
    return templates.TemplateResponse(request=request, name="panel.html")



@custom_route(router, "/lead-importar")
async def lead_importar_view(request):
    """Muestra el partial del formulario de migración"""
    return templates.TemplateResponse(request=request, name="partials/leads/importar.html")

@custom_route(router, "/lead-migrar-ejecutar", methods=["POST"])
async def lead_migrar_ejecutar(request):
    form = await request.form()
    # El service se encarga de TODO y devuelve la respuesta lista para el navegador
    return await LeadService.ejecutar_migracion_y_responder(form.get("excel_file"))





@custom_route(router, "/lead-limpiar")
async def lead_importar_view(request):
    return templates.TemplateResponse(request=request, name="partials/leads/limpiar.html")

@custom_route(router, "/lead-limpiar", methods=["POST"])
async def lead_limpiar_ejecutar(request: Request):
    return await LeadService.limpiar_tabla_y_responder()


@custom_route(router, "/analitica-resumen")
async def analitica_resumen_view(request):
    # 1. Llamamos al service para obtener los cálculos
    stats = await LeadService.obtener_estadisticas_resumen()
    
    # 2. Pasamos 'stats' al context para que Jinja2 lo use
    return templates.TemplateResponse(
        request=request, 
        name="partials/analytics/resumen.html", 
        context={"stats": stats}
    )


#  paginas publicas
# routes.py o donde tengas tus rutas

@custom_route(router, "/public/precalificacion")
async def precalificacion_view(request):
    # Capturar parámetros de origen desde la URL
    # Ejemplo: /public/precalificacion?origen=instagram&campana=verano2024
    origen = request.query_params.get('origen', 'desconocido')
    campana = request.query_params.get('campana', 'organico')
    
    return templates.TemplateResponse(
        request=request, 
        name="public/precalificacion.html",
        context={
            "origen_contacto": origen,
            "campana": campana,
            "title": "Precalificación de Crédito - Che Roga Porá"
        }
    )