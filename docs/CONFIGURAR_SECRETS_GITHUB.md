# 🔐 Como Configurar Secrets no GitHub Actions

## 📍 Onde Adicionar os Secrets

### Passo a Passo:

1. **Acesse o repositório no GitHub:**
   ```
   https://github.com/Bigu-Comunicativismo/conectades-back
   ```

2. **Vá em Settings:**
   - Clique na aba **"Settings"** (⚙️) no menu superior do repositório

3. **Acesse Secrets and Variables:**
   - No menu lateral esquerdo, procure por **"Security"**
   - Clique em **"Secrets and variables"**
   - Clique em **"Actions"**

4. **Adicione os Secrets:**
   - Clique no botão verde **"New repository secret"**
   - Preencha **Name** (nome do secret)
   - Preencha **Value** (valor do secret)
   - Clique em **"Add secret"**

## 🔑 Secrets Necessários

### Para Deploy de Desenvolvimento (deploy-develop.yml)

| Secret Name | Descrição | Exemplo |
|-------------|-----------|---------|
| `DEV_SSH_HOST` | IP ou domínio do servidor | `srv1037558.hstgr.cloud` |
| `DEV_SSH_USERNAME` | Usuário SSH | `lelo` |
| `DEV_SSH_PRIVATE_KEY` | Chave SSH privada (conteúdo completo) | Ver seção abaixo |
| `DEV_SSH_PORT` | Porta SSH | `22` |
| `DEV_PROJECT_PATH` | Caminho do projeto no servidor | `/var/www/conectades-dev` |

### Para Deploy de Produção (deploy-production.yml)

| Secret Name | Descrição | Exemplo |
|-------------|-----------|---------|
| `PROD_SSH_HOST` | IP ou domínio do servidor | `api.conectades.com` |
| `PROD_SSH_USERNAME` | Usuário SSH | `lelo` |
| `PROD_SSH_PRIVATE_KEY` | Chave SSH privada (conteúdo completo) | Ver seção abaixo |
| `PROD_SSH_PORT` | Porta SSH | `22` |
| `PROD_PROJECT_PATH` | Caminho do projeto no servidor | `/var/www/conectades-prod` |
| `PROD_BRANCH` | Branch de produção | `main` ou `prod` |
| `PROD_DB_NAME` | Nome do banco de dados | `conectades` |
| `PROD_HEALTH_CHECK_URL` | URL para health check | `https://api.conectades.com/api/health/` |

## 🔐 Como Obter a Chave SSH Privada

### Método 1: Usar chave existente

Se você já tem uma chave SSH configurada no servidor:

```bash
# No seu computador local (onde você acessa o servidor)
cat ~/.ssh/id_rsa
```

**⚠️ IMPORTANTE:** 
- Copie **TODO** o conteúdo, incluindo:
  - `-----BEGIN OPENSSH PRIVATE KEY-----`
  - Todo o texto no meio
  - `-----END OPENSSH PRIVATE KEY-----`

### Método 2: Criar nova chave SSH (recomendado)

```bash
# Gerar nova chave SSH específica para GitHub Actions
ssh-keygen -t rsa -b 4096 -C "github-actions@conectades" -f ~/.ssh/github_actions_conectades

# Exibir a chave privada (copie para o secret)
cat ~/.ssh/github_actions_conectades

# Exibir a chave pública (adicione no servidor)
cat ~/.ssh/github_actions_conectades.pub
```

**Adicionar chave pública no servidor:**

```bash
# No servidor (via SSH normal)
nano ~/.ssh/authorized_keys
# Cole a chave pública no final do arquivo
# Salve e saia (Ctrl+X, Y, Enter)

# Verificar permissões
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

## 📝 Exemplo de Configuração Completa

### Desenvolvimento

```
Name: DEV_SSH_HOST
Value: srv1037558.hstgr.cloud

Name: DEV_SSH_USERNAME
Value: lelo

Name: DEV_SSH_PRIVATE_KEY
Value: 
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
... (resto da chave) ...
-----END OPENSSH PRIVATE KEY-----

