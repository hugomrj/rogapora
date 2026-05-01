from sqlalchemy.sql import func
from app.config import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    id_excel = Column(String(100), index=True) 
    
    nombre_apellido = Column(Text)
    fecha_contacto = Column(Date)
    telefono = Column(String(100))
    ciudad = Column(Text)
    comentario = Column(Text)
    observaciones = Column(Text)
    situacion_analisis = Column(Text)
    fecha_migracion = Column(DateTime, server_default=func.now())
    
    # Foreign Keys
    origen_contacto_id = Column(Integer, ForeignKey("origenes_contacto.id"))
    interes_cliente_id = Column(Integer, ForeignKey("intereses_cliente.id"))
    rango_precios_id = Column(Integer, ForeignKey("rangos_precio.id"))
    estado_cliente_id = Column(Integer, ForeignKey("estados_cliente.id"))
    proxima_accion_id = Column(Integer, ForeignKey("proximas_acciones.id"))
    
    # Relaciones ORM
    # Usamos string references para evitar errores de importación circular
    origen = relationship("OrigenContacto")
    interes = relationship("InteresCliente")
    rango = relationship("RangoPrecio")
    estado = relationship("EstadoCliente")
    accion = relationship("ProximaAccion")


    