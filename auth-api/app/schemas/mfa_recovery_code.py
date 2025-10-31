from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Schemas de Base/CRUD ---

class MFARecoveryCodeBase(BaseModel):
    """Schema base (não deve ser usado diretamente)."""
    # Apenas para fins de type hinting e herança
    pass

class MFARecoveryCodeCreate(MFARecoveryCodeBase):
    """Schema de Criação. Não precisa de campos, pois o CRUD gera os códigos."""
    # O código é gerado internamente; este schema é mínimo.
    pass

class MFARecoveryCodeUpdate(MFARecoveryCodeBase):
    """Schema de Atualização. Usado internamente para marcar como usado."""
    is_used: bool = True
    
# --- Schema de Leitura (Resposta da API) ---
class MFARecoveryCode(MFARecoveryCodeBase):
    id: int
    user_id: int
    is_used: bool
    created_at: datetime
    used_at: Optional[datetime]

    class Config:
        from_attributes = True
