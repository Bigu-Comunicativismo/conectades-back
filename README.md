# Conectades

Solução Digital criada pela Bigu Comunicativismo com apoio do Nic.br e Ponte a Ponte para promover a troca e solidariedade entre mulheres, pessoas trans e travestis, focando prioritariamente em apoios relativos a questão do trabalho, para promover autonomia dessas pessoas.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Linux](#instalação-linux)
- [Instalação macOS](#instalação-macos)
- [Instalação Windows](#instalação-windows)
- [Testando com Insomnia](#testando-com-insomnia)
- [Testando com Postman](#testando-com-postman)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Sobre o Projeto

Plataforma de campanhas de doação que conecta beneficiárias, doadoras e organizadoras.

**Funcionalidades:**
- ✅ Cadastro de pessoas (beneficiárias, doadoras, organizadoras)
- ✅ Criação e gerenciamento de campanhas
- ✅ Registro de doações
- ✅ Autenticação JWT
- ✅ API RESTful documentada
- ✅ Cache Redis (1000+ usuários simultâneos)

---

## 🏗️ Arquitetura

**Performance:** 500-1000 RPS | Latência 10-50ms | Cache 80-90% | 1000+ usuários

```
NGINX → UVICORN (4 workers) → REDIS CACHE → POSTGRESQL
```

---

## 📦 Pré-requisitos

**Todos os sistemas:**
- Docker ≥ 20.10
- Docker Compose ≥ 2.0
- Git
- RAM: 6GB+ (recomendado)
- Disco: 5GB+

---

## 🐧 Instalação Linux

### 1. Clonar e iniciar:
```bash
git clone <url-do-repositorio>
cd conectades
chmod +x start.sh
./start.sh
```

### 2. Acessar:
- API: http://localhost/api/docs/
- Admin: http://localhost/admin/ (admin/admin123)

### Comandos úteis:
```bash
docker-compose logs -f          # Logs
docker-compose down             # Parar
docker-compose exec web python backend/manage.py migrate  # Migrações
```

---

## 🍎 Instalação macOS

### 1. Instalar Docker Desktop:
- Baixe: https://docs.docker.com/desktop/install/mac-install/
- Inicie o Docker Desktop

### 2. Clonar e iniciar:
```bash
git clone <url-do-repositorio>
cd conectades
chmod +x start.sh
./start.sh
```

### 3. Acessar:
- API: http://localhost/api/docs/
- Admin: http://localhost/admin/ (admin/admin123)

---

## 🪟 Instalação Windows

### 1. Instalar:
- Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
- Git for Windows: https://git-scm.com/download/win
- Habilite WSL 2

### 2. PowerShell:
```powershell
git clone <url-do-repositorio>
cd conectades

docker-compose down
docker-compose build --no-cache
docker-compose up -d

Start-Sleep -Seconds 30

docker-compose exec -T web python backend/manage.py migrate
docker-compose exec -T web python backend/manage.py collectstatic --noinput
```

### 3. Criar admin:
```powershell
docker-compose exec web python backend/manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); u,c=U.objects.get_or_create(username='admin', defaults={'email':'admin@conectades.com'}); u.is_staff=True; u.is_superuser=True; u.set_password('admin123'); u.save(); print('OK')"
```

### 4. Acessar:
- API: http://localhost/api/docs/
- Admin: http://localhost/admin/ (admin/admin123)

---

## 🔧 Troubleshooting

### Porta 80 em uso:
```bash
# Linux
sudo lsof -i :80
sudo systemctl stop apache2

# Ou mudar porta no docker-compose.yml:
# nginx: ports: - "8080:80"
```

### Reconstruir tudo:
```bash
docker-compose down -v
docker-compose build --no-cache
./start.sh
```

### Verificar serviços:
```bash
docker-compose ps
curl http://localhost/health
docker-compose exec redis redis-cli ping
```

---

## 🧪 Testando a API

### Documentação Swagger (Recomendado):
Acesse http://localhost/api/docs/ após iniciar a aplicação.

### Testando com Insomnia ou Postman:
Ver guia completo em: **[TESTES_INSOMNIA_POSTMAN.md](TESTES_INSOMNIA_POSTMAN.md)**

**Collections prontas para importar:**
- 📥 **Insomnia**: `insomnia_collection.json`
- 📥 **Postman**: `postman_collection.json`

**Quick Start:**
1. Importar collection no seu cliente REST
2. Executar request **"1. Login"** para obter token
3. Token é salvo automaticamente
4. Testar outros endpoints

---

## 📖 Mais Documentação

- **Testes com Insomnia/Postman**: [TESTES_INSOMNIA_POSTMAN.md](TESTES_INSOMNIA_POSTMAN.md)
- **Performance e Otimizações**: [README_PERFORMANCE.md](README_PERFORMANCE.md)
- **Arquitetura Detalhada**: [arquitetura.md](arquitetura.md)
- **API Interativa**: http://localhost/api/docs/

---

**Desenvolvido por Bigu Comunicativismo | Apoio: Nic.br e Ponte a Ponte**
