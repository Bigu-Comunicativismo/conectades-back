FROM python:3.11-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Torna o script executável
RUN chmod +x ./backend/wait-for-db.sh

# Porta
EXPOSE 8000

# Comando de inicialização
CMD ["./backend/wait-for-db.sh", "db", "python", "./backend/manage.py", "runserver", "0.0.0.0:8000"]
