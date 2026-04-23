import pandas as pd
import io
import numpy as np
from starlette.responses import HTMLResponse
from app.models.lead import Lead
from app.database import get_db # Importamos el nuevo motor
from sqlalchemy import delete, func, select

class LeadService:
    @staticmethod
    async def ejecutar_migracion_y_responder(archivo) -> HTMLResponse:
        try:
            contenido = await archivo.read()
            df = pd.read_excel(io.BytesIO(contenido))
            
            # Limpieza global de nulos
            df = df.astype(object).replace({np.nan: None})
            registros_creados = 0
            
            async with get_db() as session:
                for _, row in df.iterrows():
                    def get_val(idx):
                        try:
                            val = row.iloc[idx]
                            return str(val).strip() if val is not None and str(val).lower() != 'nan' else None
                        except:
                            return None

                    # Procesamiento de fecha
                    raw_fecha = row.iloc[2]
                    fecha_db = None
                    if raw_fecha:
                        try:
                            fecha_db = pd.to_datetime(raw_fecha, dayfirst=True).strftime('%Y-%m-%d')
                        except:
                            fecha_db = get_val(2)

                    nuevo_lead = Lead(
                        id_excel=get_val(0),
                        nombre_apellido=get_val(1),
                        fecha_contacto=fecha_db,
                        telefono=get_val(3),
                        ciudad=get_val(4),
                        origen_contacto=get_val(5),
                        interes_cliente=get_val(6),
                        rango_precios=get_val(7),
                        estado_cliente=get_val(8),
                        proxima_accion=get_val(9),
                        fecha_ultimo_contacto=get_val(10),
                        comentario=get_val(11),
                        observaciones=get_val(12),
                        situacion_analisis=get_val(13)
                    )

                    if nuevo_lead.nombre_apellido:
                        # Verificación de duplicados (Async)
                        exists = None
                        if nuevo_lead.id_excel:
                            stmt = select(Lead).where(Lead.id_excel == nuevo_lead.id_excel)
                            result = await session.execute(stmt)
                            exists = result.scalar_one_or_none()
                        
                        if not exists:
                            session.add(nuevo_lead)
                            registros_creados += 1
                
                # El commit se hace automáticamente al salir del bloque async with get_db()

            return HTMLResponse(content=f"""
                <div class="animate-fade-in p-4 rounded-xl border border-green-200 bg-green-50 flex items-center gap-4">
                    <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center" style="background: rgba(34, 197, 94, 0.1);">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <p class="text-sm font-bold text-green-800">Migración Finalizada</p>
                        <p class="text-xs text-green-700">Se procesaron <span class="font-bold">{registros_creados}</span> registros.</p>
                    </div>
                </div>
            """)

        except Exception as e:
            return HTMLResponse(content=f"<div class='p-4 bg-red-50 text-red-800 text-xs'>Error: {str(e)}</div>", status_code=500)

    @staticmethod
    async def limpiar_tabla_y_responder() -> HTMLResponse:
        try:
            async with get_db() as session:
                result = await session.execute(delete(Lead))
                count = result.rowcount
            
            return HTMLResponse(content=f"<div class='p-4 bg-green-50 text-green-800 text-xs'>Tabla vaciada: {count} registros eliminados.</div>")
        except Exception as e:
            return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

    @staticmethod
    async def obtener_estadisticas_resumen():
        async with get_db() as session:
            # Helper para conteos rápidos con filtros
            async def count_where(condition=None):
                stmt = select(func.count(Lead.id))
                if condition is not None:
                    stmt = stmt.where(condition)
                res = await session.execute(stmt)
                return res.scalar() or 0

            # Consultas asincrónicas
            total = await count_where()
            sin_resp = await count_where(Lead.comentario.ilike('%Solo Consulto, no respondió%'))
            seguimiento = await count_where(Lead.estado_cliente.ilike('En seguimiento'))
            espana = await count_where(Lead.ciudad.ilike('España'))
            interes_activo = await count_where(Lead.situacion_analisis.ilike('Interés activo'))
            reconexion = await count_where(Lead.proxima_accion.ilike('Reintentar contacto'))

            # Cálculos
            pct_sin_resp = (sin_resp / total * 100) if total > 0 else 0
            tasa_conv = (interes_activo / total * 100) if total > 0 else 0

            return {
                "total_contactos": total,
                "sin_respuesta_pct": f"{pct_sin_resp:.1f}%",
                "en_seguimiento": seguimiento,
                "desde_espana": espana,
                "interes_confirmado": interes_activo,
                "pendientes_reconectar": reconexion,
                "conversion_pct": f"{tasa_conv:.1f}%",
                "caida_leads": "-"
            }