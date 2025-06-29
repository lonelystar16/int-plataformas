from app.productos.interfaces.router import router as productos_router
from app.banco_central.interfaces.router import router as banco_central_router
from app.mercado_pago.interfaces.router import router as mercado_pago_router

from app.core.database import engine, Base

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os



templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


app = FastAPI(title="API Externa en Capas")
# Configuración de CORS
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(productos_router, prefix="/productos", tags=["Productos"])
app.include_router(banco_central_router, prefix="/banco-central", tags=["Banco Central"])
app.include_router(mercado_pago_router, prefix="/mercado-pago", tags=["Mercado Pago"])