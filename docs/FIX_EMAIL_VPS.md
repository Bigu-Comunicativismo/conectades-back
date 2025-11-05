# 🔧 FIX: Email SMTP no Servidor VPS

## 🚨 Problema Identificado

O Docker **não estava lendo o arquivo `.env`**, fazendo com que:
- ❌ `EMAIL_BACKEND` usasse `console` (padrão) ao invés de `smtp`
- ❌ `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` não fossem carregados
- ❌ Emails apareciam no log, mas não eram enviados

---

## ✅ Solução Aplicada

Foi adicionado suporte ao `.env` no `docker-compose.yml`:

```yaml
web:
  build: .
  env_file:
    - .env  # 👈 Isso foi adicionado!
  environment:
    # ... outras variáveis ...
```

---

## 🚀 Como Aplicar o Fix no Servidor

### **1️⃣ Atualizar o código:**

```bash
cd /var/www/conectades-dev
git pull conectades develop
```

---

### **2️⃣ Certificar que o `.env` existe:**

```bash
ls -la .env
```

**Se NÃO existir**, crie:

```bash
nano .env
```

Cole este conteúdo (ajuste se necessário):

```bash
# ============================================================================
# CONFIGURAÇÃO DE EMAIL - CONECTADES
# ============================================================================

EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=contato@bigu.org.br
EMAIL_HOST_PASSWORD=jgvruoezudcvkuwt
DEFAULT_FROM_EMAIL=contato@bigu.org.br
SERVER_EMAIL=contato@bigu.org.br

# URLs
SITE_URL=http://srv1037558.hstgr.cloud:8001
FRONTEND_URL=http://localhost:3000

# Django
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
```

**Salvar:** `Ctrl + O`, `Enter`, `Ctrl + X`

---

### **3️⃣ Reiniciar containers (IMPORTANTE!):**

```bash
docker compose down
docker compose up -d
```

⚠️ **Usar `down` + `up` é OBRIGATÓRIO** para que o Docker recarregue o `.env`!

Um simples `restart` **NÃO funciona** para variáveis de ambiente.

---

### **4️⃣ Verificar se funcionou:**

```bash
docker compose exec web python test_smtp_vps.py
```

**Saída esperada:**
```
📋 CONFIGURAÇÕES ATUAIS:
   EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST: smtp.gmail.com
   EMAIL_PORT: 587
   EMAIL_USE_TLS: True
   EMAIL_USE_SSL: False
   EMAIL_HOST_USER: contato@bigu.org.br
   EMAIL_HOST_PASSWORD: ****************
   DEFAULT_FROM_EMAIL: contato@bigu.org.br

📧 TESTANDO ENVIO DE EMAIL...
   Enviando email de teste para: contato@bigu.org.br
   Aguarde...

✅ EMAIL ENVIADO COM SUCESSO!
```

---

### **5️⃣ Verificar configurações (sem reiniciar):**

```bash
docker compose exec web python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
django.setup()
from django.conf import settings
print('Backend:', settings.EMAIL_BACKEND)
print('Host:', settings.EMAIL_HOST)
print('User:', settings.EMAIL_HOST_USER)
print('Password:', 'OK (' + str(len(settings.EMAIL_HOST_PASSWORD)) + ' chars)' if settings.EMAIL_HOST_PASSWORD else 'VAZIO')
print('From:', settings.DEFAULT_FROM_EMAIL)
"
```

**Antes do fix:**
```
Backend: django.core.mail.backends.console.EmailBackend
Host: smtp.gmail.com
User: 
Password: VAZIO
From: noreply@conectades.com
```

**Depois do fix:**
```
Backend: django.core.mail.backends.smtp.EmailBackend
Host: smtp.gmail.com
User: contato@bigu.org.br
Password: OK (16 chars)
From: contato@bigu.org.br
```

---

### **6️⃣ Testar cadastro de usuário:**

Acesse: `http://srv1037558.hstgr.cloud:8001/api/docs/`

1. Vá em **POST `/api/auth/registro/iniciar/`**
2. Try it out
3. Preencha:
   ```json
   {
     "email": "seu-email@gmail.com",
     "nome_completo": "Teste SMTP"
   }
   ```