Name: DEV_SSH_PORT
Value: 22

Name: DEV_PROJECT_PATH
Value: /var/www/conectades-dev
```

### Produção

```
Name: PROD_SSH_HOST
Value: api.conectades.com

Name: PROD_SSH_USERNAME
Value: lelo

Name: PROD_SSH_PRIVATE_KEY
Value: 
-----BEGIN OPENSSH PRIVATE KEY-----
... (chave SSH completa) ...
-----END OPENSSH PRIVATE KEY-----

Name: PROD_SSH_PORT
Value: 22

Name: PROD_PROJECT_PATH
Value: /var/www/conectades-prod

Name: PROD_BRANCH
Value: main

Name: PROD_DB_NAME
Value: conectades

Name: PROD_HEALTH_CHECK_URL
Value: https://api.conectades.com/api/health/
```

## ✅ Verificar Configuração

Após adicionar todos os secrets:

1. **Vá em Settings → Secrets and variables → Actions**
2. **Verifique se todos os secrets estão listados:**
   - ✅ DEV_SSH_HOST
   - ✅ DEV_SSH_USERNAME
   - ✅ DEV_SSH_PRIVATE_KEY
   - ✅ DEV_SSH_PORT
   - ✅ DEV_PROJECT_PATH
   - ✅ PROD_SSH_HOST
   - ✅ PROD_SSH_USERNAME
   - ✅ PROD_SSH_PRIVATE_KEY
   - ✅ PROD_SSH_PORT
   - ✅ PROD_PROJECT_PATH
   - ✅ PROD_BRANCH
   - ✅ PROD_DB_NAME
   - ✅ PROD_HEALTH_CHECK_URL

## 🧪 Testar Conexão SSH

### Teste local:

```bash
# Testar conexão SSH (desenvolvimento)
ssh -i ~/.ssh/sua_chave lelo@srv1037558.hstgr.cloud

# Testar conexão SSH (produção)
ssh -i ~/.ssh/sua_chave lelo@api.conectades.com
```

Se conectar com sucesso, a chave está correta! ✅

## 🔒 Segurança

### ✅ Boas Práticas:

1. **Use chaves SSH diferentes para cada ambiente**
   - Uma para dev
   - Outra para prod

2. **Adicione senha nas chaves (opcional)**
   ```bash
   ssh-keygen -p -f ~/.ssh/github_actions_conectades
   ```
   - Se usar senha, adicione secret: `DEV_SSH_PASSPHRASE`

3. **Rotacione as chaves periodicamente**
   - Gere novas chaves a cada 6 meses
   - Atualize nos secrets

4. **Limite permissões no servidor**
   ```bash
   # No servidor, no arquivo authorized_keys
   command="cd /var/www/conectades-dev && git pull" ssh-rsa AAAA...
   ```

5. **Monitore acessos**
   ```bash
   # No servidor
   tail -f /var/log/auth.log | grep sshd
   ```

## 🚨 Troubleshooting

### Erro: "missing server host"
- ✅ Verifique se `DEV_SSH_HOST` ou `PROD_SSH_HOST` está configurado
- ✅ Valor não pode estar vazio

### Erro: "Permission denied (publickey)"
- ✅ Chave privada está correta no secret?
- ✅ Chave pública está em `~/.ssh/authorized_keys` no servidor?
- ✅ Permissões corretas: `chmod 600 ~/.ssh/authorized_keys`

### Erro: "Host key verification failed"
- ✅ Adicione o host aos known_hosts no servidor
- ✅ Ou use `StrictHostKeyChecking=no` no workflow (não recomendado)

## 📚 Recursos Adicionais

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/keygen)
- [appleboy/ssh-action](https://github.com/appleboy/ssh-action)

## 💡 Dicas

1. **Teste sempre em desenvolvimento primeiro!**
2. **Faça backup das chaves SSH**
3. **Documente quais chaves estão em uso**
4. **Use um gerenciador de senhas para guardar as chaves**

