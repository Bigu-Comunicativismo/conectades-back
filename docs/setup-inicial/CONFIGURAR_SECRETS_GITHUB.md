# 🔐 Configuração de Secrets no GitHub para CI/CD

## 📋 Passo a Passo

### 1. Acessar as Configurações de Secrets no GitHub

1. Acesse: https://github.com/Bigu-Comunicativismo/conectades-back
2. Clique em **Settings** (Configurações)
3. No menu lateral esquerdo, clique em **Secrets and variables** → **Actions**
4. Clique no botão **New repository secret**

---

## 🔑 Secrets para Configurar

### Ambiente de DESENVOLVIMENTO (develop)

Adicione os seguintes secrets (clique em "New repository secret" para cada um):

#### 1. `DEV_SSH_HOST`
- **Nome do secret**: `DEV_SSH_HOST`
- **Valor**: `SEU_IP_DO_SERVIDOR` (ex: `72.61.134.237` ou hostname da VPS)

#### 2. `DEV_SSH_USERNAME`
- **Nome do secret**: `DEV_SSH_USERNAME`
- **Valor**: `root` (ou o usuário que você usa para acessar a VPS via SSH)

#### 3. `DEV_SSH_PORT`
- **Nome do secret**: `DEV_SSH_PORT`
- **Valor**: `22` (porta padrão SSH)

#### 4. `DEV_PROJECT_PATH`
- **Nome do secret**: `DEV_PROJECT_PATH`
- **Valor**: `/var/www/conectades-dev`

#### 5. `DEV_SSH_PRIVATE_KEY`
- **Nome do secret**: `DEV_SSH_PRIVATE_KEY`
- **Valor**: Veja a seção "Como obter a chave privada" abaixo

---

### Ambiente de PRODUÇÃO (main)

Repita o processo acima, mas com prefixo `PROD_`:

- `PROD_SSH_HOST` = SEU_IP_DO_SERVIDOR (mesmo IP ou diferente se tiver outro servidor)
- `PROD_SSH_USERNAME` = `root` (ou seu usuário)
- `PROD_SSH_PORT` = `22`
- `PROD_PROJECT_PATH` = `/var/www/conectades-prod`
- `PROD_SSH_PRIVATE_KEY` = (mesma chave privada abaixo)

---

## 🔐 Como obter a chave SSH privada

A chave privada já foi gerada localmente. Para copiar o conteúdo:

### No Linux/Mac:
```bash
cat ~/.ssh/id_rsa_conectades
```

**Copie TODO o conteúdo** que aparece, incluindo:
- `-----BEGIN OPENSSH PRIVATE KEY-----`
- Todo o conteúdo do meio
- `-----END OPENSSH PRIVATE KEY-----`

Cole esse conteúdo completo no secret `DEV_SSH_PRIVATE_KEY` e `PROD_SSH_PRIVATE_KEY`.

---

## 📤 Adicionar a chave pública no servidor VPS

Antes de tudo funcionar, você precisa adicionar a chave pública no servidor:

### Opção 1: Copiar manualmente

1. **Copie a chave pública**:
```bash
cat ~/.ssh/id_rsa_conectades.pub
```

2. **Acesse o servidor via SSH**:
```bash
ssh root@SEU_IP_DO_SERVIDOR
```

3. **No servidor, adicione a chave**:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "COLE_AQUI_A_CHAVE_PUBLICA" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Opção 2: Usar ssh-copy-id (mais fácil)

Se você já tem acesso SSH normal ao servidor:

```bash
ssh-copy-id -i ~/.ssh/id_rsa_conectades.pub root@SEU_IP_DO_SERVIDOR
```

Digite a senha quando solicitado.

---

## ✅ Verificar se está funcionando

Depois de configurar tudo, teste a conexão SSH:

```bash
ssh -i ~/.ssh/id_rsa_conectades root@SEU_IP_DO_SERVIDOR
```

Se conseguir conectar **sem pedir senha**, está tudo certo! ✅

---

## 🚀 Depois de configurar os secrets

1. Faça um push para a branch `develop`:
```bash
git push origin develop
```

2. O GitHub Actions vai:
   - ✅ Rodar os testes
   - ✅ Conectar via SSH no servidor
   - ✅ Fazer pull do código
   - ✅ Instalar dependências
   - ✅ Rodar migrações
   - ✅ Reiniciar os serviços

3. Acompanhe em: https://github.com/Bigu-Comunicativismo/conectades-back/actions

---

## 📝 Resumo dos Secrets

| Secret | Valor Exemplo | Descrição |
|--------|---------------|-----------|
| `DEV_SSH_HOST` | `72.61.134.237` | IP ou hostname do servidor |
| `DEV_SSH_USERNAME` | `root` | Usuário SSH |
| `DEV_SSH_PORT` | `22` | Porta SSH |
| `DEV_PROJECT_PATH` | `/var/www/conectades-dev` | Caminho do projeto |
| `DEV_SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH...` | Chave privada completa |

Repita com prefixo `PROD_` para produção.

---

## 🆘 Problemas Comuns

### "Permission denied (publickey)"
- A chave pública não foi adicionada ao servidor
- Execute: `ssh-copy-id -i ~/.ssh/id_rsa_conectades.pub root@SEU_IP`

### "Host key verification failed"
- Primeiro acesso ao servidor
- Execute: `ssh-keyscan SEU_IP >> ~/.ssh/known_hosts`

### "missing server host"
- Secret `DEV_SSH_HOST` não foi configurado no GitHub
- Verifique se o nome do secret está correto (exatamente `DEV_SSH_HOST`)

---

## 🎯 Informações Necessárias

**ANTES DE CONFIGURAR, você precisa saber:**

✅ IP do seu servidor VPS (ex: `72.61.134.237`)  
✅ Usuário SSH (geralmente `root`)  
✅ Porta SSH (geralmente `22`)  
✅ Ter acesso SSH ao servidor (conseguir logar via `ssh root@IP`)

Se você ainda não tem essas informações, consulte o painel da Hostinger ou onde sua VPS está hospedada.












