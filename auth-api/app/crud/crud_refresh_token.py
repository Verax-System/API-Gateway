from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.crud.base import CRUDBase # Importação da classe base
from app.models.refresh_token import RefreshToken
# --- CORREÇÃO CRÍTICA ---
# Estas classes são necessárias para a definição da classe CRUDRefreshToken
from app.schemas.token import RefreshTokenCreate, RefreshTokenUpdate, SessionInfo
# --- FIM CORREÇÃO CRÍTICA ---
from datetime import datetime, timezone
from typing import Optional, List
import hashlib

class CRUDRefreshToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    async def create_refresh_token(
        self, db: AsyncSession, *, user: "User", token: str, expires_at: datetime,
        ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> RefreshToken:
        token_hash = self.hash_token(token)
        db_obj = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at.replace(tzinfo=None), # Store naive datetime in UTC
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_refresh_token(self, db: AsyncSession, *, token: str) -> Optional[RefreshToken]:
        token_hash = self.hash_token(token)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now
        )
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def get_refresh_token_by_id(self, db: AsyncSession, *, token_id: int, user_id: int) -> Optional[RefreshToken]:
        """Busca um token pelo ID, garantindo que pertence ao usuário."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = select(RefreshToken).where(
            RefreshToken.id == token_id,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > now
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def revoke_refresh_token(self, db: AsyncSession, *, token: str) -> bool:
        token_hash = self.hash_token(token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.execute(stmt)
        db_token = result.scalars().first()
        if db_token and not db_token.is_revoked:
            db_token.is_revoked = True
            db.add(db_token)
            await db.commit()
            return True
        return False
    
    async def revoke_refresh_token_by_id(self, db: AsyncSession, *, db_token: RefreshToken) -> None:
        """Revoga um refresh token específico (objeto do modelo)."""
        db_token.is_revoked = True
        db.add(db_token)
        await db.commit()
        return

    async def revoke_all_refresh_tokens_for_user(self, db: AsyncSession, *, user_id: int, exclude_token_hash: Optional[str] = None) -> int:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        query = (
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now
            )
        )
        if exclude_token_hash:
            query = query.where(RefreshToken.token_hash != exclude_token_hash)
        
        result = await db.execute(query)
        tokens_to_revoke = result.scalars().all()
        
        if not tokens_to_revoke:
            return 0

        for token in tokens_to_revoke:
            token.is_revoked = True
            db.add(token)
            
        await db.commit()
        return len(tokens_to_revoke)

    async def get_active_sessions_for_user(self, db: AsyncSession, *, user_id: int) -> List[SessionInfo]:
        """Retorna uma lista de sessões ativas (tokens não revogados/expirados) para o schema SessionInfo."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = (
            select(
                RefreshToken.id,
                RefreshToken.user_agent,
                RefreshToken.ip_address,
                RefreshToken.created_at,
                RefreshToken.expires_at,
                RefreshToken.token_hash # Adicionado para debug ou lógica de 'sessão atual'
            )
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now
            )
            .order_by(RefreshToken.created_at.desc())
        )
        
        result = await db.execute(stmt)
        
        # Mapeia os resultados para o Pydantic model SessionInfo
        sessions = [
            SessionInfo(
                id=row.id,
                user_agent=row.user_agent,
                ip_address=row.ip_address,
                created_at=row.created_at,
                expires_at=row.expires_at,
                # Opcional: Adicionar o hash se o schema SessionInfo o incluir
                # token_hash=row.token_hash 
            )
            for row in result.mappings()
        ]
        return sessions

# Instância do CRUD
crud_refresh_token = CRUDRefreshToken(RefreshToken)
