# 🔄 Pipeline CI/CD - Conectades

## 📊 Visão Geral

O projeto Conectades usa **GitHub Actions** para automatizar o processo de deploy em dois ambientes:
- **Development (develop)**: Para testes e desenvolvimento
- **Production (main/prod)**: Ambiente de produção

---

## 🌳 Estrutura de Branches

```
┌─────────────────────────────────────────────────────────┐
│                    FLUXO DE BRANCHES                     │
└─────────────────────────────────────────────────────────┘

feature/nova-funcionalidade
    │
    │ (PR + Code Review)
    ↓
develop ────────────► [Auto Deploy DEV] ────► Servidor Dev
    │
    │ (PR + Aprovação + Tests)
    ↓
main ───────────────► [Auto Deploy PROD] ───► Servidor Prod
```

### Regras de Proteção

#### **Branch `develop`:**
- ✅ Permite push direto (para desenvolvimento rápido)
- ✅ Deploy automático ao fazer push
- ✅ Executa testes antes do deploy
- ⚠️ Pode ter bugs (ambiente de testes)

#### **Branch `main` (produção):**
- 🔒 **Protegida** - apenas via Pull Request
- 🔒 Requer aprovação de pelo menos 1 revisor
- ✅ Testes obrigatórios passando
- ✅ Verifica segurança (safety, bandit)
- ✅ Backup automático antes do deploy
- ✅ Health check pós-deploy
- 🔙 Rollback automático se falhar

---

## 🔧 Workflows Configurados

### 1. Deploy to Development (.github/workflows/deploy-develop.yml)

**Trigger:**
- Push para branch `develop`
- Pull Request para `develop`

**Jobs:**

#### **Job 1: Test**
```yaml
- Configurar PostgreSQL e Redis
- Instalar dependências Python
- Executar migrações
- Rodar testes
- Verificar linting
```

#### **Job 2: Deploy** (apenas se tests passar)
```yaml
- Conectar ao servidor via SSH
- Pull do código
- Atualizar dependências
- Executar migrações
- Coletar static files
- Reiniciar aplicação
```

### 2. Deploy to Production (.github/workflows/deploy-production.yml)

**Trigger:**
- Push para branch `main` ou `prod`
- Pull Request para `main` ou `prod`

**Jobs:**

#### **Job 1: Test**
```yaml
- Configurar PostgreSQL e Redis
- Instalar dependências Python
- Verificar migrações pendentes
- Rodar testes completos
- Verificar linting
- Verificar segurança (safety, bandit)
```

#### **Job 2: Deploy** (apenas se tests passar)
```yaml
- Fazer backup do banco de dados
- Conectar ao servidor via SSH
- Pull do código
- Atualizar dependências
- Executar migrações
- Coletar static files
- Reiniciar aplicação
- Health check
- Rollback se falhar
```

---

## 🔐 GitHub Secrets Necessários

### Development

Vá em: **Settings → Secrets → Actions → New repository secret**

```
DEV_SSH_HOST=ip-servidor-dev
DEV_SSH_USERNAME=usuario
DEV_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
DEV_SSH_PORT=22
DEV_PROJECT_PATH=/var/www/conectades-dev
```

### Production

```
PROD_SSH_HOST=seu-vps.hostinger.com
PROD_SSH_USERNAME=usuario
PROD_SSH_PRIVATE_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
PROD_SSH_PORT=22
PROD_PROJECT_PATH=/var/www/conectades
PROD_DB_NAME=conectades
PROD_BRANCH=main
PROD_HEALTH_CHECK_URL=https://api.conectades.com/health/
```

---

## 🚀 Como Usar

### Desenvolvimento

```bash
# 1. Criar feature branch
git checkout develop
git pull origin develop
git checkout -b feature/minha-funcionalidade

# 2. Desenvolver
# ... fazer mudanças ...

# 3. Commit e push
git add .
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/minha-funcionalidade

# 4. Criar PR no GitHub
# feature/minha-funcionalidade → develop

# 5. Após merge: deploy automático para DEV!
# Acompanhe em: https://github.com/seu-usuario/conectades/actions
```

### Produção

```bash
# 1. Garantir que develop está estável
# Testar em https://dev.conectades.com

# 2. Criar PR para produção
# develop → main

# 3. Code Review
# Pelo menos 1 aprovação necessária

# 4. Após aprovação e merge: deploy automático para PROD!
# - Backup automático
# - Deploy
# - Health check
# - Se falhar: rollback automático
```

---

## 📋 Checklist Pré-Deploy

### Antes de Mergear para Develop:
- [ ] Código funciona localmente
- [ ] Testes passando
- [ ] Sem erros de linting
- [ ] Migrações criadas (se necessário)
- [ ] Documentação atualizada

