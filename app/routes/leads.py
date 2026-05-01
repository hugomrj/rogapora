from starlette.routing import Route
from starlette.responses import RedirectResponse
from app.config import templates, SessionLocal
from datetime import datetime

# Importamos joinedload para solucionar el error de DetachedInstanceError
from sqlalchemy.orm import joinedload

from app.models.catalogos import EstadoCliente, InteresCliente, ProximaAccion, RangoPrecio
from app.models.lead import Lead
from app.models.origenes_contacto import OrigenContacto

# --- Funciones Auxiliares ---

def parse_date(date_str):
    """Maneja fechas vacías."""
    return date_str if date_str and date_str.strip() != "" else None

def clean_int(value):
    """Convierte cadenas vacías de los selects a None para la FK."""
    if value == "" or value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None

# --- Vistas ---

def list_leads(request):
    with SessionLocal() as db:
        # Usamos joinedload para traer las relaciones en la misma query
        leads = db.query(Lead).options(
            joinedload(Lead.origen),
            joinedload(Lead.interes),
            joinedload(Lead.rango),
            joinedload(Lead.estado),
            joinedload(Lead.accion)
        ).order_by(Lead.fecha_migracion.desc()).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="partials/leads/list.html", 
        context={"leads": leads}
    )

def create_lead_form(request):
    with SessionLocal() as db:
        context = {
            "lead": None,
            "origenes": db.query(OrigenContacto).all(),
            "intereses": db.query(InteresCliente).all(),
            "rangos": db.query(RangoPrecio).all(),
            "estados": db.query(EstadoCliente).all(),
            "acciones": db.query(ProximaAccion).all(),
        }
    
    return templates.TemplateResponse(
        request=request, 
        name="partials/leads/form.html", 
        context=context
    )

def edit_lead_form(request):
    lead_id = request.path_params["lead_id"]
    
    with SessionLocal() as db:
        lead = db.query(Lead).options(
            joinedload(Lead.origen),
            joinedload(Lead.interes)
        ).filter(Lead.id == lead_id).first()
        
        context = {
            "lead": lead,
            "origenes": db.query(OrigenContacto).all(),
            "intereses": db.query(InteresCliente).all(),
            "rangos": db.query(RangoPrecio).all(),
            "estados": db.query(EstadoCliente).all(),
            "acciones": db.query(ProximaAccion).all(),
        }
        
    return templates.TemplateResponse(
        request=request, 
        name="partials/leads/form.html", 
        context=context
    )

async def save_lead(request):
    form = await request.form()
    lead_id = form.get("id")
    
    with SessionLocal() as db:
        if lead_id:
            # --- ACTUALIZACIÓN ---
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if lead:
                lead.nombre_apellido = form.get("nombre_apellido")
                lead.telefono = form.get("telefono")
                lead.ciudad = form.get("ciudad")
                lead.fecha_contacto = parse_date(form.get("fecha_contacto"))
                
                lead.origen_contacto_id = clean_int(form.get("origen_contacto_id"))
                lead.interes_cliente_id = clean_int(form.get("interes_cliente_id"))
                lead.rango_precios_id = clean_int(form.get("rango_precios_id"))
                lead.estado_cliente_id = clean_int(form.get("estado_cliente_id"))
                lead.proxima_accion_id = clean_int(form.get("proxima_accion_id"))
                
                lead.comentario = form.get("comentario")
                lead.observaciones = form.get("observaciones")
                lead.situacion_analisis = form.get("situacion_analisis")
        else:
            # --- CREACIÓN ---
            new_lead = Lead(
                nombre_apellido=form.get("nombre_apellido"),
                telefono=form.get("telefono"),
                ciudad=form.get("ciudad"),
                fecha_contacto=parse_date(form.get("fecha_contacto")),
                
                origen_contacto_id=clean_int(form.get("origen_contacto_id")),
                interes_cliente_id=clean_int(form.get("interes_cliente_id")),
                rango_precios_id=clean_int(form.get("rango_precios_id")),
                estado_cliente_id=clean_int(form.get("estado_cliente_id")),
                proxima_accion_id=clean_int(form.get("proxima_accion_id")),
                
                comentario=form.get("comentario"),
                observaciones=form.get("observaciones"),
                situacion_analisis=form.get("situacion_analisis")
            )
            db.add(new_lead)
        
        db.commit()
    
    return RedirectResponse(url=request.url_for("leads:list"), status_code=303)

# --- NUEVA FUNCIÓN DELETE ---
def delete_lead(request):
    lead_id = request.path_params["lead_id"]
    
    with SessionLocal() as db:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            db.delete(lead)
            db.commit()
            
    # Redirigimos de vuelta a la lista
    return RedirectResponse(url=request.url_for("leads:list"), status_code=303)

# --- Rutas ---
routes = [
    Route("/list", endpoint=list_leads, name="list"),
    Route("/create", endpoint=create_lead_form, name="create"),
    Route("/{lead_id}/edit", endpoint=edit_lead_form, name="edit"),
    Route("/save", endpoint=save_lead, methods=["POST"], name="save"),
    # RUTA AGREGADA:
    Route("/{lead_id}/delete", endpoint=delete_lead, methods=["DELETE"], name="delete"),
]