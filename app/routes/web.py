from sqlalchemy import select
from starlette.routing import Router
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse  



# Imports de configuración
from app.config import templates, custom_route

# Imports de servicios
from app.database import get_db
from app.models.solicitud import Solicitud
from app.services.precalificacion_service import PrecalificacionService
from app.services.lead_service import LeadService 
from app.services.solicitud_service import SolicitudService 


router = Router()

# === VISTAS PRINCIPALES (Layouts completos) ===

@custom_route(router, "/")
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@custom_route(router, "/panel")
async def dashboard_panel(request: Request):
    return templates.TemplateResponse(request=request, name="panel.html")


# === GESTIÓN DE LEADS (Parciales HTMX) ===

@custom_route(router, "/lead-importar")
async def lead_importar_view(request: Request):
    return templates.TemplateResponse(request=request, name="partials/leads/importar.html")

@custom_route(router, "/lead-migrar-ejecutar", methods=["POST"])
async def lead_migrar_ejecutar(request: Request):
    form = await request.form()
    # El service procesa el Excel y devuelve el HTML parcial de respuesta
    return await LeadService.ejecutar_migracion_y_responder(form.get("excel_file"))

@custom_route(router, "/lead-limpiar")
async def lead_limpiar_view(request: Request): # Nombre corregido (antes duplicado)
    return templates.TemplateResponse(request=request, name="partials/leads/limpiar.html")

@custom_route(router, "/lead-limpiar", methods=["POST"])
async def lead_limpiar_ejecutar(request: Request):
    return await LeadService.limpiar_tabla_y_responder()


# === SOLICITUDES Y ANÁLISIS (Parciales HTMX) ===

@custom_route(router, "/analitica-resumen")
async def analitica_resumen_view(request: Request):
    stats = await LeadService.obtener_estadisticas_resumen()
    return templates.TemplateResponse(
        request=request, 
        name="partials/analytics/resumen.html", 
        context={"stats": stats}
    )

@custom_route(router, "/solicitudes-listar")
async def solicitudes_listar_view(request: Request):
    # Llamamos al service asincrónico
    solicitudes = await SolicitudService.obtener_todas()
    
    return templates.TemplateResponse(
        request=request, 
        name="partials/solicitudes/lista.html", 
        context={"solicitudes": solicitudes}
    )


@custom_route(router, "/solicitudes/ver/{id:int}")
async def solicitud_formulario_view(request: Request):
    sol_id = request.path_params.get("id")
    async with get_db() as session:
        result = await session.execute(select(Solicitud).where(Solicitud.id == sol_id))
        solicitud = result.scalar_one_or_none()
    
    if not solicitud:
        return HTMLResponse(
            content="<div class='p-4 bg-red-50 text-red-800 rounded-lg'>Solicitud no encontrada</div>", 
            status_code=404
        )

    return templates.TemplateResponse(
        request=request, 
        name="partials/solicitudes/form.html", 
        context={"sol": solicitud}
    )


# === PÁGINAS PÚBLICAS (Formularios externos) ===

@custom_route(router, "/public/precalificacion")
async def precalificacion_view(request: Request):
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
async def guardar_precalificacion_view(request: Request):
    try:
        data = await request.json()
        # El service ahora debe ser asincrónico también
        await PrecalificacionService.guardar_solicitud(data)

        return JSONResponse(
            {"status": "ok", "message": "Solicitud guardada correctamente"}, 
            status_code=201
        )
    except Exception as e:
        # Útil para debug en consola, pero limpio para el usuario
        print(f"Error en la ruta de precalificación: {e}")
        return JSONResponse(
            {"status": "error", "detail": str(e)}, 
            status_code=400
        )