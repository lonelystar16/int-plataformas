from pydantic import BaseModel
from datetime import datetime

class Indicador(BaseModel):
    valor: float
    fecha: datetime
