# Verax System - Plataforma de Gerenciamento (API Gateway)

Este projeto implementa uma arquitetura de microsserviços completa, orquestrada com Docker Compose e gerenciada por um API Gateway (Nginx). A plataforma é dividida em três domínios principais: Autenticação (auth), Vendas (sales) e Gerenciamento de Frotas (fleet).

## 🧠 Arquitetura

O sistema é projetado para ser modular e escalável. O Nginx atua como um reverse proxy e API Gateway, direcionando o tráfego da porta 8000 para os serviços de backend (APIs) e frontend (UIs) apropriados.

- **Gateway**: Nginx (Ouvindo na porta 8000)
- **Banco de Dados**: PostgreSQL (Uma única instância servindo múltiplos bancos de dados)
- **Serviços de Backend (APIs)**:
  - `auth-api` (Python / FastAPI)
  - `sales-api` (Python / FastAPI)
  - `fleet-api` (Python / FastAPI)
- **Serviços de Frontend (UIs)**:
  - `auth-ui` (Vue.js / Quasar)
  - `sales-ui` (React.js)
  - `fleet-ui` (Vue.js / Quasar)

### Fluxo de Requisições (via Nginx)

| Rota Externa (`http://localhost:8000/...`) | Serviço Interno | Porta Interna |
| ------------------------------------------ | --------------- | ------------- |
| `/api/auth/*`                              | `auth-api`      | `8001`        |
| `/api/sales/*`                             | `sales-api`     | `8002`        |
| `/api/fleet/*`                             | `fleet-api`     | `8003`        |
| `/auth/*`                                  | `auth-ui`       | `9001`        |
| `/sales/*`                                 | `sales-ui`      | `9002`        |
| `/` (e outras rotas)                       | `fleet-ui`      | `9003`        |

## 🛠️ Tecnologias Utilizadas

| Categoria       | Tecnologia                  | Propósito                                                 |
| --------------- | --------------------------- | --------------------------------------------------------- |
| Infraestrutura  | Docker, Docker Compose      | Orquestração e conteinerização dos serviços.              |
| Gateway         | Nginx                       | Reverse Proxy e API Gateway.                              |
| Banco de Dados  | PostgreSQL                  | Persistência de dados para todas as APIs.                 |
| Backend         | Python 3.10, FastAPI        | APIs assíncronas de alta performance.                     |
| Backend (ORM)   | SQLAlchemy, Alembic         | Mapeamento Objeto-Relacional e gerenciamento de migrações. |
| Backend (Driver)| asyncpg                     | Driver assíncrono para PostgreSQL.                        |
| Frontend (Frota)| Vue.js 3, Quasar 2, Vite    | UI principal de gerenciamento de frotas.                  |
| Frontend (Auth) | Vue.js 3, Quasar 2, Vite    | UI de login, registro e gerenciamento de conta.           |
| Frontend (Vendas)| React.js 18, Vite           | UI do Ponto de Venda (PDV).                               |

## 🚀 Como Rodar o Projeto

Siga estes passos para configurar e executar toda a pilha de microsserviços localmente.

### 1. Pré-requisitos

- Docker instalado e em execução.
- Docker Compose (geralmente incluído no Docker Desktop).

### 2. Configuração do Banco de Dados

O `docker-compose.yml` está configurado para usar um arquivo `init.sql` para criar os bancos de dados necessários na primeira vez que o contêiner `db` é iniciado.

Crie um arquivo chamado `init.sql` na raiz do projeto (ao lado do `docker-compose.yml`) com o seguinte conteúdo.

**Arquivo: `init.sql`**

(Nota: O banco de dados `frota_agil` é criado automaticamente pela variável `POSTGRES_DB` no seu `docker-compose.yml`).

### 3. Configuração das Variáveis de Ambiente (.env)

Cada serviço (API e UI) requer seu próprio arquivo `.env`. Crie os arquivos a seguir dentro de suas respectivas pastas.

- **Arquivo: `auth-api/.env`**
- **Arquivo: `sales-api/.env`**
- **Arquivo: `fleet-api/.env`**
- **Arquivo: `auth-ui/.env`**
- **Arquivo: `fleet-ui/.env`**
- **Arquivo: `sales-ui/.env`**

**IMPORTANTE**: Lembre-se de substituir valores sensíveis como `SUA_CHAVE_SECRETA_FORTE_AQUI`, senhas de banco de dados e chaves de API por valores de produção seguros antes de fazer o deploy.

### 4. Build e Execução

Com todos os arquivos `.env` e o `init.sql` no lugar, abra um terminal na raiz do projeto (onde está o `docker-compose.yml`) e execute o seguinte comando:

```bash
docker-compose up --build -d
```

- `--build`: Força a reconstrução das imagens (importante na primeira vez ou após mudanças no `Dockerfile` ou `requirements.txt`).
- `-d`: Executa os contêineres em modo "detached" (em segundo plano).

As APIs de backend executarão automaticamente as migrações do Alembic (`alembic upgrade head`) antes de iniciar.

### 5. Acessando a Aplicação

Após os contêineres estarem em execução, você pode acessar as aplicações:

- **Aplicação Principal (Frota)**: `http://localhost:8000/`
- **UI de Autenticação**: `http://localhost:8000/auth/`
- **UI de Vendas (PDV)**: `http://localhost:8000/sales/`

### 6. Parando a Aplicação

Para parar todos os serviços, execute no mesmo diretório:

```bash
docker-compose down
```
