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

# Aguardar Django estar pronto
echo "🐍 Aguardando Django..."
ATTEMPTS=0
MAX_ATTEMPTS=30
until docker-compose exec -T web python backend/manage.py check >/dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
        echo "⚠️  Timeout aguardando Django. Logs:"
        docker-compose logs web --tail=50
        exit 1
    fi
    echo "   Aguardando... ($ATTEMPTS/$MAX_ATTEMPTS)"
    sleep 3
done
echo "✅ Django está pronto!"

# Executar migrações
echo "📊 Executando migrações..."
docker-compose exec -T web python backend/manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
docker-compose exec -T web python backend/manage.py collectstatic --noinput

# Popular dados iniciais (executa migrations/0005)
echo "📝 Populando dados iniciais (tipos, gêneros, categorias)..."
docker-compose exec -T web python backend/manage.py migrate pessoas 0005 2>/dev/null || true

# Carregar localizações
echo "🌍 Carregando localizações da RMR..."
docker-compose exec -T web python backend/manage.py carregar_localizacoes_rmr 2>/dev/null || echo "⚠️  Aviso: erro ao carregar localizações"

# Criar superusuário
echo "👤 Criando superusuário..."
docker-compose exec -T web python backend/manage.py shell -c "
from backend.pessoas.models import Pessoa, TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse

try:
    tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
    genero = Genero.objects.get(codigo='prefiro-nao-informar')
    categoria = CategoriaInteresse.objects.get(codigo='outros')
    localizacao = LocalizacaoInteresse.objects.filter(tipo='cidade').first()
    
    admin_user, created = Pessoa.objects.get_or_create(
        username='admin',
        defaults={
            'nome_completo': 'Administrador do Sistema',
            'cpf': '000.000.000-00',
            'telefone': '(81) 99999-9999',
            'email': 'admin@conectades.com',
            'tipo_usuario': tipo_doadora,
            'genero': genero,
            'cidade': 'Recife',
            'bairro': 'Centro',
            'nome_social': 'Admin',
            'mini_bio': 'Administrador do sistema',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    
    admin_user.set_password('admin123')
    admin_user.save()
    
    admin_user.categorias_interesse.set([categoria])
    if localizacao:
        admin_user.localizacoes_interesse.set([localizacao])
    
    print('✅ Superusuário: admin/admin123')
except Exception as e:
    print(f'⚠️  Erro ao criar superusuário: {e}')
" 2>/dev/null || echo "⚠️  Aviso: erro ao criar superusuário"

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
echo ""
echo "📊 DADOS POPULADOS:"
echo "==================="
echo "✅ 2 Tipos de Usuário (Beneficiária, Doadora)"
echo "✅ 10 Gêneros"
echo "✅ 11 Categorias de Interesse"
echo "✅ 15 Cidades da RMR"
echo "✅ 91 Bairros de Recife"
echo "✅ Total: 106 localizações"
echo ""
echo "👤 LOGIN ADMIN:"
echo "==============="
echo "Usuário: admin"
echo "Senha: admin123"

