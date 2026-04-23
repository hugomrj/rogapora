# app/models
from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Datos Personales
    nombre = Column(String(255), nullable=False)
    cedula = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date)
    email = Column(String(255))
    telefono = Column(String(50))
    
    # Perfil Profesional
    nivel_educativo = Column(String(50))
    tipo_empleo = Column(String(50))
    
    # Ingresos (Precisión para Guaraníes)
    ingreso_principal = Column(Numeric(15, 2))
    ingreso_adicional = Column(Numeric(15, 2))
    ingreso_pareja = Column(Numeric(15, 2))
    
    # Gastos
    gasto_alquiler = Column(Numeric(15, 2))
    gasto_servicios = Column(Numeric(15, 2))
    gasto_alimentacion = Column(Numeric(15, 2))
    gasto_salud = Column(Numeric(15, 2))
    
    # Deudas (JSONB es excelente para listas dinámicas en Postgres)
    deudas = Column(JSONB)
    
    # Buró / Historial
    informconf = Column(Boolean, default=False)
    atrasos_90 = Column(Boolean, default=False)
    
    # Vivienda deseada
    ubicacion_preferida = Column(String(255))
    tipo_vivienda = Column(String(50))
    presupuesto_maximo = Column(Numeric(15, 2))
    entrega_inicial = Column(Numeric(15, 2))
    
    # Administración
    estado = Column(String(20), default='pendiente')
    
    # Marketing / Trazabilidad
    origen_contacto = Column(String(50))
    campana = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())

    # === PROPIEDADES CALCULADAS ===
    @property
    def ingreso_total(self):
        """Suma de todos los ingresos del postulante"""
        return (self.ingreso_principal or 0) + \
               (self.ingreso_adicional or 0) + \
               (self.ingreso_pareja or 0)

    @property
    def capacidad_estimada(self):
        return float(self.ingreso_total) * 0.4


    def __repr__(self):
        return f"<Solicitud(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"
    


    