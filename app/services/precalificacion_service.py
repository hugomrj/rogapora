import json
from datetime import datetime
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.config import SessionLocal
from app.models.solicitud import Solicitud

class PrecalificacionService:
    @staticmethod
    async def guardar_solicitud(data: dict):
        """
        Recibe el diccionario con los datos del formulario,
        realiza las conversiones de tipos necesarias y guarda en DB
        utilizando un hilo aparte para no bloquear el event loop.
        """
        
        def _guardar_en_db():
            with SessionLocal() as db:
                # 1. Manejo de Fecha: Convertimos string "YYYY-MM-DD" a objeto date
                fecha_str = data.get('fecha_nacimiento')
                fecha_dt = None
                if fecha_str:
                    try:
                        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    except ValueError:
                        fecha_dt = None

                # 2. Manejo de Deudas: 
                # Si tu DB es PostgreSQL con JSONB, data.get('deudas') está bien.
                # Si es String/VARCHAR, descomenta la siguiente línea:
                # deudas_data = json.dumps(data.get('deudas', []))
                deudas_data = data.get('deudas', [])

                # 3. Creación de la instancia del modelo
                nueva_solicitud = Solicitud(
                    # Datos Personales
                    nombre=data.get('nombre'),
                    cedula=data.get('cedula'),
                    fecha_nacimiento=fecha_dt,
                    email=data.get('email'),
                    telefono=data.get('telefono'),
                    
                    # Perfil y Educación
                    nivel_educativo=data.get('nivel_educativo'),
                    tipo_empleo=data.get('tipo_empleo'),
                    
                    # Ingresos (Aseguramos que sean numéricos o 0)
                    ingreso_principal=float(data.get('ingreso_principal') or 0),
                    ingreso_adicional=float(data.get('ingreso_adicional') or 0),
                    ingreso_pareja=float(data.get('ingreso_pareja') or 0),
                    
                    # Gastos
                    gasto_alquiler=float(data.get('gasto_alquiler') or 0),
                    gasto_servicios=float(data.get('gasto_servicios') or 0),
                    gasto_alimentacion=float(data.get('gasto_alimentacion') or 0),
                    gasto_salud=float(data.get('gasto_salud') or 0),
                    
                    # Buró y Estado Financiero
                    deudas=deudas_data,
                    informconf=bool(data.get('informconf', False)),
                    atrasos_90=bool(data.get('atrasos_90', False)),
                    
                    # Preferencias de Vivienda
                    ubicacion_preferida=data.get('ubicacion_preferida'),
                    tipo_vivienda=data.get('tipo_vivienda'),
                    presupuesto_maximo=float(data.get('presupuesto_maximo') or 0),
                    entrega_inicial=float(data.get('entrega_inicial') or 0),
                    
                    # Marketing / Origen
                    origen_contacto=data.get('origen_contacto', 'desconocido'),
                    campana=data.get('campana', 'organico')
                )
                
                db.add(nueva_solicitud)
                db.commit()
                db.refresh(nueva_solicitud)
                return nueva_solicitud

        # Ejecución asíncrona de la lógica síncrona de SQLAlchemy
        return await run_in_threadpool(_guardar_en_db)