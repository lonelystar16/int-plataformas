from pydantic import BaseModel
from typing import Optional

class PreferenciaRequest(BaseModel):
    title: str
    quantity: int
    unit_price: float
    success_url: Optional[str] = "https://echoapi.io/success"
    failure_url: Optional[str] = "https://echoapi.io/failure"
    pending_url: Optional[str] = "https://echoapi.io/pending"

class PreferenciaResponse(BaseModel):
    init_point: str
    id: str
