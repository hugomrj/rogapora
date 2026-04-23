# app/models/precalificador.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    # Datos personales
    nombre = Column(String)
    cedula = Column(String, unique=True)
    fecha_nacimiento = Column(DateTime)
    edad = Column(Integer)
    email = Column(String)
    telefono = Column(String)
    # Perfil socioeconómico
    nivel_educativo = Column(String)
    tipo_empleo = Column(String)  # dependiente/independiente/emprendedor
    # Ingresos
    ingreso_principal = Column(Float)
    ingreso_adicional = Column(Float, default=0)
    ingreso_pareja = Column(Float, default=0)
    ingreso_total = Column(Float)
    # Gastos
    gasto_alquiler = Column(Float, default=0)
    gasto_servicios = Column(Float, default=0)
    gasto_alimentacion = Column(Float, default=0)
    gasto_transporte = Column(Float, default=0)
    gasto_educacion = Column(Float, default=0)
    gasto_salud = Column(Float, default=0)
    gasto_otros = Column(Float, default=0)
    gasto_total = Column(Float)
    # Deudas
    deudas = Column(JSON)  # lista de {tipo, monto, cuota_mensual, estado}
    total_cuotas_deudas = Column(Float)
    # Información crediticia
    informconf = Column(Boolean)  # True = aparece en Informconf
    atrasos_90 = Column(Boolean)
    comportamiento_pago = Column(String)  # bueno, regular, malo
    # Interés de compra
    tipo_vivienda = Column(String)
    ubicacion_preferida = Column(String)
    presupuesto_maximo = Column(Float)
    entrega_inicial = Column(Float)
    # Campos calculados
    capacidad_pago = Column(Float)
    ratio_endeudamiento = Column(Float)
    score_interno = Column(Integer)
    clasificacion = Column(String)  # apto / potencial / no_apto
    # Tracking
    origen_contacto = Column(String)
    campana = Column(String)
    ip_cliente = Column(String)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())



