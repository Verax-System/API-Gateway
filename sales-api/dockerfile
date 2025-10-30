# Usa a imagem base oficial do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Atualiza o pip para a versão mais recente
RUN pip install --no-cache-dir -U pip

# Copia APENAS o requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código da aplicação
COPY . .

# O comando para iniciar a aplicação (uvicorn) já está no seu docker-compose.yml