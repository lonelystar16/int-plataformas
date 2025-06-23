from app.productos.interfaces.router import router as productos_router
from app.banco_central.interfaces.router import router as banco_central_router
from app.mercado_pago.interfaces.router import router as mercado_pago_router
from fastapi import FastAPI
app = FastAPI(title="API Externa en Capas")
app.include_router(productos_router, prefix="/productos", tags=["Productos"])
app.include_router(banco_central_router, prefix="/banco-central", tags=["Banco Central"])
app.include_router(mercado_pago_router, prefix="/mercado-pago", tags=["Mercado Pago"])