# initdb.py
import sys
from sqlalchemy import text
from app.config import engine

# Tabla principal de leads (sin cambios en tu estructura)
CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    id_excel VARCHAR(100), 
    nombre_apellido TEXT,
    fecha_contacto TEXT,
    telefono VARCHAR(100),
    ciudad TEXT,
    origen_contacto VARCHAR(100),  -- Acá va: 'Instagram', 'Recomendación', etc.
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

# Catálogo único de orígenes (para mantener consistencia)
CREATE_ORIGENES_TABLE = """
CREATE TABLE IF NOT EXISTS origenes_contacto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,  -- 'Instagram', 'Recomendación', 'Web', etc.
    tipo VARCHAR(50),                      -- 'digital', 'offline', 'referido' (opcional)
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tabla de solicitudes pendientes (pre-leads)
CREATE_SOLICITUDES_TABLE = """
CREATE TABLE IF NOT EXISTS solicitudes_redes (
    id SERIAL PRIMARY KEY,
    
    -- Datos del prospecto
    nombre_apellido TEXT NOT NULL,
    telefono VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    ciudad TEXT,
    interes_cliente TEXT,
    rango_precios VARCHAR(100),
    comentario TEXT,
    
    -- Origen (igual que en leads, para cuando se migre)
    origen_contacto VARCHAR(100),  -- 'Instagram', 'Facebook', etc.
    campana VARCHAR(100),           -- Si querés trackear campañas específicas
    
    -- Estado de revisión
    estado_solicitud VARCHAR(50) DEFAULT 'pendiente',
    
    -- Revisión por equipo
    revisado_por VARCHAR(100),
    fecha_revision TIMESTAMP,
    motivo_rechazo TEXT,
    
    -- Link a lead aprobado
    lead_id INTEGER REFERENCES leads(id),
    
    -- Metadata
    ip_solicitud INET,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Tus orígenes actuales
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

def setup_database():
    print("--- Verificando conexión a PostgreSQL ---")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ [EXITO]: Conexión establecida correctamente.")
            
            print("--- Creando tabla 'leads' ---")
            conn.execute(text(CREATE_LEADS_TABLE))
            
            print("--- Creando tabla 'origenes_contacto' ---")
            conn.execute(text(CREATE_ORIGENES_TABLE))
            
            print("--- Creando tabla 'solicitudes_redes' ---")
            conn.execute(text(CREATE_SOLICITUDES_TABLE))
            
            print("--- Cargando orígenes de contacto ---")
            conn.execute(text(INSERT_ORIGENES))
            
            conn.commit()
            print("✅ [EXITO]: Base de datos lista.")
            
    except Exception as e:
        print("❌ [ERROR]: Hubo un problema.")
        print(f"Detalle: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()