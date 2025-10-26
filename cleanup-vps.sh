#!/bin/bash

##############################################################################
# 🧹 Script de Limpeza Completa - Conectades VPS
# 
# Execute: ./cleanup-vps.sh
#
# ⚠️  ATENÇÃO: Este script remove TUDO relacionado ao Conectades!
# - Para containers Docker
# - Remove imagens e volumes
# - Remove diretórios /var/www/conectades-*
# - Remove bancos PostgreSQL
# - Remove configurações Nginx
# - Remove serviços Gunicorn
# - Remove arquivos de configuração
##############################################################################

set -e

# Cores
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; B='\033[0;34m'; C='\033[0;36m'; NC='\033[0m'

# Funções
log_ok() { echo -e "${G}✅ $1${NC}"; }
log_warn() { echo -e "${Y}⚠️  $1${NC}"; }
log_err() { echo -e "${R}❌ $1${NC}"; }
log_info() { echo -e "${B}ℹ️  $1${NC}"; }
log_step() { echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n${C}🧹 $1${NC}\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

# Banner
clear
echo -e "${R}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🧹  CONECTADES - LIMPEZA COMPLETA VPS  🧹               ║
║                                                              ║
║     ⚠️  ESTE SCRIPT VAI REMOVER TUDO!  ⚠️                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${R}⚠️  ATENÇÃO - LEIA ANTES DE CONTINUAR!${NC}"
echo -e "${R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Este script irá:"
echo ""
echo "  ${R}❌ Parar e remover todos os containers Docker${NC}"
echo "  ${R}❌ Remover todas as imagens Docker do Conectades${NC}"
echo "  ${R}❌ Remover todos os volumes Docker (DADOS PERDIDOS!)${NC}"
echo "  ${R}❌ Remover diretórios /var/www/conectades-*${NC}"
echo "  ${R}❌ Remover bancos PostgreSQL (conectades_dev e conectades_prod)${NC}"
echo "  ${R}❌ Remover serviços Gunicorn (systemd)${NC}"
echo "  ${R}❌ Remover configurações Nginx${NC}"
echo "  ${R}❌ Remover ambientes virtuais Python${NC}"
echo "  ${R}❌ Remover arquivos de credenciais${NC}"
echo ""
echo -e "${Y}💾 Backups NÃO serão removidos (pasta ~/backups)${NC}"
echo ""
echo -e "${R}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Tem CERTEZA que deseja continuar? Digite 'DELETAR TUDO' para confirmar: " confirm

if [ "$confirm" != "DELETAR TUDO" ]; then
    log_info "Cancelado. Nada foi removido."
    exit 0
fi

echo ""
read -p "Última chance! Digite 'SIM' para confirmar novamente: " confirm2

if [ "$confirm2" != "SIM" ]; then
    log_info "Cancelado. Nada foi removido."
    exit 0
fi

log_warn "Iniciando limpeza em 5 segundos... Ctrl+C para cancelar!"
sleep 5

# ═══════════════════════════════════════════════════════════
# ETAPA 1: PARAR E REMOVER CONTAINERS DOCKER
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 1/8: Removendo Containers Docker"

if command -v docker &> /dev/null; then
    # Parar containers
    log_info "Parando containers do Conectades..."
    docker stop $(docker ps -a -q --filter "name=conectades") 2>/dev/null || log_info "Nenhum container rodando"
    
    # Remover containers
    log_info "Removendo containers..."
    docker rm $(docker ps -a -q --filter "name=conectades") 2>/dev/null || log_info "Nenhum container para remover"
    
    # Remover imagens
    log_info "Removendo imagens Docker..."
    docker rmi $(docker images -q --filter "reference=conectades*") 2>/dev/null || log_info "Nenhuma imagem para remover"
    docker rmi $(docker images -q --filter "reference=*conectades*") 2>/dev/null || log_info "Nenhuma imagem relacionada"
    
    # Remover volumes
    log_info "Removendo volumes Docker..."
    docker volume rm $(docker volume ls -q --filter "name=conectades") 2>/dev/null || log_info "Nenhum volume para remover"
    
    log_ok "Containers, imagens e volumes Docker removidos"
else
    log_info "Docker não instalado, pulando..."
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 2: PARAR SERVIÇOS SYSTEMD
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 2/8: Parando Serviços Systemd"

for service in gunicorn-dev gunicorn-prod; do
    if systemctl list-unit-files | grep -q "$service.service"; then
        log_info "Parando e desabilitando $service..."
        sudo systemctl stop $service 2>/dev/null || true
        sudo systemctl disable $service 2>/dev/null || true
        sudo rm -f /etc/systemd/system/$service.service
        log_ok "Serviço $service removido"
    fi
done

sudo systemctl daemon-reload
log_ok "Serviços systemd removidos"

# ═══════════════════════════════════════════════════════════
# ETAPA 3: REMOVER CONFIGURAÇÕES NGINX
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 3/8: Removendo Configurações Nginx"

if [ -f /etc/nginx/sites-enabled/conectades-dev ]; then
    log_info "Removendo configuração Nginx DEV..."
    sudo rm -f /etc/nginx/sites-enabled/conectades-dev
    sudo rm -f /etc/nginx/sites-available/conectades-dev
    log_ok "Configuração Nginx DEV removida"
fi

if [ -f /etc/nginx/sites-enabled/conectades-prod ]; then
    log_info "Removendo configuração Nginx PROD..."
    sudo rm -f /etc/nginx/sites-enabled/conectades-prod
    sudo rm -f /etc/nginx/sites-available/conectades-prod
    log_ok "Configuração Nginx PROD removida"
fi

if command -v nginx &> /dev/null; then
    sudo nginx -t 2>/dev/null && sudo systemctl reload nginx
    log_ok "Nginx recarregado"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 4: REMOVER DIRETÓRIOS DE PROJETO
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 4/8: Removendo Diretórios de Projeto"

if [ -d /var/www/conectades-dev ]; then
    log_info "Removendo /var/www/conectades-dev..."
    
    # Parar docker-compose se existir
    if [ -f /var/www/conectades-dev/docker-compose.yml ]; then
        cd /var/www/conectades-dev
        docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true
    fi
    
    sudo rm -rf /var/www/conectades-dev
    log_ok "Diretório DEV removido"
fi

if [ -d /var/www/conectades-prod ]; then
    log_info "Removendo /var/www/conectades-prod..."
    
    # Parar docker-compose se existir
    if [ -f /var/www/conectades-prod/docker-compose.yml ]; then
        cd /var/www/conectades-prod
        docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true
    fi
    
    sudo rm -rf /var/www/conectades-prod
    log_ok "Diretório PROD removido"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 5: REMOVER BANCOS POSTGRESQL
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 5/8: Removendo Bancos PostgreSQL"

if command -v psql &> /dev/null; then
    log_warn "Removendo bancos de dados..."
    
    # Criar backup antes de remover
    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p ~/backups
    
    # Backup DEV
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw conectades_dev; then
        log_info "Fazendo backup de conectades_dev..."
        sudo -u postgres pg_dump conectades_dev > ~/backups/conectades_dev_${timestamp}.sql 2>/dev/null || true
        
        log_info "Removendo banco conectades_dev..."
        sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS conectades_dev;
DROP USER IF EXISTS admin_conectades_dev;
EOF
        log_ok "Banco conectades_dev removido (backup em ~/backups/)"
    fi
    
    # Backup PROD
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw conectades_prod; then
        log_info "Fazendo backup de conectades_prod..."
        sudo -u postgres pg_dump conectades_prod > ~/backups/conectades_prod_${timestamp}.sql 2>/dev/null || true
        
        log_info "Removendo banco conectades_prod..."
        sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS conectades_prod;
DROP USER IF EXISTS admin_conectades_prod;
EOF
        log_ok "Banco conectades_prod removido (backup em ~/backups/)"
    fi
else
    log_info "PostgreSQL não instalado, pulando..."
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 6: REMOVER CONFIGURAÇÕES SUDO
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 6/8: Removendo Configurações Sudo"

if [ -f /etc/sudoers.d/conectades ]; then
    log_info "Removendo /etc/sudoers.d/conectades..."
    sudo rm -f /etc/sudoers.d/conectades
    log_ok "Configurações sudo removidas"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 7: REMOVER CHAVES SSH
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 7/8: Removendo Chaves SSH"

read -p "Remover chave SSH do GitHub Actions? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f ~/.ssh/github_deploy_key ]; then
        log_info "Fazendo backup da chave SSH..."
        mkdir -p ~/backups
        cp ~/.ssh/github_deploy_key ~/backups/github_deploy_key_backup_$(date +%Y%m%d_%H%M%S)
        cp ~/.ssh/github_deploy_key.pub ~/backups/github_deploy_key_pub_backup_$(date +%Y%m%d_%H%M%S)
        
        log_info "Removendo chave SSH..."
        rm -f ~/.ssh/github_deploy_key ~/.ssh/github_deploy_key.pub
        
        # Remover da authorized_keys
        if [ -f ~/.ssh/authorized_keys ]; then
            grep -v "github-actions" ~/.ssh/authorized_keys > ~/.ssh/authorized_keys.tmp 2>/dev/null || true
            mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys 2>/dev/null || true
        fi
        
        log_ok "Chave SSH removida (backup em ~/backups/)"
    fi
else
    log_info "Chave SSH mantida"
fi

# ═══════════════════════════════════════════════════════════
# ETAPA 8: REMOVER ARQUIVOS DE CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════

log_step "ETAPA 8/8: Removendo Arquivos de Configuração"

log_info "Removendo marcadores de instalação..."
rm -f ~/.conectades_installed
rm -f ~/.conectades_docker_installed
rm -f ~/.conectades_setup_done

read -p "Remover arquivo de credenciais ~/.conectades_credentials? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f ~/.conectades_credentials ]; then
        log_info "Fazendo backup das credenciais..."
        mkdir -p ~/backups
        cp ~/.conectades_credentials ~/backups/conectades_credentials_backup_$(date +%Y%m%d_%H%M%S)
        rm -f ~/.conectades_credentials
        log_ok "Credenciais removidas (backup em ~/backups/)"
    fi
else
    log_info "Credenciais mantidas"
fi

rm -rf ~/.conectades_backup 2>/dev/null || true

log_ok "Arquivos de configuração removidos"

# ═══════════════════════════════════════════════════════════
# RESUMO
# ═══════════════════════════════════════════════════════════

clear
echo -e "${G}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ✅  LIMPEZA CONCLUÍDA COM SUCESSO!  ✅             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${G}📊 RESUMO DA LIMPEZA${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${G}✅ Containers Docker removidos${NC}"
echo -e "  ${G}✅ Imagens e volumes Docker removidos${NC}"
echo -e "  ${G}✅ Serviços Systemd removidos${NC}"
echo -e "  ${G}✅ Configurações Nginx removidas${NC}"
echo -e "  ${G}✅ Diretórios de projeto removidos${NC}"
echo -e "  ${G}✅ Bancos PostgreSQL removidos (com backup)${NC}"
echo -e "  ${G}✅ Configurações sudo removidas${NC}"
echo -e "  ${G}✅ Arquivos de configuração removidos${NC}"

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${Y}💾 BACKUPS${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Backups salvos em: ~/backups/"
echo ""
if [ -d ~/backups ]; then
    ls -lh ~/backups/ | tail -n +2
fi

echo -e "\n${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${B}ℹ️  PRÓXIMOS PASSOS${NC}"
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Para reinstalar o Conectades:"
echo ""
echo "  ${C}./setup-vps-docker.sh${NC}  (para setup com Docker)"
echo ""
echo "Verificar se ainda existe algo relacionado:"
echo ""
echo "  ${C}docker ps -a | grep conectades${NC}"
echo "  ${C}docker images | grep conectades${NC}"
echo "  ${C}docker volume ls | grep conectades${NC}"
echo "  ${C}sudo -u postgres psql -l | grep conectades${NC}"
echo ""
echo -e "${C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

