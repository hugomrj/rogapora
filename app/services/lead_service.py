
import pandas as pd
import io
import numpy as np
from starlette.responses import HTMLResponse
from app.models.lead import Lead
from app.config import SessionLocal
from sqlalchemy import delete, func

class LeadService:
    @staticmethod
    async def ejecutar_migracion_y_responder(archivo) -> HTMLResponse:
        try:
            contenido = await archivo.read()
            # Leemos el Excel tal cual viene
            df = pd.read_excel(io.BytesIO(contenido))
            
            # Limpieza global de nulos de Pandas (NaN) a None de Python
            df = df.astype(object).replace({np.nan: None})
            registros_creados = 0
            
            with SessionLocal() as db:
                for _, row in df.iterrows():
                    # Helper para obtener valor por índice y limpiar espacios
                    def get_val(idx):
                        try:
                            val = row.iloc[idx]
                            return str(val).strip() if val is not None and str(val).lower() != 'nan' else None
                        except:
                            return None

                    # --- TRATAMIENTO DE FECHA (Posición 2: Fecha de Contacto) ---
                    raw_fecha = row.iloc[2]
                    fecha_db = None
                    if raw_fecha:
                        try:
                            # Convertimos a YYYY-MM-DD para que el ordenamiento en DB sea correcto
                            fecha_db = pd.to_datetime(raw_fecha, dayfirst=True).strftime('%Y-%m-%d')
                        except:
                            fecha_db = get_val(2)

                    # --- MAPEO POR POSICIÓN (Basado en tu imagen amarilla) ---
                    nuevo_lead = Lead(
                        id_excel=get_val(0),              # Id Cliente
                        nombre_apellido=get_val(1),       # Nombre y Apellido
                        fecha_contacto=fecha_db,           # Fecha de Contacto (Procesada)
                        telefono=get_val(3),              # Telefono
                        ciudad=get_val(4),                # Ciudad
                        origen_contacto=get_val(5),       # Origen del Contacto
                        interes_cliente=get_val(6),       # Interes del Cliente
                        rango_precios=get_val(7),         # Rango de Precios
                        estado_cliente=get_val(8),        # Estado Cliente
                        proxima_accion=get_val(9),        # Proxima Accion
                        fecha_ultimo_contacto=get_val(10),# Fecha del ultimo contacto
                        comentario=get_val(11),           # Comentario
                        observaciones=get_val(12),        # Observaciones
                        situacion_analisis=get_val(13)    # Situacion según Analisis
                    )

                    # Solo procesamos si hay un nombre (evita filas vacías al final del Excel)
                    if nuevo_lead.nombre_apellido:
                        # Evitar duplicados si existe el ID de Excel
                        exists = False
                        if nuevo_lead.id_excel:
                            exists = db.query(Lead).filter(Lead.id_excel == nuevo_lead.id_excel).first()
                        
                        if not exists:
                            db.add(nuevo_lead)
                            registros_creados += 1

                
                db.commit()

            return HTMLResponse(content=f"""
                <div class="animate-fade-in p-4 rounded-xl border border-green-200 bg-green-50 flex items-center gap-4">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: rgba(34, 197, 94, 0.1);">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-bold text-green-800">Migración Finalizada</p>
                        <p class="text-xs text-green-700">Se procesaron <span class="font-bold">{registros_creados}</span> registros desde <span class="italic text-green-900">{archivo.filename}</span>.</p>
                    </div>
                </div>
            """)

        except Exception as e:
            return HTMLResponse(content=f"""
                <div class="animate-fade-in p-4 rounded-xl border border-red-200 bg-red-50 flex items-center gap-3">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: rgba(239, 68, 68, 0.1);">
                        <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-bold text-red-800">Error en la carga</p>
                        <p class="text-xs text-red-700 font-mono line-clamp-2">{str(e)}</p>
                    </div>
                </div>
            """, status_code=500)
        


    @staticmethod
    async def limpiar_tabla_y_responder() -> HTMLResponse:
        try:
            # Usamos el bloque 'with' igual que en tu migración exitosa
            with SessionLocal() as db:
                # delete(Lead) usa el modelo que me pasaste arriba
                result = db.execute(delete(Lead))
                db.commit()
                count = result.rowcount
            
            return HTMLResponse(content=f"""
                <div class="animate-fade-in p-4 rounded-xl border border-green-200 bg-green-50 flex items-center gap-4">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: rgba(34, 197, 94, 0.1);">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-bold text-green-800">
                        Tabla vaciada
                        </p>
                        <p class="text-xs text-green-700">Se eliminaron correctamente 
                            <span class="font-bold">
                                {count}</span> registros
                            </span>.
                        </p>
                    </div>
                </div>
            """)

        except Exception as e:
            return HTMLResponse(
                content=f"<div class='p-4 bg-red-50 text-red-800 text-xs font-bold'>Error: {str(e)}</div>",
                status_code=500
            )


    @staticmethod
    async def obtener_estadisticas_resumen():
        with SessionLocal() as db:
            # 1. Universo total de registros
            cantidad_total_contactos = db.query(func.count(Lead.id)).scalar() or 0
            
            # 2. Conteo de prospectos que no respondieron
            cantidad_contactos_sin_respuesta = db.query(func.count(Lead.id)).filter(
                Lead.comentario.ilike('%Solo Consulto, no respondió%')
            ).scalar() or 0
            
            # 3. Conteo de leads en etapa de seguimiento activo
            cantidad_contactos_en_seguimiento = db.query(func.count(Lead.id)).filter(
                Lead.estado_cliente.ilike('En seguimiento')
            ).scalar() or 0

            # 4. Conteo de leads localizados en España
            cantidad_contactos_desde_espana = db.query(func.count(Lead.id)).filter(
                Lead.ciudad.ilike('España')
            ).scalar() or 0

            # 5. Conteo de leads con interés activo confirmado
            cantidad_contactos_interes_activo = db.query(func.count(Lead.id)).filter(
                Lead.situacion_analisis.ilike('Interés activo')
            ).scalar() or 0

            # 6. Conteo de leads pendientes de reconexión (Dato Real)
            cantidad_contactos_pendientes_reconexion = db.query(func.count(Lead.id)).filter(
                Lead.proxima_accion.ilike('Reintentar contacto')
            ).scalar() or 0
            
            # --- Lógica de Cálculos de Porcentaje ---
            porcentaje_sin_respuesta = 0
            tasa_conversion_efectiva = 0
            
            if cantidad_total_contactos > 0:
                # Porcentaje de nula respuesta
                porcentaje_sin_respuesta = (cantidad_contactos_sin_respuesta / cantidad_total_contactos) * 100
                
                # Conversión = (Interés Activo / Total) * 100
                tasa_conversion_efectiva = (cantidad_contactos_interes_activo / cantidad_total_contactos) * 100

            return {
                "total_contactos": cantidad_total_contactos,
                "sin_respuesta_pct": f"{porcentaje_sin_respuesta:.1f}%",
                "en_seguimiento": cantidad_contactos_en_seguimiento,
                "desde_espana": cantidad_contactos_desde_espana,
                "interes_confirmado": cantidad_contactos_interes_activo,
                "pendientes_reconectar": cantidad_contactos_pendientes_reconexion,
                "conversion_pct": f"{tasa_conversion_efectiva:.1f}%",
                
                # Único placeholder restante (requiere comparativa histórica mensual)
                "caida_leads": "-"
            }