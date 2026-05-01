# app/router.py

from starlette.routing import Mount
from app.routes import web, leads 

routes = [
    
    # leads.routes apunta a la lista del archivo leads.py
    Mount("/leads", routes=leads.routes, name="leads"),

    # web.routes apunta a la lista que acabamos de crear arriba
    Mount("/", routes=web.routes, name="web"),

]

