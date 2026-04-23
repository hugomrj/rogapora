from sqlalchemy import select
from app.models.solicitud import Solicitud
from app.database import get_db  # <--- Importamos desde el nuevo database.py

class SolicitudService:
    @staticmethod
    async def obtener_todas():
        """
        Retorna todas las solicitudes ordenadas por fecha de creación descendente.
        Usa SQLAlchemy Async con el context manager asincrónico.
        """
        async with get_db() as session:
            # Construimos la query usando la sintaxis de SQLAlchemy 2.0 (select)
            query = select(Solicitud).order_by(Solicitud.created_at.desc())
            
            # Ejecutamos de forma asincrónica
            result = await session.execute(query)
            
            # .scalars().all() convierte el resultado en una lista de objetos Solicitud
            return result.scalars().all()