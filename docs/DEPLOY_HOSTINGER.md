# 🚀 Guia de Deploy na Hostinger

## 📋 Índice
1. [Configuração do VPS Hostinger](#configuração-do-vps)
2. [Configuração do GitHub Actions](#configuração-do-github-actions)
3. [Secrets do GitHub](#secrets-do-github)
4. [Estrutura de Branches](#estrutura-de-branches)
5. [Fluxo de Deploy](#fluxo-de-deploy)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ Configuração do VPS Hostinger

### 1. Acesso SSH ao VPS

```bash
# Conectar ao VPS
ssh usuario@seu-vps.hostinger.com -p 22

# Ou se usar chave SSH
ssh -i ~/.ssh/hostinger_key usuario@seu-vps.hostinger.com
```

### 2. Instalar Dependências no Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Instalar Redis
sudo apt install redis-server -y

# Instalar Nginx
sudo apt install nginx -y

# Instalar ferramentas adicionais
sudo apt install git build-essential libpq-dev -y
```

### 3. Configurar PostgreSQL

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco de dados e usuário
CREATE DATABASE conectades;
CREATE USER admin_conectades WITH PASSWORD 'SUA_SENHA_FORTE_AQUI';
ALTER ROLE admin_conectades SET client_encoding TO 'utf8';
ALTER ROLE admin_conectades SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin_conectades SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE conectades TO admin_conectades;
\q
```

### 4. Clonar Projeto

```bash
# Criar diretório
mkdir -p /var/www/conectades
cd /var/www/conectades

# Clonar repositório
git clone https://github.com/SEU_USUARIO/conectades.git .

# Criar ambiente virtual
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano backend/.env
```

**Conteúdo do .env:**
```bash
# Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,seu-ip-vps

# Database
DB_NAME=conectades
DB_USER=admin_conectades
DB_PASSWORD=sua-senha-postgresql
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (configurar com seu provedor)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# Segurança
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Mídia
MEDIA_ROOT=/var/www/conectades/media
STATIC_ROOT=/var/www/conectades/staticfiles
```

### 6. Configurar Gunicorn

```bash
# Criar arquivo de configuração
nano /var/www/conectades/gunicorn_config.py
```

**gunicorn_config.py:**
```python
import multiprocessing

# Servidor
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/www/conectades/logs/gunicorn_access.log"
errorlog = "/var/www/conectades/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "conectades"

# Server mechanics
daemon = False
pidfile = "/var/www/conectades/gunicorn.pid"
user = "www-data"
group = "www-data"

# SSL (se usar)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

### 7. Criar Serviço Systemd

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/conectades.service
```

**conectades.service:**
```ini
[Unit]
Description=Conectades Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/conectades/backend
Environment="PATH=/var/www/conectades/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=backend.core.settings"
ExecStart=/var/www/conectades/venv/bin/gunicorn \
    --config /var/www/conectades/gunicorn_config.py \
    backend.core.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**Ativar serviço:**
```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable conectades

# Iniciar serviço
sudo systemctl start conectades

# Verificar status
sudo systemctl status conectades
```

### 8. Configurar Nginx

```bash
# Criar configuração do site
sudo nano /etc/nginx/sites-available/conectades
```

**conectades (nginx config):**
```nginx
# Upstream para Gunicorn
upstream conectades_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # SSL (Certbot irá configurar automaticamente)
    # ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    client_max_body_size 20M;
    
    # Logs
    access_log /var/log/nginx/conectades_access.log;
    error_log /var/log/nginx/conectades_error.log;
    
    # Static files
    location /static/ {
        alias /var/www/conectades/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/conectades/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # API e Admin
    location / {
        proxy_pass http://conectades_backend;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    # Health check
    location /health/ {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
```

**Ativar site:**
```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/conectades /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 9. Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática já está configurada
```

### 10. Criar Diretórios Necessários

```bash
# Criar diretórios
mkdir -p /var/www/conectades/logs
mkdir -p /var/www/conectades/media
mkdir -p /var/www/conectades/staticfiles
mkdir -p ~/backups

# Ajustar permissões
sudo chown -R www-data:www-data /var/www/conectades
sudo chmod -R 755 /var/www/conectades
```

### 11. Executar Setup Inicial

```bash
cd /var/www/conectades
source venv/bin/activate
cd backend

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar static files
python manage.py collectstatic --noinput

# Carregar dados iniciais
python manage.py carregar_localizacoes_rmr
python manage.py criar_tipos_padrao
```

---

## 🔐 Configuração do GitHub Actions

### Secrets do GitHub

Vá em **Settings → Secrets and variables → Actions → New repository secret**

#### **Secrets para Development:**

```
DEV_SSH_HOST=ip-do-servidor-dev
DEV_SSH_USERNAME=usuario-ssh
DEV_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
DEV_SSH_PORT=22
DEV_PROJECT_PATH=/var/www/conectades-dev
```

#### **Secrets para Production:**

```
PROD_SSH_HOST=seu-vps.hostinger.com
PROD_SSH_USERNAME=usuario-ssh
PROD_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
PROD_SSH_PORT=22
PROD_PROJECT_PATH=/var/www/conectades
PROD_DB_NAME=conectades
PROD_BRANCH=main
PROD_HEALTH_CHECK_URL=https://api.conectades.com/health/
```

### Gerar Chave SSH para Deploy

```bash
# No seu computador local
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/conectades_deploy

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/conectades_deploy.pub usuario@seu-vps.hostinger.com

# Copiar chave PRIVADA para GitHub Secrets
cat ~/.ssh/conectades_deploy
# Cole o conteúdo em PROD_SSH_PRIVATE_KEY
```

---

## 🌳 Estrutura de Branches

```
main (prod)      ←──── Produção (deploy automático)
  ↑
  │ PR (requer aprovação)
  │
develop          ←──── Desenvolvimento (deploy automático)
  ↑
  │ PR
  │
feature/*        ←──── Features individuais
```

### Workflow de Desenvolvimento

```bash
# 1. Criar feature branch
git checkout develop
git pull origin develop
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver e commitar
git add .
git commit -m "feat: adiciona nova funcionalidade"

# 3. Push e criar PR para develop
git push origin feature/nova-funcionalidade
# Criar PR no GitHub: feature/nova-funcionalidade → develop

# 4. Após merge: deploy automático para DEV

# 5. Testar em desenvolvimento

# 6. Criar PR para produção
# Criar PR no GitHub: develop → main

# 7. Após aprovação e merge: deploy automático para PROD
```

---

## 🔄 Fluxo de Deploy

### Development (develop branch)

```mermaid
graph LR
    A[Push to develop] --> B[Run Tests]
    B --> C{Tests Pass?}
    C -->|Yes| D[Deploy to DEV]
    C -->|No| E[❌ Fail]
    D --> F[✅ Success]
```

**Triggers:**
- Push direto para `develop`
- Merge de PR para `develop`

**Actions:**
1. ✅ Executa testes
2. ✅ Verifica migrações
3. ✅ Deploy via SSH para servidor DEV
4. ✅ Reinicia aplicação

### Production (main/prod branch)

```mermaid
graph LR
    A[PR: develop → main] --> B[Run Tests]
    B --> C[Security Checks]
    C --> D{Approved?}
    D -->|Yes| E[Merge]
    E --> F[Backup DB]
    F --> G[Deploy to PROD]
    G --> H[Health Check]
    H --> I{Healthy?}
    I -->|Yes| J[✅ Success]
    I -->|No| K[🔙 Rollback]
```

**Triggers:**
- Merge de PR para `main` ou `prod`

**Actions:**
1. ✅ Executa testes completos
2. ✅ Verifica segurança (safety, bandit)
3. ✅ Backup automático do banco
4. ✅ Deploy via SSH para servidor PROD
5. ✅ Health check pós-deploy
6. ✅ Rollback automático se falhar

---

## 🔧 Configurações Específicas da Hostinger

### Opção 1: Usando Passenger (Mais Comum na Hostinger)

```bash
# passenger_wsgi.py (na raiz do projeto)
import sys
import os

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.core.settings'

# Importar aplicação
from backend.core.wsgi import application
```

**Reload com Passenger:**
```bash
# No script de deploy, usar:
touch /var/www/conectades/tmp/restart.txt
```

### Opção 2: Usando Gunicorn + Systemd (Recomendado)

Já configurado nas seções anteriores.

**Reload:**
```bash
sudo systemctl restart conectades
```

### Opção 3: Usando PM2

```bash
# Instalar PM2
npm install -g pm2

# Criar ecosystem file
nano ecosystem.config.js
```

**ecosystem.config.js:**
```javascript
module.exports = {
  apps: [{
    name: 'conectades',
    cwd: '/var/www/conectades/backend',
    script: '/var/www/conectades/venv/bin/gunicorn',
    args: 'backend.core.wsgi:application --bind 127.0.0.1:8000 --workers 4',
    interpreter: 'none',
    env: {
      DJANGO_SETTINGS_MODULE: 'backend.core.settings',
      PYTHONPATH: '/var/www/conectades'
    }
  }]
}
```

**Comandos:**
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

**Reload:**
```bash
pm2 restart conectades
```

---

## 🔑 Checklist de Configuração

### No VPS Hostinger:

- [ ] Python 3.12 instalado
- [ ] PostgreSQL configurado e rodando
- [ ] Redis instalado e rodando
- [ ] Nginx configurado
- [ ] Projeto clonado em `/var/www/conectades`
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo `.env` configurado
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Arquivos estáticos coletados
- [ ] Serviço (Gunicorn/Passenger/PM2) rodando
- [ ] SSL configurado (Let's Encrypt)
- [ ] Permissões corretas nos diretórios
- [ ] Backup automático configurado

### No GitHub:

- [ ] Branch `develop` criada
- [ ] Branch `main` ou `prod` criada
- [ ] Secrets configurados:
  - [ ] `PROD_SSH_HOST`
  - [ ] `PROD_SSH_USERNAME`
  - [ ] `PROD_SSH_PRIVATE_KEY`
  - [ ] `PROD_SSH_PORT`
  - [ ] `PROD_PROJECT_PATH`
  - [ ] `PROD_DB_NAME`
  - [ ] `PROD_BRANCH`
  - [ ] `PROD_HEALTH_CHECK_URL`
  - [ ] (Mesmos para DEV se tiver servidor separado)
- [ ] Workflows testados

---

## 🧪 Testar Deploy

### 1. Testar Conexão SSH

```bash
# Do GitHub Actions (simular)
ssh -i chave_privada usuario@host "echo 'Conexão OK'"
```

### 2. Testar Workflow Localmente

```bash
# Instalar act (para testar GitHub Actions localmente)
# https://github.com/nektos/act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Testar workflow
act -j test
```

### 3. Deploy Manual (primeira vez)

```bash
# No VPS, fazer um deploy manual primeiro
cd /var/www/conectades
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart conectades
```

---

## 📊 Monitoramento

### Logs para Verificar

```bash
# Logs do Gunicorn
tail -f /var/www/conectades/logs/gunicorn_error.log

# Logs do Systemd
sudo journalctl -u conectades -f

# Logs do Nginx
sudo tail -f /var/log/nginx/conectades_error.log

# Logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Health Checks

```bash
# Verificar se aplicação está respondendo
curl https://seu-dominio.com/health/

# Verificar admin
curl https://seu-dominio.com/admin/

# Verificar API
curl https://seu-dominio.com/api/docs/
```

---

## 🆘 Troubleshooting

### Deploy falhou?

1. **Verificar logs do GitHub Actions**
2. **Conectar via SSH e verificar:**
   ```bash
   cd /var/www/conectades
   git status
   sudo systemctl status conectades
   tail -f logs/gunicorn_error.log
   ```

### Aplicação não inicia?

```bash
# Verificar serviço
sudo systemctl status conectades

# Testar Gunicorn manualmente
cd /var/www/conectades/backend
source ../venv/bin/activate
gunicorn backend.core.wsgi:application --bind 127.0.0.1:8000

# Verificar variáveis de ambiente
env | grep DJANGO
```

### Erros 502 Bad Gateway?

```bash
# Gunicorn não está rodando
sudo systemctl start conectades

# Ou porta errada no Nginx
sudo nano /etc/nginx/sites-available/conectades
# Verificar: proxy_pass http://127.0.0.1:8000;
```

### Arquivos estáticos não carregam?

```bash
# Coletar novamente
python manage.py collectstatic --noinput

# Verificar permissões
sudo chown -R www-data:www-data /var/www/conectades/staticfiles
sudo chmod -R 755 /var/www/conectades/staticfiles
```

---

## 📝 Comandos Úteis

```bash
# Reiniciar todos os serviços
sudo systemctl restart conectades nginx postgresql redis

# Ver logs em tempo real
sudo journalctl -u conectades -f

# Fazer backup manual
pg_dump conectades > ~/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
psql conectades < ~/backups/backup_20251020_120000.sql

# Limpar logs antigos
sudo journalctl --vacuum-time=7d

# Monitorar recursos
htop
df -h
free -h
```

---

## 🎯 Próximos Passos

Após configurar tudo:

1. ✅ Criar branches `develop` e `main`
2. ✅ Configurar secrets no GitHub
3. ✅ Configurar VPS Hostinger
4. ✅ Fazer primeiro deploy manual
5. ✅ Testar workflow de deploy automático
6. ✅ Configurar monitoramento
7. ✅ Configurar backups automáticos

**Quando estiver pronto, me passe as configurações da Hostinger que eu ajusto os workflows!** 🚀

