import secrets
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.crud.base import CRUDBase # <-- Necessário para definir a classe
from app.models.mfa_recovery_code import MFARecoveryCode
# --- CORREÇÃO CRÍTICA ---
# Importar os Schemas de Criação e Atualização
from app.schemas.mfa_recovery_code import MFARecoveryCodeCreate, MFARecoveryCodeUpdate 
# --- FIM CORREÇÃO CRÍTICA ---
from app.models.user import User
import hashlib
from datetime import datetime, timezone

# --- CORREÇÃO CRÍTICA: A classe CRUD está definida e herda corretamente ---
class CRUDMFARecoveryCode(CRUDBase[MFARecoveryCode, MFARecoveryCodeCreate, MFARecoveryCodeUpdate]):
# --- FIM CORREÇÃO CRÍTICA ---

    def hash_code(self, code: str) -> str:
        """Gera um hash SHA-256 para o código de recuperação."""
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    # ... (restante das funções do CRUD) ...

    def generate_plain_code(self) -> str:
        """Gera um código de recuperação simples (ex: 8-10 caracteres)."""
        # Ex: "abcd-1234"
        return f"{secrets.token_hex(4)}-{secrets.token_hex(4)}"

    async def create_recovery_codes(self, db: AsyncSession, *, user: User, count: int = 8) -> List[str]:
        """Gera e salva novos códigos de recuperação, apagando os antigos."""
        
        # 1. Apagar todos os códigos antigos
        await self.delete_all_codes_for_user(db=db, user_id=user.id)
        
        # 2. Gerar novos códigos
        plain_codes = [self.generate_plain_code() for _ in range(count)]
        db_codes = [
            MFARecoveryCode(
                user_id=user.id,
                hashed_code=self.hash_code(code),
                is_used=False
            ) for code in plain_codes
        ]
        
        db.add_all(db_codes)
        await db.commit()
        
        return plain_codes

    async def get_valid_recovery_code(self, db: AsyncSession, *, user: User, plain_code: str) -> MFARecoveryCode | None:
        """Verifica se um código de recuperação é válido e não foi usado."""
        hashed_code = self.hash_code(plain_code)
        
        stmt = select(MFARecoveryCode).where(
            MFARecoveryCode.user_id == user.id,
            MFARecoveryCode.hashed_code == hashed_code,
            MFARecoveryCode.is_used == False
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def mark_code_as_used(self, db: AsyncSession, *, db_code: MFARecoveryCode) -> MFARecoveryCode:
        """Marca um código de recuperação como utilizado."""
        db_code.is_used = True
        db_code.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add(db_code)
        await db.commit()
        await db.refresh(db_code)
        return db_code

    async def delete_all_codes_for_user(self, db: AsyncSession, *, user_id: int) -> int:
        """Apaga todos os códigos de recuperação de um usuário."""
        stmt = delete(MFARecoveryCode).where(MFARecoveryCode.user_id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

# Renomeado para a instância ser igual ao que é importado por outros ficheiros (crud_mfa_recovery_code)
crud_mfa_recovery_code = CRUDMFARecoveryCode(MFARecoveryCode)
