# 1. Imagem base otimizada
FROM python:3.12-slim

# 2. Variáveis de ambiente para performance e limpeza
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 3. Dependências de sistema (apenas o essencial)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. TRUQUE DE MESTRE: Instalar dependências ANTES de copiar o código
# Isso acelera o build em 90% nas próximas vezes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar o restante do código
COPY . .

# 6. Criar pastas necessárias e ajustar permissões para escrita de logs/resultados
RUN mkdir -p monitoring/results && chmod -R 777 monitoring/results

# 7. Segurança: Evitar rodar como root
RUN useradd -m myuser
USER myuser

# Exposição da porta do Streamlit
EXPOSE 8501

# Healthcheck: Permite que o Kubernetes saiba se o app está vivo
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de inicialização
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]