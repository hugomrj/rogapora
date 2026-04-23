from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.models import Solicitud  # Asegúrate de importar tu modelo
from starlette.concurrency import run_in_threadpool

class PrecalificacionService:
    
    @staticmethod
    async def guardar_solicitud(data: dict):
        """
        Recibe el diccionario con los datos del formulario,
        crea el objeto y lo guarda en la DB.
        """
        
        # Función síncrona que ejecuta la lógica de DB
        def _guardar_en_db():
            with SessionLocal() as db:
                nueva_solicitud = Solicitud(
                    # Datos Personales
                    nombre=data.get('nombre'),
                    cedula=data.get('cedula'),
                    fecha_nacimiento=data.get('fecha_nacimiento'),
                    email=data.get('email'),
                    telefono=data.get('telefono'),
                    
                    # Perfil
                    nivel_educativo=data.get('nivel_educativo'),
                    tipo_empleo=data.get('tipo_empleo'),
                    
                    # Ingresos
                    ingreso_principal=data.get('ingreso_principal'),
                    ingreso_adicional=data.get('ingreso_adicional'),
                    ingreso_pareja=data.get('ingreso_pareja'),
                    
                    # Gastos
                    gasto_alquiler=data.get('gasto_alquiler'),
                    gasto_servicios=data.get('gasto_servicios'),
                    gasto_alimentacion=data.get('gasto_alimentacion'),
                    gasto_salud=data.get('gasto_salud'),
                    
                    # Deudas y Buró
                    deudas=data.get('deudas'), # Asegúrate que tu modelo acepte JSON o string
                    informconf=data.get('informconf', False),
                    atrasos_90=data.get('atrasos_90', False),
                    
                    # Vivienda
                    ubicacion_preferida=data.get('ubicacion_preferida'),
                    tipo_vivienda=data.get('tipo_vivienda'),
                    presupuesto_maximo=data.get('presupuesto_maximo'),
                    entrega_inicial=data.get('entrega_inicial'),
                    
                    # Marketing
                    origen_contacto=data.get('origen_contacto'),
                    campana=data.get('campana')
                )
                
                db.add(nueva_solicitud)
                db.commit()
                db.refresh(nueva_solicitud)
                return nueva_solicitud

        # Ejecutamos la función síncrona en un hilo aparte
        # Esto es CRUCIAL en Starlette/FastAPI cuando usas DB síncronas (como psycopg2)
        return await run_in_threadpool(_guardar_en_db)