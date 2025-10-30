#!/bin/bash

##############################################################################
# Script de Deploy para Conectades
# Uso: ./deploy.sh [dev|prod]
##############################################################################

set -e  # Sair em caso de erro

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
    echo "❌ Erro: Especifique o ambiente (dev ou prod)"
    echo "Uso: ./deploy.sh [dev|prod]"
    exit 1
fi

echo "🚀 Iniciando deploy para ambiente: $ENVIRONMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para log
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar branch atual
CURRENT_BRANCH=$(git branch --show-current)
echo "📋 Branch atual: $CURRENT_BRANCH"

if [ "$ENVIRONMENT" == "prod" ] && [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "prod" ]; then
    log_warning "Você não está na branch main/prod!"
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. Verificar se há mudanças não commitadas
if [[ -n $(git status -s) ]]; then
    log_warning "Existem mudanças não commitadas!"
    git status -s
    read -p "Deseja continuar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 2. Pull das últimas mudanças
echo "🔄 Atualizando código local..."
git pull origin $CURRENT_BRANCH
log_success "Código atualizado"

# 3. Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
    log_success "Ambiente virtual ativado"
else
    log_error "Ambiente virtual não encontrado!"
    exit 1
fi

# 4. Instalar/Atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt --quiet
log_success "Dependências instaladas"

# 5. Verificar migrações pendentes
echo "🔍 Verificando migrações..."
cd backend
python manage.py makemigrations --check --dry-run 2>&1 | grep -q "No changes detected" || {
    log_warning "Existem migrações não criadas!"
    python manage.py makemigrations
}

# 6. Executar migrações
echo "🗄️  Executando migrações..."
python manage.py migrate --noinput
log_success "Migrações aplicadas"

# 7. Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
log_success "Arquivos estáticos coletados"

# 8. Executar testes (apenas em prod)
if [ "$ENVIRONMENT" == "prod" ]; then
    echo "🧪 Executando testes..."
    python manage.py test --noinput
    log_success "Testes passaram"
fi

cd ..

# 9. Confirmar deploy
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Pronto para deploy em $ENVIRONMENT!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ENVIRONMENT" == "prod" ]; then
    log_warning "ATENÇÃO: Deploy para PRODUÇÃO!"
    read -p "Tem certeza que deseja continuar? (yes/N): " -r
    if [[ ! $REPLY == "yes" ]]; then
        log_warning "Deploy cancelado"
        exit 0
    fi
fi

# 10. Push para GitHub (triggers GitHub Actions)
echo "🚀 Fazendo push para $CURRENT_BRANCH..."
git push origin $CURRENT_BRANCH

log_success "Deploy iniciado!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Próximos passos:"
echo "   1. Acompanhe o progresso em: https://github.com/sergiomonteirodev/conectades/actions"
echo "   2. Aguarde conclusão do workflow"
echo "   3. Verifique a aplicação no ambiente"
if [ "$ENVIRONMENT" == "dev" ]; then
    echo "   4. Acesse: http://dev.conectades.com"
else
    echo "   4. Acesse: https://api.conectades.com"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

