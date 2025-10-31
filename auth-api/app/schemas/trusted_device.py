from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Schemas de Base/CRUD ---

class TrustedDeviceBase(BaseModel):
    """Schema base para TrustedDevice."""
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class TrustedDeviceCreate(TrustedDeviceBase):
    """Schema usado pelo CRUD para criar um dispositivo. Apenas metadados."""
    # O token e a expiração são gerados na lógica de CRUD.
    pass

class TrustedDeviceUpdate(TrustedDeviceBase):
    """Schema de Atualização."""
    # Raramente usado, mas necessário para CRUDBase.
    pass

# --- Schema de Leitura (Resposta da API) ---

class TrustedDeviceInfo(TrustedDeviceBase):
    """Schema de saída para listar dispositivos confiáveis (sessões)."""
    id: int
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
