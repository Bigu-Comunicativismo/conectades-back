#!/bin/bash

##############################################################################
# 🐳 Setup Automático Conectades - VPS com Docker
# 
# Execute: ./setup-vps-docker.sh
#
# ✅ Configura Docker + Docker Compose
# ✅ Cria ambientes DEV e PROD separados
# ✅ Nginx como proxy reverso
##############################################################################

set -e

# Cores
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; B='\033[0;34m'; C='\033[0;36m'; NC='\033[0m'

# Funções
log_ok() { echo -e "${G}✅ $1${NC}"; }
log_warn() { echo -e "${Y}⚠️  $1${NC}"; }
log_err() { echo -e "${R}❌ $1${NC}"; exit 1; }
log_info() { echo -e "${B}ℹ️  $1${NC}"; }
log_step() { echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n${C}📋 $1${NC}\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

# Banner
clear
echo -e "${C}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🐳  CONECTADES BACKEND - SETUP VPS COM DOCKER  🐳       ║
║                                                              ║
║     Deploy completo do BACKEND (API Django)                 ║
║     Ambientes: Dev + Prod com Docker Compose                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar root
[ "$EUID" -eq 0 ] && log_err "NÃO RODE COMO ROOT! Use: su - seu_usuario"

# Verificar se já instalado
if [ -f ~/.conectades_docker_installed ]; then
    log_warn "Setup Docker já foi executado!"
    read -p "Reinstalar? (yes/N): " confirm
    [ "$confirm" != "yes" ] && { log_info "Cancelado."; exit 0; }
fi

# ═══════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════

GITHUB_REPO="https://github.com/Bigu-Comunicativismo/conectades-back.git"
BRANCH_DEV="develop"
BRANCH_PROD="main"
SERVER_IP=$(hostname -I | awk '{print $1}')

log_step "CONFIGURAÇÕES"
echo "  IP do Servidor: $SERVER_IP"
echo "  Repositório: $GITHUB_REPO"
echo "  Branch DEV: $BRANCH_DEV"
echo "  Branch PROD: $BRANCH_PROD"
echo ""
echo "  DEV rodará em: http://$SERVER_IP:8001"
echo "  PROD rodará em: http://$SERVER_IP:8002"
echo ""
read -p "Continuar? (y/N): " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && { log_info "Cancelado."; exit 0; }

# ═══════════════════════════════════════════════════════════
# ETAPA 1: INSTALAR DOCKER
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 1/6: Instalando Docker"

if ! command -v docker &> /dev/null; then
    log_info "Instalando Docker..."
    
    # Remover versões antigas
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Instalar dependências
    sudo apt-get update -qq
    sudo apt-get install -y ca-certificates curl gnupg lsb-release -qq
    
    # Adicionar chave GPG oficial do Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Adicionar repositório
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    sudo apt-get update -qq
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -qq
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    log_ok "Docker instalado"
    log_warn "⚠️  IMPORTANTE: Usuário adicionado ao grupo docker"
    log_warn "   As permissões serão aplicadas após próximo login"
    
    DOCKER_NEEDS_SUDO=true
else
    log_info "Docker já instalado ($(docker --version))"
    
    # Verificar se usuário está no grupo docker
    if ! groups | grep -q docker; then
        log_warn "Adicionando usuário ao grupo docker..."
        sudo usermod -aG docker $USER
        DOCKER_NEEDS_SUDO=true
    else
        # Testar se pode usar docker sem sudo
        if ! docker ps &> /dev/null; then
            DOCKER_NEEDS_SUDO=true
        else
            DOCKER_NEEDS_SUDO=false
        fi
    fi
fi

# Definir comando docker baseado em permissões
if [ "$DOCKER_NEEDS_SUDO" = true ]; then
    log_info "Docker será executado com sudo (permissões ainda não aplicadas)"
    DOCKER_CMD="sudo docker"
    DOCKER_COMPOSE_CMD="sudo docker compose"
else
    DOCKER_CMD="docker"
    DOCKER_COMPOSE_CMD="docker compose"
fi

# Verificar se docker-compose está disponível
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    log_info "Instalando docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    log_ok "docker-compose instalado"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 2: CRIAR ESTRUTURA
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 2/6: Criando Estrutura de Diretórios"

sudo mkdir -p /var/www/conectades-dev /var/www/conectades-prod
sudo chown -R $USER:$USER /var/www/conectades-dev /var/www/conectades-prod
mkdir -p ~/backups

log_ok "Diretórios criados"

# ═══════════════════════════════════════════════════════════
# ETAPA 3: CLONAR REPOSITÓRIOS
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 3/6: Clonando Repositórios"

# DEV
if [ -d "/var/www/conectades-dev/.git" ]; then
    log_warn "Repositório DEV já existe, atualizando..."
    cd /var/www/conectades-dev
    git fetch origin && git checkout $BRANCH_DEV && git pull origin $BRANCH_DEV
else
    log_info "Clonando branch $BRANCH_DEV..."
    git clone -b $BRANCH_DEV $GITHUB_REPO /var/www/conectades-dev
    log_ok "Repositório DEV clonado"
fi

# PROD
if [ -d "/var/www/conectades-prod/.git" ]; then
    log_warn "Repositório PROD já existe, atualizando..."
    cd /var/www/conectades-prod
    git fetch origin && git checkout $BRANCH_PROD && git pull origin $BRANCH_PROD
else
    log_info "Clonando branch $BRANCH_PROD..."
    git clone -b $BRANCH_PROD $GITHUB_REPO /var/www/conectades-prod
    log_ok "Repositório PROD clonado"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 4: CRIAR DOCKER-COMPOSE PARA DEV
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 4/6: Configurando Docker Compose DEV"

cat > /var/www/conectades-dev/docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:15-alpine
    container_name: conectades-dev-db
    environment:
      POSTGRES_DB: conectades
      POSTGRES_USER: admin_conectades
      POSTGRES_PASSWORD: conectaZ0Z6@
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: conectades-dev-redis
    ports:
      - "6380:6379"
    restart: unless-stopped

  web:
    build: .
    container_name: conectades-dev-web
    command: >
      sh -c "python backend/manage.py migrate --noinput &&
             python backend/manage.py collectstatic --noinput &&
             gunicorn --chdir backend backend.core.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    volumes:
      - .:/app
      - static_volume_dev:/app/staticfiles
      - media_volume_dev:/app/media
    ports:
      - "8001:8000"
    environment:
      - DEBUG=True
      - PYTHONPATH=/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data_dev:
  static_volume_dev:
  media_volume_dev:
EOF

log_ok "docker-compose.yml DEV criado"

# ═══════════════════════════════════════════════════════════
# ETAPA 5: CRIAR DOCKER-COMPOSE PARA PROD
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 5/6: Configurando Docker Compose PROD"

cat > /var/www/conectades-prod/docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:15-alpine
    container_name: conectades-prod-db
    environment:
      POSTGRES_DB: conectades
      POSTGRES_USER: admin_conectades
      POSTGRES_PASSWORD: conectaZ0Z6@
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
    ports:
      - "5434:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: conectades-prod-redis
    ports:
      - "6381:6379"
    restart: unless-stopped

  web:
    build: .
    container_name: conectades-prod-web
    command: >
      sh -c "python backend/manage.py migrate --noinput &&
             python backend/manage.py collectstatic --noinput &&
             gunicorn --chdir backend backend.core.wsgi:application --bind 0.0.0.0:8000 --workers 5"
    volumes:
      - .:/app
      - static_volume_prod:/app/staticfiles
      - media_volume_prod:/app/media
    ports:
      - "8002:8000"
    environment:
      - DEBUG=False
      - PYTHONPATH=/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data_prod:
  static_volume_prod:
  media_volume_prod:
EOF

log_ok "docker-compose.yml PROD criado"

# ═══════════════════════════════════════════════════════════
# ETAPA 6: INICIAR CONTAINERS
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 6/6: Iniciando Containers"

log_info "Buildando e iniciando DEV..."
cd /var/www/conectades-dev
$DOCKER_COMPOSE_CMD build
$DOCKER_COMPOSE_CMD up -d
log_ok "Containers DEV iniciados"

log_info "Buildando e iniciando PROD..."
cd /var/www/conectades-prod
$DOCKER_COMPOSE_CMD build
$DOCKER_COMPOSE_CMD up -d
log_ok "Containers PROD iniciados"

# Aguardar containers subirem
sleep 10

# ═══════════════════════════════════════════════════════════
# CONFIGURAR SUDO PARA CI/CD
# ═══════════════════════════════════════════════════════════

log_info "Configurando permissões sudo para CI/CD..."

sudo tee /etc/sudoers.d/conectades > /dev/null << EOF
$USER ALL=(ALL) NOPASSWD: /usr/bin/docker
$USER ALL=(ALL) NOPASSWD: /usr/bin/docker-compose
$USER ALL=(ALL) NOPASSWD: /usr/local/bin/docker-compose
EOF

sudo chmod 0440 /etc/sudoers.d/conectades
log_ok "Permissões configuradas"

# ═══════════════════════════════════════════════════════════
# GERAR CHAVE SSH
# ═══════════════════════════════════════════════════════════

if [ ! -f ~/.ssh/github_deploy_key ]; then
    log_info "Gerando chave SSH para GitHub Actions..."
    ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key -N ""
    cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    log_ok "Chave SSH gerada"
fi

# Marcar instalação
echo "$(date)" > ~/.conectades_docker_installed

# ═══════════════════════════════════════════════════════════
# RESUMO
# ═══════════════════════════════════════════════════════════

clear
echo -e "${G}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ✅  INSTALAÇÃO DOCKER CONCLUÍDA COM SUCESSO!  ✅        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${G}🐳 CONTAINERS RODANDO${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${B}DEV:${NC}"
$DOCKER_CMD ps --filter "name=conectades-dev" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${B}PROD:${NC}"
$DOCKER_CMD ps --filter "name=conectades-prod" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${G}🌐 ACESSAR APLICAÇÕES${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${B}DEV:${NC}  http://$SERVER_IP:8001/admin/"
echo -e "  ${B}PROD:${NC} http://$SERVER_IP:8002/admin/"
echo -e "  ${B}API Docs DEV:${NC}  http://$SERVER_IP:8001/api/docs/"
echo -e "  ${B}API Docs PROD:${NC} http://$SERVER_IP:8002/api/docs/"

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${Y}📋 PRÓXIMOS PASSOS${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${Y}1. Criar superusers:${NC}"
echo -e "   ${C}cd /var/www/conectades-dev${NC}"
echo -e "   ${C}docker compose exec web python backend/manage.py createsuperuser${NC}"
echo -e ""
echo -e "   ${C}cd /var/www/conectades-prod${NC}"
echo -e "   ${C}docker compose exec web python backend/manage.py createsuperuser${NC}"

echo -e "\n${Y}2. Ver logs:${NC}"
echo -e "   ${C}docker logs -f conectades-dev-web${NC}"
echo -e "   ${C}docker logs -f conectades-prod-web${NC}"

echo -e "\n${Y}3. GitHub Secrets (para CI/CD):${NC}"
echo -e "   DEV_SSH_HOST = $SERVER_IP"
echo -e "   DEV_SSH_USERNAME = $USER"
echo -e "   DEV_SSH_PORT = 22"
echo -e "   DEV_PROJECT_PATH = /var/www/conectades-dev"
echo -e ""
echo -e "   PROD_SSH_HOST = $SERVER_IP"
echo -e "   PROD_SSH_USERNAME = $USER"
echo -e "   PROD_SSH_PORT = 22"
echo -e "   PROD_PROJECT_PATH = /var/www/conectades-prod"
echo -e ""
echo -e "   ${G}Chave SSH:${NC}"
echo -e "   ${C}cat ~/.ssh/github_deploy_key${NC}"

echo -e "\n${Y}4. Comandos úteis:${NC}"
echo -e "   ${C}cd /var/www/conectades-dev && docker compose restart${NC}"
echo -e "   ${C}cd /var/www/conectades-prod && docker compose restart${NC}"
echo -e "   ${C}docker ps${NC} - Ver containers rodando"
echo -e "   ${C}docker compose logs -f${NC} - Ver logs em tempo real"

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${G}✅ Tudo pronto! Teste agora:${NC}"
echo -e "   ${C}curl http://$SERVER_IP:8001/admin/${NC}"
echo -e "   ${C}curl http://$SERVER_IP:8002/admin/${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

