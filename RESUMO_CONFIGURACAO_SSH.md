# 🚀 Resumo Rápido - Configuração SSH para CI/CD

## ✅ O que já foi feito localmente:

1. ✅ Chave SSH gerada: `~/.ssh/id_rsa_conectades`
2. ✅ Script criado: `copiar-chave-para-vps.sh`
3. ✅ Documentação completa: `CONFIGURAR_SECRETS_GITHUB.md`

---

## 📋 O que você precisa fazer agora:

### Passo 1: Copiar a chave para o servidor VPS

Execute o script interativo:

```bash
./copiar-chave-para-vps.sh
```

**OU** faça manualmente:

```bash
# Substitua SEU_IP pelo IP real da VPS
ssh-copy-id -i ~/.ssh/id_rsa_conectades.pub root@SEU_IP
```

---

### Passo 2: Configurar Secrets no GitHub

Acesse: https://github.com/Bigu-Comunicativismo/conectades-back/settings/secrets/actions

Crie os seguintes secrets (clique em "New repository secret"):

#### Para Development (develop):

1. **DEV_SSH_HOST**
   ```
   SEU_IP_DA_VPS
   ```

2. **DEV_SSH_USERNAME**
   ```
   root
   ```

3. **DEV_SSH_PORT**
   ```
   22
   ```

4. **DEV_SSH_PROJECT_PATH**
   ```
   /var/www/conectades-dev
   ```

5. **DEV_SSH_PRIVATE_KEY**
   ```bash
   # Para copiar a chave privada:
   cat ~/.ssh/id_rsa_conectades
   
   # Cole TODO o conteúdo (incluindo BEGIN e END)
   ```

#### Para Production (main):

Repita os mesmos secrets acima, mas com prefixo `PROD_` ao invés de `DEV_`:
- `PROD_SSH_HOST`
- `PROD_SSH_USERNAME`
- `PROD_SSH_PORT`
- `PROD_PROJECT_PATH` = `/var/www/conectades-prod`
- `PROD_SSH_PRIVATE_KEY`

---

## 🧪 Testar a configuração

Depois de configurar os secrets, faça um push:

```bash
git push origin develop
```

Acompanhe em: https://github.com/Bigu-Comunicativismo/conectades-back/actions

Se tudo estiver correto, verá:
- ✅ Tests passed
- ✅ Deploy to Development Server - succeeded

---

## 📱 Comandos Úteis

### Ver a chave pública:
```bash
cat ~/.ssh/id_rsa_conectades.pub
```

### Ver a chave privada (para o secret):
```bash
cat ~/.ssh/id_rsa_conectades
```

### Testar conexão SSH:
```bash
ssh -i ~/.ssh/id_rsa_conectades root@SEU_IP
```

### Verificar se a chave está no servidor:
```bash
ssh root@SEU_IP "cat ~/.ssh/authorized_keys"
```

---

## 🆘 Problemas?

Leia o arquivo `CONFIGURAR_SECRETS_GITHUB.md` para instruções detalhadas e solução de problemas.

---

## 🎯 Informações que você precisa:

- [ ] IP ou hostname da VPS
- [ ] Usuário SSH (geralmente `root`)
- [ ] Porta SSH (geralmente `22`)
- [ ] Conseguir acessar via SSH: `ssh root@IP`

Se não tem essas informações, consulte o painel da Hostinger.












