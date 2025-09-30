#!/bin/bash

# Script para inicializar a aplicação Conectades com arquitetura otimizada
# Nginx + Redis + Uvicorn + Django

echo "🚀 Iniciando Conectades - Arquitetura Otimizada para 1000+ Usuários"
echo "=================================================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover volumes antigos (opcional - descomente se quiser limpar dados)
# echo "🗑️  Removendo volumes antigos..."
# docker-compose down -v

# Build das imagens
echo "🔨 Fazendo build das imagens..."
docker-compose build --no-cache

# Subir os serviços
echo "⬆️  Subindo serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."

# Aguardar PostgreSQL
echo "🐘 Aguardando PostgreSQL..."
until docker-compose exec -T db pg_isready -U admin_conectades -d conectades; do
    echo "   PostgreSQL ainda não está pronto..."
    sleep 2
done
echo "✅ PostgreSQL está pronto!"

# Aguardar Redis
echo "🔴 Aguardando Redis..."
until docker-compose exec -T redis redis-cli ping; do
    echo "   Redis ainda não está pronto..."
    sleep 2
done
echo "✅ Redis está pronto!"

# Aguardar Django via HTTP (Nginx -> web) para garantir que a stack respondeu
echo "🐍 Aguardando Django (via Nginx /health)..."
ATTEMPTS=0
until curl -sf http://localhost/health > /dev/null; do
    ATTEMPTS=$((ATTEMPTS+1))
    # Fallback: tentar checar via manage.py com caminho correto
    docker-compose exec -T web python backend/manage.py check >/dev/null 2>&1 || true
    echo "   Django ainda não está pronto... (tentativa $ATTEMPTS)"
    sleep 2
    # Evitar loop infinito (timeout ~120s)
    if [ "$ATTEMPTS" -ge 60 ]; then
        echo "⚠️  Timeout aguardando Django. Verificando logs do web:"
        docker-compose logs --tail=100 web
        exit 1
    fi
done
echo "✅ Django está pronto!"

# Executar migrações
echo "📊 Executando migrações..."
docker-compose exec -T web python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Criar superusuário (opcional)
echo "👤 Criando superusuário de teste..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@conectades.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Verificar status dos serviços
echo ""
echo "📊 STATUS DOS SERVIÇOS:"
echo "======================"
docker-compose ps

echo ""
echo "🌐 URLs DE ACESSO:"
echo "=================="
echo "🔗 API: http://localhost/api/"
echo "📚 Documentação: http://localhost/api/docs/"
echo "⚙️  Admin: http://localhost/admin/"
echo "❤️  Health Check: http://localhost/health"

echo ""
echo "📊 MONITORAMENTO:"
echo "================="
echo "📋 Logs em tempo real: docker-compose logs -f"
echo "📋 Logs do Django: docker-compose logs -f web"
echo "📋 Logs do Redis: docker-compose logs -f redis"
echo "📋 Logs do Nginx: docker-compose logs -f nginx"

echo ""
echo "🧪 TESTE DE PERFORMANCE:"
echo "========================"
echo "🐍 python test_performance.py"

echo ""
echo "✅ APLICAÇÃO INICIADA COM SUCESSO!"
echo "🎯 Arquitetura otimizada para 1000+ usuários simultâneos"
echo "⚡ Nginx + Redis + Uvicorn + Django"