4. Execute

**Resposta esperada:**
```json
{
  "message": "Link de ativação enviado para seu email",
  "email": "seu-email@gmail.com"
}
```

**Verifique:**
- ✅ Email deve chegar (aguarde até 2 minutos)
- ✅ Se não chegou na caixa de entrada, **verifique o SPAM**
- ✅ Remetente deve ser: `contato@bigu.org.br`

---

### **7️⃣ Verificar logs (se não chegar):**

```bash
docker compose logs web --tail=50 | grep -E "(mail|smtp|error)" -i
```

**Se aparecer:**
```
From: contato@bigu.org.br
To: seu-email@gmail.com
```

✅ Email foi enviado com sucesso!

---

## 🔍 Troubleshooting

### **Problema: Ainda usando `console` backend**

**Sintoma:**
```
Backend: django.core.mail.backends.console.EmailBackend
```

**Solução:**
```bash
# 1. Verificar .env
cat .env | grep EMAIL_BACKEND
# Deve retornar: EMAIL_BACKEND=smtp

# 2. Se estiver certo, REBUILD o container
docker compose down
docker compose build --no-cache web
docker compose up -d

# 3. Verificar novamente
docker compose exec web python -c "..."
```

---

### **Problema: Senha incorreta**

**Sintoma:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Solução:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma **nova senha de app**
3. Atualize no `.env`:
   ```bash
   nano .env
   # Altere EMAIL_HOST_PASSWORD=nova_senha_aqui
   ```
4. Reinicie: `docker compose down && docker compose up -d`

---

### **Problema: Email não chega**

**Checklist:**
- [ ] `docker compose exec web python test_smtp_vps.py` retorna sucesso?
- [ ] Verificou pasta de SPAM?
- [ ] Aguardou 2-3 minutos?
- [ ] Email `contato@bigu.org.br` está ativo no Gmail?
- [ ] Senha de app está correta (16 caracteres)?
- [ ] Verificação em 2 etapas está ativada no Gmail?

---

## 📊 Antes vs Depois

### **Antes do Fix:**

```bash
# Log do Docker mostrava:
From: noreply@conectades.com  # ❌ Errado
To: usuario@exemplo.com

# Email aparecia no LOG, não era enviado
```

### **Depois do Fix:**

```bash
# Email é ENVIADO via SMTP:
From: contato@bigu.org.br  # ✅ Correto
To: usuario@exemplo.com

# Nada aparece no log (email foi enviado de verdade)
```

---

## 🎯 Comando Completo (Tudo de Uma Vez)

Execute no servidor:

```bash
cd /var/www/conectades-dev && \
git pull conectades develop && \
docker compose down && \
docker compose up -d && \
sleep 10 && \
echo "=== Verificando configurações ===" && \
docker compose exec -T web python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
django.setup()
from django.conf import settings
print('✅ Backend:', settings.EMAIL_BACKEND)
print('✅ User:', settings.EMAIL_HOST_USER)
print('✅ Password:', 'OK' if settings.EMAIL_HOST_PASSWORD else 'VAZIO')
print('✅ From:', settings.DEFAULT_FROM_EMAIL)
" && \
echo "" && \
echo "=== Testando envio ===" && \
docker compose exec -T web python test_smtp_vps.py
```

---

## ✅ Resultado Final Esperado

Quando tudo estiver funcionando:

1. ✅ `EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend`
2. ✅ `EMAIL_HOST_USER = contato@bigu.org.br`
3. ✅ `EMAIL_HOST_PASSWORD` definido (16 caracteres)
4. ✅ `DEFAULT_FROM_EMAIL = contato@bigu.org.br`
5. ✅ Script de teste envia email com sucesso
6. ✅ Email chega na caixa de entrada (ou spam)

---

## 📞 Próximos Passos

Se ainda não funcionar depois deste fix:

1. Execute: `docker compose exec web python test_smtp_vps.py`
2. Copie a saída completa
3. Envie para análise

O script de teste mostrará exatamente onde está o problema! 🔍

---

## 🎉 Pronto!

Após seguir este guia, o email SMTP deve estar funcionando perfeitamente! 📧✨

