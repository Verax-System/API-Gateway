import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

# Define o diretório base de uploads, criando-o se não existir
# O nome 'static/uploads' é baseado em convenções de projetos FastAPI/Starlette para arquivos estáticos.
UPLOAD_DIR = Path("static/uploads")

if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Requer que o diretório principal da API (fleet-api) tenha permissão de escrita.

def save_upload_file(upload_file: UploadFile, destination: str = "general") -> str:
    """
    Salva um UploadFile em um subdiretório específico com um nome de arquivo exclusivo.
    
    Args:
        upload_file: O objeto UploadFile do FastAPI.
        destination: Subdiretório dentro de UPLOAD_DIR (ex: 'avatars', 'documents').
        
    Returns:
        O caminho do arquivo salvo relativo (ex: 'static/uploads/avatars/uuid.ext').
    """
    
    # 1. Cria o subdiretório (ex: static/uploads/avatars)
    sub_dir = UPLOAD_DIR / destination
    if not sub_dir.exists():
        sub_dir.mkdir(parents=True, exist_ok=True)

    # 2. Gera um nome de arquivo exclusivo com a extensão original
    original_filename = upload_file.filename
    if original_filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de arquivo ausente.",
        )
        
    file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'bin'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = sub_dir / unique_filename

    # 3. Salva o arquivo em disco de forma síncrona
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao salvar arquivo: {e}",
        )
    finally:
        upload_file.file.close()

    # 4. Retorna o caminho relativo (path estático)
    return f"{UPLOAD_DIR.name}/{destination}/{unique_filename}"