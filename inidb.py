import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "rogapora_database")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin12345")
DB_HOST = os.getenv("DB_HOST", "localhost")

# URLs de conexión
# Conexión a la DB del sistema para crear la base de datos destino
SYS_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"
# Conexión a la DB de la aplicación
APP_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# --- SQL DE LAS TABLAS ---

CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    id_excel VARCHAR(100), 
    nombre_apellido TEXT,
    fecha_contacto TEXT,
    telefono VARCHAR(100),
    ciudad TEXT,
    origen_contacto VARCHAR(100),
    interes_cliente TEXT,
    rango_precios VARCHAR(100),
    estado_cliente TEXT,
    proxima_accion TEXT,
    fecha_ultimo_contacto TEXT,
    comentario TEXT,
    observaciones TEXT,
    situacion_analisis TEXT,
    fecha_migracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ORIGENES_TABLE = """
CREATE TABLE IF NOT EXISTS origenes_contacto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_ORIGENES = """
INSERT INTO origenes_contacto (nombre, tipo) VALUES 
    ('Recomendación', 'referido'),
    ('Instagram', 'digital'),
    ('Tik Tok', 'digital'),
    ('Facebook', 'digital'),
    ('Recomendación Bco. Itau', 'referido'),
    ('Web Che Roga Porá', 'web')
ON CONFLICT (nombre) DO NOTHING;
"""


CREATE_SOLICITUDES_TABLE = """
CREATE TABLE solicitudes (
    id SERIAL PRIMARY KEY,
    
    -- Datos Personales
    nombre VARCHAR(255) NOT NULL,
    cedula VARCHAR(20) NOT NULL,
    fecha_nacimiento DATE,
    email VARCHAR(255),
    telefono VARCHAR(50),
    
    -- Perfil Profesional
    nivel_educativo VARCHAR(50),
    tipo_empleo VARCHAR(50),
    
    -- Ingresos (usamos NUMERIC para guaraníes)
    ingreso_principal NUMERIC(15, 2),
    ingreso_adicional NUMERIC(15, 2),
    ingreso_pareja NUMERIC(15, 2),
    
    -- Gastos
    gasto_alquiler NUMERIC(15, 2),
    gasto_servicios NUMERIC(15, 2),
    gasto_alimentacion NUMERIC(15, 2),
    gasto_salud NUMERIC(15, 2),
    
    -- Deudas (Guardaremos la lista dinámica como JSONB)
    deudas JSONB, 
    
    -- Buró / Historial
    informconf BOOLEAN DEFAULT FALSE,
    atrasos_90 BOOLEAN DEFAULT FALSE,
    
    -- Vivienda deseada
    ubicacion_preferida VARCHAR(255),
    tipo_vivienda VARCHAR(50),
    presupuesto_maximo NUMERIC(15, 2),
    entrega_inicial NUMERIC(15, 2),
    
    -- CAMPO SOLO PARA ADMIN (Backoffice)
    -- 'pendiente', 'validado', 'rechazado'
    estado VARCHAR(20) DEFAULT 'pendiente',
    
    -- Marketing / Trazabilidad
    origen_contacto VARCHAR(50),
    campana VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""




def create_database():
    """Crea la base de datos física si no existe."""
    print(f"--- Verificando existencia de la base de datos: {DB_NAME} ---")
    engine_sys = create_engine(SYS_DB_URL, isolation_level="AUTOCOMMIT")
    
    try:
        with engine_sys.connect() as conn:
            # Verificar si la DB ya existe
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
            exists = result.scalar()
            
            if not exists:
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                print(f"✅ [EXITO]: Base de datos '{DB_NAME}' creada.")
            else:
                print(f"ℹ️ [INFO]: La base de datos '{DB_NAME}' ya existe.")
                
    except Exception as e:
        print(f"❌ [ERROR]: No se pudo crear la base de datos: {e}")
        sys.exit(1)
    finally:
        engine_sys.dispose()

def setup_schema():
    """Crea las tablas e inserta datos iniciales."""
    print(f"--- Conectando a {DB_NAME} para crear el esquema ---")
    engine_app = create_engine(APP_DB_URL)
    
    try:
        with engine_app.begin() as conn:  # .begin() maneja el COMMIT automáticamente
            print("Creando tabla 'leads'...")
            conn.execute(text(CREATE_LEADS_TABLE))
            
            print("Creando tabla 'origenes_contacto'...")
            conn.execute(text(CREATE_ORIGENES_TABLE))
            
            print("Creando tabla 'solicitudes'...")
            conn.execute(text(CREATE_SOLICITUDES_TABLE))
            
            print("Cargando datos iniciales de orígenes...")
            conn.execute(text(INSERT_ORIGENES))

            print("Cargando datos iniciales de orígenes...")
            conn.execute(text(INSERT_ORIGENES))

            
        print("✅ [EXITO]: Esquema de base de datos listo.")
        
    except Exception as e:
        print(f"❌ [ERROR]: Error al crear el esquema: {e}")
        sys.exit(1)
    finally:
        engine_app.dispose()

if __name__ == "__main__":
    # Primero creamos el contenedor (la DB)
    create_database()
    # Luego creamos el contenido (las tablas)
    setup_schema()