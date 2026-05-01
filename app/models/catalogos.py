from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config import Base


class EstadoCliente(Base):
    __tablename__ = "estados_cliente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)



# Clases de Catálogo
class InteresCliente(Base):
    __tablename__ = "intereses_cliente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)


class RangoPrecio(Base):
    __tablename__ = "rangos_precio"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)



class ProximaAccion(Base):
    __tablename__ = "proximas_acciones"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True)
