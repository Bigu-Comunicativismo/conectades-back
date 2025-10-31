# 🗑️ Como Limpar o Cache Redis

## 🤖 Limpeza Automática

O sistema agora possui **limpeza automática de cache** em duas situações:

### 1️⃣ Após Migrations (Signal post_migrate)
Sempre que você executar `python manage.py migrate`, o cache é limpo automaticamente.

### 2️⃣ Detecção de Cache Corrompido (Middleware)
Se uma requisição encontrar erro de serialização no cache, o middleware:
- ✅ Detecta o erro automaticamente
- ✅ Limpa o cache Redis
- ✅ Retorna HTTP 503 (Service Unavailable) com `retry_after: 2`
- ✅ Cliente pode tentar novamente em 2 segundos

**Resultado:** Você não precisa mais limpar cache manualmente na maioria dos casos! 🎉

## Quando usar limpeza manual?

Limpe o cache manualmente apenas quando:
- ✅ Quiser forçar reconstrução do cache sem esperar erro
- ✅ Fizer alterações em dados estáticos (categorias, localizações)
- ✅ Quiser limpar chaves específicas para testes

## 📝 Comandos

### 1️⃣ Servidor Local (Desenvolvimento)

```bash
# Com venv ativado
cd backend
python manage.py clear_cache

# Ou com Python path
PYTHONPATH=/caminho/do/projeto DJANGO_SETTINGS_MODULE=backend.core.settings_local python manage.py clear_cache
```

### 2️⃣ Servidor Docker (Produção/Dev)

```bash
# Para ambiente de desenvolvimento
cd /var/www/conectades-dev
sudo docker compose exec web python backend/manage.py clear_cache

# Para ambiente de produção
cd /var/www/conectades-prod
sudo docker compose exec web python backend/manage.py clear_cache
```

### 3️⃣ Limpar chaves específicas

```bash
# Local
python manage.py clear_cache --keys "campanhas_lista,opcoes_cadastro"

# Docker
sudo docker compose exec web python backend/manage.py clear_cache --keys "campanhas_lista,opcoes_cadastro"
```

## 🔧 Chaves de Cache Usadas no Sistema

| Chave | Descrição | TTL |
|-------|-----------|-----|
| `campanhas_lista` | Lista de campanhas ativas | 1 hora |
| `opcoes_cadastro` | Opções para formulário de cadastro | 1 hora |
| `bairros_{cidade}` | Lista de bairros por cidade | 1 hora |
| `campanhas_destaque` | Campanhas em destaque | 5 min |

## 🐛 Resolvendo Problemas

### Erro: "Object of type Response is not JSON serializable"

**Causa:** Cache Redis contém dados serializados incorretamente de versões anteriores do código.

**Solução:**
```bash
# Limpe TODO o cache
sudo docker compose exec web python backend/manage.py clear_cache
```

### Erro: "ModuleNotFoundError: No module named 'backend'"

**Causa:** PYTHONPATH não configurado corretamente.

**Solução:**
```bash
# Use o caminho completo do manage.py dentro do container
sudo docker compose exec web python backend/manage.py clear_cache
```

## 💡 Dicas

1. **Após Deploy**: Sempre limpe o cache após fazer deploy de alterações significativas
2. **Cache Automático**: O cache é reconstruído automaticamente nas próximas requisições
3. **Performance**: Limpar o cache pode causar lentidão temporária até que seja reconstruído
4. **Monitoramento**: Verifique os logs após limpar o cache para garantir que tudo foi reconstruído corretamente

## 🔍 Verificar Status do Redis

```bash
# Entrar no container Redis
sudo docker compose exec redis redis-cli

# Comandos úteis dentro do redis-cli:
# INFO               # Informações gerais do Redis
# DBSIZE             # Número de chaves no banco atual
# KEYS *             # Listar todas as chaves (cuidado em produção!)
# FLUSHDB            # Limpar banco atual (mesmo que o comando clear_cache)
# MONITOR            # Monitorar comandos em tempo real
```

## 📚 Referências

- [Django Cache Framework](https://docs.djangoproject.com/en/5.2/topics/cache/)
- [Redis Commands](https://redis.io/commands/)
- [Django Redis](https://github.com/jazzband/django-redis)

