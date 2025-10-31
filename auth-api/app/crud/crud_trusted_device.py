import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.crud.base import CRUDBase # <-- Garante que CRUDBase está definido
from app.models.trusted_device import TrustedDevice
# --- CORREÇÃO: Importar os Schemas necessários para a definição da classe ---
from app.schemas.trusted_device import TrustedDeviceCreate, TrustedDeviceUpdate, TrustedDeviceInfo
# --- FIM CORREÇÃO ---
from app.models.user import User
from app.core.config import settings

# A classe agora pode ser definida porque todos os tipos são conhecidos
class CRUDTrustedDevice(CRUDBase[TrustedDevice, TrustedDeviceCreate, TrustedDeviceUpdate]):

    def hash_device_token(self, token: str) -> str:
        """Gera um hash SHA-256 para o token do dispositivo."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def generate_plain_token(self) -> str:
        """Gera um token seguro de 64 bytes."""
        return secrets.token_urlsafe(64)

    async def create_trusted_device(
        self, 
        db: AsyncSession, 
        *, 
        user: User, 
        user_agent: Optional[str] = None, 
        ip_address: Optional[str] = None
    ) -> Tuple[TrustedDevice, str]:
        """Cria e armazena um novo dispositivo confiável."""
        
        plain_token = self.generate_plain_token()
        hashed_token = self.hash_device_token(plain_token)
        
        expires_delta = timedelta(days=settings.TRUSTED_DEVICE_COOKIE_MAX_AGE_DAYS)
        expires_at = datetime.now(timezone.utc) + expires_delta

        db_obj = TrustedDevice(
            user_id=user.id,
            device_token_hash=hashed_token,
            expires_at=expires_at.replace(tzinfo=None),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj, plain_token

    async def get_trusted_device_by_token(
        self, db: AsyncSession, *, plain_token: str
    ) -> Optional[TrustedDevice]:
        """Busca um dispositivo confiável pelo seu token (não hash)."""
        
        hashed_token = self.hash_device_token(plain_token)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        stmt = select(TrustedDevice).where(
            TrustedDevice.device_token_hash == hashed_token,
            TrustedDevice.expires_at > now
        )
        
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def get_trusted_device_by_id(
        self, db: AsyncSession, *, device_id: int, user_id: int
    ) -> Optional[TrustedDevice]:
        """Busca um dispositivo pelo ID, garantindo que pertence ao usuário."""
        stmt = select(TrustedDevice).where(
            TrustedDevice.id == device_id,
            TrustedDevice.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_trusted_devices_for_user(
        self, db: AsyncSession, *, user_id: int
    ) -> List[TrustedDeviceInfo]:
        """Lista todos os dispositivos confiáveis (não expirados) de um usuário."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        stmt = select(TrustedDevice).where(
            TrustedDevice.user_id == user_id,
            TrustedDevice.expires_at > now
        ).order_by(TrustedDevice.created_at.desc())
        
        result = await db.execute(stmt)
        devices = result.scalars().all()
        
        # Mapeia para o schema Pydantic
        return [TrustedDeviceInfo.from_orm(d) for d in devices]

    async def delete_trusted_device(self, db: AsyncSession, *, db_device: TrustedDevice) -> None:
        """Deleta um dispositivo confiável específico."""
        await db.delete(db_device)
        await db.commit()
        return

    async def prune_expired_devices(self, db: AsyncSession) -> int:
        """Apaga todos os dispositivos expirados do banco de dados."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        stmt = delete(TrustedDevice).where(
            TrustedDevice.expires_at <= now
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

# Instância do CRUD
crud_trusted_device = CRUDTrustedDevice(TrustedDevice)
