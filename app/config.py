# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates
from starlette.routing import Route
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Cargamos el .env (buscando en la raíz del proyecto)
load_dotenv()

# 2. Rutas base y Templates
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "web"))

# 3. Configuración de Base de Datos
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

# Construimos la URL para SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Creamos el motor y la sesión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Este es el decorador global que ya tenías
def custom_route(router, path, methods=["GET"]):
    def decorator(func):
        router.routes.append(Route(path, endpoint=func, methods=methods))
        return func
    return decorator

# Función de ayuda para obtener sesión en las rutas
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()