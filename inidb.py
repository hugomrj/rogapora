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
SYS_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"
APP_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# --- SQL DE LAS TABLAS ---

# 1. Tabla de Orígenes (Existente)
CREATE_ORIGENES_TABLE = """
CREATE TABLE IF NOT EXISTS origenes_contacto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    tipo VARCHAR(50), -- 'digital', 'referido', 'web'
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_ORIGENES = """
INSERT INTO origenes_contacto (nombre, tipo) VALUES 
    ('Instagram', 'digital'),
    ('Tik Tok', 'digital'),
    ('Facebook', 'digital'),
    ('Recomendación', 'referido'),
    ('Recomendación Bco. Itau', 'referido'),
    ('Web Che Roga Porá', 'web'),
    ('Web Propia', 'web')
ON CONFLICT (nombre) DO NOTHING;
"""

# 2. Nuevas Tablas de Catálogo
CREATE_INTERESES_TABLE = """
CREATE TABLE IF NOT EXISTS intereses_cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
"""

CREATE_RANGOS_PRECIO_TABLE = """
CREATE TABLE IF NOT EXISTS rangos_precio (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
"""

CREATE_ESTADOS_CLIENTE_TABLE = """
CREATE TABLE IF NOT EXISTS estados_cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
"""

CREATE_PROXIMAS_ACCIONES_TABLE = """
CREATE TABLE IF NOT EXISTS proximas_acciones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
"""

# Inserts para nuevos catálogos
INSERT_INTERESES = """
INSERT INTO intereses_cliente (nombre) VALUES 
    ('Che Roga Pora'), ('Duplex'), ('Vivienda'), 
    ('Casa + Terreno'), ('Alquiler'), ('Comercio'), ('Sin Datos') 
ON CONFLICT (nombre) DO NOTHING;
"""

INSERT_RANGOS = """
INSERT INTO rangos_precio (nombre) VALUES 
    ('Bajo'), ('Medio'), ('Alto'), ('Sin Datos') 
ON CONFLICT (nombre) DO NOTHING;
"""

INSERT_ESTADOS = """
INSERT INTO estados_cliente (nombre) VALUES 
    ('Contactado (sin respuesta)'), ('No interesado'), ('En seguimiento') 
ON CONFLICT (nombre) DO NOTHING;
"""

INSERT_ACCIONES = """
INSERT INTO proximas_acciones (nombre) VALUES 
    ('Seguimiento'), ('Definir propuesta'), ('Esperar Condición Externa'), 
    ('Descartar Cliente'), ('Reintentar contacto') 
ON CONFLICT (nombre) DO NOTHING;
"""

# 3. Tabla Leads Actualizada (Con FKs a las nuevas tablas)
# Nota: Se eliminaron campos antiguos como texto libre de estado/interés para usar las FKs
CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    id_excel VARCHAR(100), 
    nombre_apellido TEXT,
    fecha_contacto DATE,
    telefono VARCHAR(100),
    ciudad TEXT,
    
    -- FKs a catálogos
    origen_contacto_id INTEGER REFERENCES origenes_contacto(id),
    interes_cliente_id INTEGER REFERENCES intereses_cliente(id),
    rango_precios_id INTEGER REFERENCES rangos_precio(id),
    estado_cliente_id INTEGER REFERENCES estados_cliente(id),
    proxima_accion_id INTEGER REFERENCES proximas_acciones(id),
    
    comentario TEXT,
    observaciones TEXT,
    situacion_analisis TEXT,
    fecha_migracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 4. Tabla Solicitudes (Existente)
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
        with engine_app.begin() as conn:
            # 1. Crear tablas de catálogo primero (para las Foreign Keys)
            print("Creando tablas de catálogo...")
            conn.execute(text(CREATE_ORIGENES_TABLE))
            conn.execute(text(CREATE_INTERESES_TABLE))
            conn.execute(text(CREATE_RANGOS_PRECIO_TABLE))
            conn.execute(text(CREATE_ESTADOS_CLIENTE_TABLE))
            conn.execute(text(CREATE_PROXIMAS_ACCIONES_TABLE))
            
            # 2. Crear tabla de leads (depende de las anteriores)
            print("Creando tabla 'leads'...")
            conn.execute(text(CREATE_LEADS_TABLE))
            
            # 3. Crear tabla solicitudes
            print("Creando tabla 'solicitudes'...")
            conn.execute(text(CREATE_SOLICITUDES_TABLE))
            
            # 4. Insertar datos iniciales en catálogos
            print("Cargando datos iniciales...")
            conn.execute(text(INSERT_ORIGENES))
            conn.execute(text(INSERT_INTERESES))
            conn.execute(text(INSERT_RANGOS))
            conn.execute(text(INSERT_ESTADOS))
            conn.execute(text(INSERT_ACCIONES))
            
        print("✅ [EXITO]: Esquema de base de datos actualizado y listo.")
        
    except Exception as e:
        print(f"❌ [ERROR]: Error al crear el esquema: {e}")
        sys.exit(1)
    finally:
        engine_app.dispose()

if __name__ == "__main__":
    create_database()
    setup_schema()