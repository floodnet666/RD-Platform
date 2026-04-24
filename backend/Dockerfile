FROM python:3.13-slim

# Instalação de dependências de sistema (Git, Curl, build-essential para ifcopenshell)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalação do uv (Standalone)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copia apenas os arquivos de dependência primeiro para cache de camada
COPY pyproject.toml uv.lock ./

# Instalação das dependências no modo --frozen (usando o lockfile)
RUN uv sync --frozen --no-cache

# O código será montado via Volume no Docker Compose para permitir Hot Reload
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8000

# Rodando com uvicorn --reload para Hot Reload do Backend
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
