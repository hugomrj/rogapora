# app/models/lead.py
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Lead(Base):
    __tablename__ = "leads"

    # ID interno (Serial en Postgres)
    id = Column(Integer, primary_key=True, index=True)
    
    # Mapeo exacto de tu tabla SQL
    id_excel = Column(String(50), unique=True, index=True)
    nombre_apellido = Column(Text)
    fecha_contacto = Column(Text)
    telefono = Column(String(100))
    ciudad = Column(Text)
    origen_contacto = Column(String(100))
    interes_cliente = Column(Text)
    rango_precios = Column(String(100))
    estado_cliente = Column(Text)
    proxima_accion = Column(Text)
    fecha_ultimo_contacto = Column(Text)
    comentario = Column(Text)
    observaciones = Column(Text)
    situacion_analisis = Column(Text)