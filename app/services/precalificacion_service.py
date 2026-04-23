from datetime import datetime
from app.database import get_db  # Importamos el nuevo motor asincrónico
from app.models.solicitud import Solicitud

class PrecalificacionService:
    @staticmethod
    async def guardar_solicitud(data: dict):
        """
        Guarda la solicitud de forma asincrónica nativa.
        Ya no requiere run_in_threadpool.
        """
        
        # 1. Preparación de datos (Conversión de tipos)
        fecha_str = data.get('fecha_nacimiento')
        fecha_dt = None
        if fecha_str:
            try:
                # Si viene como string, lo pasamos a objeto date
                fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_dt = None

        # 2. Uso del context manager asincrónico
        async with get_db() as session:
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
                
                # Ingresos (Convertimos a float para el tipo Numeric de SQLAlchemy)
                ingreso_principal=float(data.get('ingreso_principal') or 0),
                ingreso_adicional=float(data.get('ingreso_adicional') or 0),
                ingreso_pareja=float(data.get('ingreso_pareja') or 0),
                
                # Gastos
                gasto_alquiler=float(data.get('gasto_alquiler') or 0),
                gasto_servicios=float(data.get('gasto_servicios') or 0),
                gasto_alimentacion=float(data.get('gasto_alimentacion') or 0),
                gasto_salud=float(data.get('gasto_salud') or 0),
                
                # Buró y Estado Financiero
                deudas=data.get('deudas', []),
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
            
            session.add(nueva_solicitud)
            # El commit y el close se manejan automáticamente por el @asynccontextmanager
            # que definimos en database.py. Solo hacemos flush si necesitamos el ID de vuelta.
            await session.flush() 
            
            return nueva_solicitud