### Antes de Mergear para Main (Produção):
- [ ] Testado em ambiente de desenvolvimento
- [ ] Todos os testes passando
- [ ] Code review aprovado
- [ ] Migrações testadas
- [ ] Backup recente disponível
- [ ] Plano de rollback definido
- [ ] Stakeholders notificados

---

## 🔍 Monitoramento de Deploys

### Visualizar Workflow

1. Acesse: `https://github.com/seu-usuario/conectades/actions`
2. Clique no workflow em execução
3. Acompanhe cada step em tempo real

### Logs em Tempo Real

```bash
# No servidor (via SSH)
# Logs do serviço
sudo journalctl -u conectades -f

# Logs do Gunicorn
tail -f /var/www/conectades/logs/gunicorn_error.log

# Logs do Django
tail -f /var/www/conectades/logs/django.log

# Logs do Nginx
sudo tail -f /var/log/nginx/conectades_error.log
```

---

## ⚠️ Troubleshooting

### Deploy falhou no GitHub Actions

1. **Ver logs detalhados:**
   - Actions → Workflow → Job → Step
   - Copiar erro completo

2. **Erros comuns:**
   - ❌ **SSH connection failed**: Verificar secrets e chave SSH
   - ❌ **Tests failed**: Corrigir testes localmente primeiro
   - ❌ **Migration error**: Testar migração localmente
   - ❌ **Permission denied**: Ajustar permissões no servidor

### Deploy sucedeu mas site não funciona

```bash
# Conectar ao servidor
ssh usuario@vps.hostinger.com

# Verificar serviço
sudo systemctl status conectades

# Ver últimos erros
sudo journalctl -u conectades -n 50 --no-pager

# Reiniciar manualmente
sudo systemctl restart conectades

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Rollback Manual

```bash
# No servidor
cd /var/www/conectades

# Ver commits recentes
git log --oneline -10

# Voltar para commit anterior
git reset --hard HEAD~1
# ou
git checkout COMMIT_HASH

# Recarregar
sudo systemctl restart conectades
```

---

## 🎯 Boas Práticas

### 1. Sempre Testar Localmente

```bash
# Antes de fazer push
./deploy.sh dev  # Testa localmente
```

### 2. Usar Mensagens de Commit Semânticas

```bash
feat: adiciona nova funcionalidade
fix: corrige bug na autenticação
docs: atualiza documentação
refactor: refatora modelo de doações
perf: melhora performance de queries
test: adiciona testes para campanhas
chore: atualiza dependências
```

### 3. Deploy Gradual

```
1. Desenvolver em feature branch
2. Mergear para develop
3. Testar em DEV por pelo menos 24h
4. Se estável, mergear para main
5. Deploy automático para PROD
```

### 4. Monitorar Pós-Deploy

```bash
# Primeiros 10 minutos após deploy
- Verificar logs
- Testar funcionalidades críticas
- Monitorar performance
- Verificar erros 500/404
```

---

## 📈 Métricas de Deploy

### Objetivos

- ⚡ **Deploy time**: < 5 minutos
- ✅ **Success rate**: > 95%
- 🔙 **Rollback time**: < 2 minutos
- 🐛 **Zero downtime**: Sempre

### Monitorar

```bash
# Ver histórico de deploys
gh run list --workflow=deploy-production.yml

# Ver último deploy
gh run view

# Ver logs de um deploy específico
gh run view RUN_ID --log
```

---

## 🔄 Fluxo Completo de Exemplo

### Cenário: Nova Funcionalidade

```bash
# Dia 1: Desenvolvimento
git checkout develop
git pull origin develop
git checkout -b feature/doacao-rapida
# ... desenvolver ...
git push origin feature/doacao-rapida
# Criar PR: feature/doacao-rapida → develop
# Mergear → Deploy automático para DEV ✅

# Dia 2-3: Testes em DEV
# Testar em https://dev.conectades.com
# Corrigir bugs se necessário
# Push direto para develop → Deploy automático ✅

# Dia 4: Promover para Produção
# Criar PR: develop → main
# Code review + aprovação
# Mergear → Deploy automático para PROD ✅
# Monitorar por 1 hora
```

---

## 📚 Recursos Adicionais

### Links Úteis

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SSH Action](https://github.com/appleboy/ssh-action)
- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Nginx Docs](https://nginx.org/en/docs/)

### Arquivos Relacionados

- `.github/workflows/deploy-develop.yml` - Workflow de desenvolvimento
- `.github/workflows/deploy-production.yml` - Workflow de produção
- `deploy.sh` - Script helper de deploy
- `docs/DEPLOY_HOSTINGER.md` - Guia completo de configuração

---

## ✅ Status Atual

- [x] Workflows criados
- [x] Scripts de deploy criados
- [x] Documentação completa
- [ ] Secrets configurados no GitHub
- [ ] VPS Hostinger configurado
- [ ] Primeiro deploy realizado
- [ ] Monitoramento configurado

**Pronto para configurar quando tiver as credenciais da Hostinger! 🚀**

