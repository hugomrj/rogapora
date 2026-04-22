
# Rogapora

## Requisitos

- Python 3.10+
- PostgreSQL
- pip

---

## Setup del proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/hugomrj/rogapora.git
```

cd rogapora
2. Crear entorno virtual
```
python -m venv venv
```
Activar:

Linux / Mac:
```
source venv/bin/activate
```
Windows:
```
venv\Scripts\activate
```

3. Instalar dependencias
```
pip install -r requirements.txt
```

4. Configurar variables de entorno

Crear un archivo .env en la raíz del proyecto:
```
DB_NAME=rogapora_database
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
```
Agregar .env al .gitignore.

5. Inicializar la base de datos
python inidb.py

Este script:

crea las tablas necesarias
inserta datos iniciales
6. Ejecutar la aplicación
```
uvicorn app.main:app --reload --port 9000 --host 0.0.0.0
```
Stack
```
Starlette (framework ASGI)
Uvicorn (servidor ASGI)
SQLAlchemy (ORM)
PostgreSQL (base de datos)
```

Notas

Se recomienda crear un archivo .env.example con la estructura de variables sin valores sensibles:
```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
```