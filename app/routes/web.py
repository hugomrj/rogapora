# app/routes/web.py
from starlette.routing import Router
from app.config import templates, custom_route
from app.models.solicitud import Solicitud
from app.services.lead_service import LeadService # Importamos el decorador
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import SessionLocal 

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
    """ Vista GET: Renderiza el formulario """
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





@custom_route(router, "/public/precalificacion/guardar", methods=["POST"])
async def guardar_precalificacion_view(request):
    try:
        # 1. Obtenemos los datos del cuerpo de la petición
        data = await request.json()

        # 2. Llamamos al Service para que haga el trabajo pesado
        # Esto sigue el mismo patrón que tu ejemplo: await Service.metodo()
        await PrecalificacionService.guardar_solicitud(data)

        # 3. Retornamos la respuesta exitosa
        return JSONResponse(
            {"status": "ok", "message": "Solicitud guardada correctamente"}, 
            status_code=201
        )

    except Exception as e:
        print(f"Error en la ruta de precalificación: {e}")
        return JSONResponse(
            {"status": "error", "detail": "Ocurrió un error al procesar la solicitud"}, 
            status_code=400
        )