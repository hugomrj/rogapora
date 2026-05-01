# app/services/lead_service.py
import pandas as pd
import io
import numpy as np
from starlette.responses import HTMLResponse
from app.config import SessionLocal
from sqlalchemy import delete, func

from app.models.catalogos import EstadoCliente, InteresCliente, ProximaAccion, RangoPrecio
from app.models.lead import Lead
from app.models.origenes_contacto import OrigenContacto

class LeadService:
    
    @staticmethod
    async def ejecutar_migracion_y_responder(archivo) -> HTMLResponse:
        try:
            contenido = await archivo.read()
            df = pd.read_excel(io.BytesIO(contenido))
            
            # Limpieza global de nulos de Pandas (NaN) a None de Python
            df = df.astype(object).replace({np.nan: None})
            registros_creados = 0
            
            with SessionLocal() as db:
                # --- 1. PRE-CARGA DE CATÁLOGOS EN MEMORIA ---
                # Esto es mucho más rápido que buscar en la DB por cada fila
                def get_map(model_class):
                    return {item.nombre: item.id for item in db.query(model_class).all()}

                origenes_map = get_map(OrigenContacto)
                intereses_map = get_map(InteresCliente)
                rangos_map = get_map(RangoPrecio)
                estados_map = get_map(EstadoCliente)
                acciones_map = get_map(ProximaAccion)

                # Helper para obtener valor por índice
                def get_val(idx):
                    try:
                        val = row.iloc[idx]
                        return str(val).strip() if val is not None and str(val).lower() != 'nan' else None
                    except:
                        return None

                # --- 2. ITERACIÓN DEL EXCEL ---
                for _, row in df.iterrows():
                    # Tratamiento de Fecha
                    raw_fecha = row.iloc[2]
                    fecha_db = None
                    if raw_fecha:
                        try:
                            fecha_db = pd.to_datetime(raw_fecha, dayfirst=True).strftime('%Y-%m-%d')
                        except:
                            fecha_db = get_val(2)

                    # Obtención de valores de texto del Excel
                    txt_origen = get_val(5)
                    txt_interes = get_val(6)
                    txt_rango = get_val(7)
                    txt_estado = get_val(8)
                    txt_accion = get_val(9)

                    # --- 3. CREACIÓN DEL LEAD CON IDs ---
                    # Nota: Se eliminaron campos que no están en tu nueva estructura (fecha_ultimo_contacto, etc.)
                    nuevo_lead = Lead(
                        id_excel=get_val(0),
                        nombre_apellido=get_val(1),
                        fecha_contacto=fecha_db,
                        telefono=get_val(3),
                        ciudad=get_val(4),
                        
                        # Mapeo de Texto -> ID (usando los diccionarios cargados)
                        # Si el texto no existe en el catálogo, asigna None
                        origen_contacto_id=origenes_map.get(txt_origen),
                        interes_cliente_id=intereses_map.get(txt_interes),
                        rango_precios_id=rangos_map.get(txt_rango),
                        estado_cliente_id=estados_map.get(txt_estado),
                        proxima_accion_id=acciones_map.get(txt_accion),
                        
                        # Campos de texto directo
                        comentario=get_val(11),        # Ajustar índice si hizo falta
                        observaciones=get_val(12),     # Ajustar índice si hizo falta
                        situacion_analisis=get_val(13) # Ajustar índice si hizo falta
                    )

                    if nuevo_lead.nombre_apellido:
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
            with SessionLocal() as db:
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
                        <p class="text-sm font-bold text-green-800">Tabla vaciada</p>
                        <p class="text-xs text-green-700">Se eliminaron correctamente <span class="font-bold">{count}</span> registros.</p>
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
            # 1. Universo total
            cantidad_total_contactos = db.query(func.count(Lead.id)).scalar() or 0
            
            # 2. Conteo por comentario (Texto libre, sigue igual)
            cantidad_contactos_sin_respuesta = db.query(func.count(Lead.id)).filter(
                Lead.comentario.ilike('%Solo Consulto, no respondió%')
            ).scalar() or 0
            
            # 3. Conteo por Estado (Ahora es FK, necesitamos el ID del estado)
            # Buscamos el ID del estado "En seguimiento"
            estado_seg = db.query(EstadoCliente.id).filter(EstadoCliente.nombre == 'En seguimiento').first()
            cantidad_contactos_en_seguimiento = 0
            if estado_seg:
                cantidad_contactos_en_seguimiento = db.query(func.count(Lead.id)).filter(
                    Lead.estado_cliente_id == estado_seg.id
                ).scalar() or 0

            # 4. Ciudad (Texto libre, sigue igual)
            cantidad_contactos_desde_espana = db.query(func.count(Lead.id)).filter(
                Lead.ciudad.ilike('España')
            ).scalar() or 0

            # 5. Situación Análisis (Texto libre, sigue igual)
            cantidad_contactos_interes_activo = db.query(func.count(Lead.id)).filter(
                Lead.situacion_analisis.ilike('Interés activo')
            ).scalar() or 0

            # 6. Próxima Acción (Ahora es FK)
            # Buscamos el ID de la acción "Reintentar contacto"
            accion_reintentar = db.query(ProximaAccion.id).filter(ProximaAccion.nombre == 'Reintentar contacto').first()
            cantidad_contactos_pendientes_reconexion = 0
            if accion_reintentar:
                cantidad_contactos_pendientes_reconexion = db.query(func.count(Lead.id)).filter(
                    Lead.proxima_accion_id == accion_reintentar.id
                ).scalar() or 0
            
            # --- Cálculos de Porcentaje ---
            porcentaje_sin_respuesta = 0
            tasa_conversion_efectiva = 0
            
            if cantidad_total_contactos > 0:
                porcentaje_sin_respuesta = (cantidad_contactos_sin_respuesta / cantidad_total_contactos) * 100
                tasa_conversion_efectiva = (cantidad_contactos_interes_activo / cantidad_total_contactos) * 100

            return {
                "total_contactos": cantidad_total_contactos,
                "sin_respuesta_pct": f"{porcentaje_sin_respuesta:.1f}%",
                "en_seguimiento": cantidad_contactos_en_seguimiento,
                "desde_espana": cantidad_contactos_desde_espana,
                "interes_confirmado": cantidad_contactos_interes_activo,
                "pendientes_reconectar": cantidad_contactos_pendientes_reconexion,
                "conversion_pct": f"{tasa_conversion_efectiva:.1f}%",
                "caida_leads": "-"
            }


