# app/routes/web.py
from starlette.routing import Route
from starlette.responses import JSONResponse
from app.config import templates
from app.services import PrecalificacionService
from app.services.lead_service import LeadService


# --- Definición de Vistas ---

async def login(request):
    return templates.TemplateResponse(request=request, name="login.html")

async def demo(request):
    return templates.TemplateResponse(request=request, name="panel.html")

async def lead_importar_view(request):
    """Muestra el partial del formulario de migración"""
    return templates.TemplateResponse(request=request, name="partials/leads/importar.html")

async def lead_migrar_ejecutar(request):
    form = await request.form()
    # El service se encarga de TODO y devuelve la respuesta lista para el navegador
    return await LeadService.ejecutar_migracion_y_responder(form.get("excel_file"))

# Se renombró esta función para que no choque con la anterior
async def lead_limpiar_view(request):
    return templates.TemplateResponse(request=request, name="partials/leads/limpiar.html")

async def lead_limpiar_ejecutar(request):
    return await LeadService.limpiar_tabla_y_responder()



async def analitica_resumen_view(request):
    # 1. Llamamos al service para obtener los cálculos
    stats = await LeadService.obtener_estadisticas_resumen()
    
    # 2. Pasamos 'stats' al context para que Jinja2 lo use
    return templates.TemplateResponse(
        request=request, 
        name="partials/analytics/resumen.html", 
        context={"stats": stats}
    )



# --- Rutas Públicas ---

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

async def guardar_precalificacion_view(request):
    try:
        # 1. Obtenemos los datos del cuerpo de la petición
        data = await request.json()

        # 2. Llamamos al Service
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

# --- Lista de Rutas (Estándar de Starlette) ---

routes = [
    Route("/", endpoint=login, name="login"),
    Route("/panel", endpoint=demo, name="panel"),
    
    # Leads
    Route("/lead-importar", endpoint=lead_importar_view, name="lead_importar"),
    Route("/lead-migrar-ejecutar", endpoint=lead_migrar_ejecutar, methods=["POST"]),
    Route("/lead-limpiar", endpoint=lead_limpiar_view, name="lead_limpiar"), # GET
    Route("/lead-limpiar", endpoint=lead_limpiar_ejecutar, methods=["POST"]), # POST
    
    # Analítica
    Route("/analitica-resumen", endpoint=analitica_resumen_view, name="analitica_resumen"),
    
    # Público
    Route("/public/precalificacion", endpoint=precalificacion_view, name="precalificacion"),
    Route("/public/precalificacion/guardar", endpoint=guardar_precalificacion_view, methods=["POST"]),
]