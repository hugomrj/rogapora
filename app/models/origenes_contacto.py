from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class OrigenContacto(Base):
    __tablename__ = "origenes_contacto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    tipo = Column(String(50))
    activo = Column(Integer, default=True) # O Boolean dependiendo de tu configuración
    created_at = Column(DateTime, server_default=func.now())
