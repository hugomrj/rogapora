# inidb.py
import sys
from sqlalchemy import text
from app.config import engine

# Definición de la tabla (Todo como Texto para la migración del Excel)
CREATE_TABLE_SQL = """
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

def setup_database():
    print("--- Verificando conexión a PostgreSQL ---")
    try:
        with engine.connect() as conn:
            # 1. Test de conexión
            conn.execute(text("SELECT 1"))
            print("✅ [EXITO]: Conexión establecida correctamente.")
            
            # 2. Creación de tabla
            print("--- Creando tabla 'clientes' si no existe ---")
            conn.execute(text(CREATE_TABLE_SQL))
            conn.commit() # Importante para guardar cambios en SQL crudo
            print("✅ [EXITO]: Estructura de base de datos lista.")
            
    except Exception as e:
        print("❌ [ERROR]: Hubo un problema en el proceso.")
        print(f"Detalle: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()