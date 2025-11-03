# 📧 Configurar Email SMTP (Gmail)

## ❌ Problema

O cadastro está sendo processado, mas o email de verificação **não está sendo enviado**.

---

## ✅ Solução: Configurar SMTP do Gmail

### 📋 Pré-requisitos

1. ✅ Conta do Gmail
2. ✅ Verificação em duas etapas ativada (obrigatório)
3. ✅ Gerar "Senha de App" do Google

---

## 🔐 Passo 1: Gerar Senha de App do Gmail

### 1.1 Ativar Verificação em Duas Etapas

1. Acesse: https://myaccount.google.com/security
2. Role até "Verificação em duas etapas"
3. Clique em **"Começar"** ou **"Ativar"**
4. Siga as instruções para configurar (pode ser SMS ou app Google Authenticator)

### 1.2 Gerar Senha de App

1. Após ativar a verificação em duas etapas, acesse:
   **https://myaccount.google.com/apppasswords**

2. Faça login novamente se solicitado

3. No campo **"Selecione o app"**:
   - Escolha: **"E-mail"**
   - Ou escolha: **"Outro (nome personalizado)"** e digite: `Conectades`

4. No campo **"Selecione o dispositivo"**:
   - Escolha: **"Outro (nome personalizado)"**
   - Digite: `Servidor Conectades`

5. Clique em **"Gerar"**

6. **IMPORTANTE:** Copie a senha gerada (16 caracteres)
   - Exemplo: `abcd efgh ijkl mnop`
   - **Cole sem os espaços:** `abcdefghijklmnop`

7. Guarde essa senha em local seguro (você vai usá-la no `.env`)

---

## 📝 Passo 2: Configurar Arquivo `.env`

### 2.1 Criar arquivo `.env` (se não existir)

```bash
cd /home/lelo/conectades
touch .env
chmod 600 .env  # Permissões seguras
```

### 2.2 Editar arquivo `.env`

Abra o arquivo `.env` e adicione/edite:

```bash
# Email - SMTP Gmail
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=noreply@conectades.com
SERVER_EMAIL=admin@conectades.com

# URLs
SITE_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
```

**Substitua:**
- `seu_email@gmail.com` → Seu email do Gmail
- `abcdefghijklmnop` → A senha de app gerada (sem espaços)

### ⚠️ ATENÇÃO: Erros Comuns

❌ **NÃO use sua senha normal do Gmail** (não vai funcionar)
✅ Use a **"Senha de App"** gerada

❌ **NÃO coloque espaços na senha**
```bash
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # ❌ ERRADO
```
✅ Cole sem espaços:
```bash
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # ✅ CORRETO
```

❌ **NÃO coloque aspas na senha**
```bash
EMAIL_HOST_PASSWORD="abcdefghijklmnop"  # ❌ ERRADO
```
✅ Cole sem aspas:
```bash
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # ✅ CORRETO
```

---

## 🧪 Passo 3: Testar Envio de Email

### 3.1 Testar via Script Python

```bash
cd /home/lelo/conectades
source venv/bin/activate
python test_email.py
```

O script irá:
1. Mostrar as configurações atuais
2. Solicitar um email de destino
3. Tentar enviar um email de teste
4. Mostrar se foi sucesso ou erro

### 3.2 Testar via Django Shell

```bash
cd /home/lelo/conectades
source venv/bin/activate
PYTHONPATH=/home/lelo/conectades DJANGO_SETTINGS_MODULE=backend.core.settings python backend/manage.py shell
```

Dentro do shell:

```python
from django.core.mail import send_mail
from django.conf import settings

# Verificar configurações
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

# Enviar email de teste
send_mail(
    subject='Teste Conectades',
    message='Email de teste',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['seu_email_teste@gmail.com'],
    fail_silently=False,
)

print("✅ Email enviado!")
```

---

## 🚀 Passo 4: Reiniciar o Servidor

Após configurar o `.env`, reinicie o servidor Django:

```bash
# Se estiver rodando localmente
cd /home/lelo/conectades/backend
source ../venv/bin/activate
PYTHONPATH=/home/lelo/conectades DJANGO_SETTINGS_MODULE=backend.core.settings_local python manage.py runserver 8001
```

---

## 🧪 Passo 5: Testar Cadastro Real

### 5.1 Via Swagger

1. Acesse: http://localhost:8001/api/docs/
2. Procure: `POST /api/auth/iniciar-registro/`
3. Clique "Try it out"
4. Preencha os dados do cadastro
5. Use um **email real que você tenha acesso**
6. Clique "Execute"
7. Verifique sua caixa de entrada (e SPAM)

### 5.2 Via cURL

```bash
curl -X POST http://localhost:8001/api/auth/iniciar-registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu_email@gmail.com",
    "nome_completo": "Maria Silva",
    "cpf": "123.456.789-00",
    "telefone": "81999999999",
    "senha": "senha123",
    "tipo_usuario": 1,
    "genero": 1,
    "cidade": "Recife",
    "bairro": "Centro",
    "nome_social": "Maria",
    "mini_bio": "Teste",
    "categorias_interesse": [1],
    "localizacoes_interesse": [1]
  }'
```

---

## 📋 Checklist de Verificação

### ✅ Gmail

- [ ] Verificação em duas etapas ativada
- [ ] Senha de App gerada
- [ ] Senha copiada sem espaços

### ✅ Arquivo `.env`

- [ ] Arquivo `.env` criado
- [ ] `EMAIL_BACKEND=smtp`
- [ ] `EMAIL_HOST=smtp.gmail.com`
- [ ] `EMAIL_PORT=587`
- [ ] `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER` configurado (seu email)
- [ ] `EMAIL_HOST_PASSWORD` configurado (senha de app)
- [ ] Senha sem espaços e sem aspas

### ✅ Teste

- [ ] Script `test_email.py` executado com sucesso
- [ ] Email de teste recebido
- [ ] Cadastro testado
- [ ] Email de verificação recebido

---

## ❌ Troubleshooting (Problemas Comuns)

### Erro: `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`

**Causa:** Senha incorreta ou não é uma "Senha de App"

**Solução:**
1. Verifique se está usando **"Senha de App"**, não a senha normal
2. Gere uma nova "Senha de App"
3. Cole sem espaços no `.env`

---

### Erro: `SMTPException: STARTTLS extension not supported by server`

**Causa:** Configuração incorreta de TLS/SSL

**Solução:**
```bash
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_PORT=587
```

---

### Erro: `gaierror: [Errno -2] Name or service not known`

**Causa:** Servidor SMTP incorreto

**Solução:**
```bash
EMAIL_HOST=smtp.gmail.com  # Não smtp.google.com
```

---

### Email não chega

**Possíveis causas:**

1. **Email na pasta SPAM**
   - Verifique a pasta de SPAM/Lixo Eletrônico

2. **Email bloqueado pelo Gmail**
   - Acesse: https://myaccount.google.com/notifications
   - Veja se há alertas de segurança
   - Autorize o acesso se necessário

3. **Conta Gmail com limite atingido**
   - Gmail limita envio de emails por dia (500/dia para contas gratuitas)
   - Aguarde 24h ou use outra conta

4. **`.env` não está sendo lido**
   - Verifique se o arquivo está no diretório correto: `/home/lelo/conectades/.env`
   - Reinicie o servidor Django

---

## 🔒 Segurança

### ⚠️ NUNCA commite o arquivo `.env` para o Git!

O `.env` contém informações sensíveis (senha de email).

**Verificar se `.env` está no `.gitignore`:**

```bash
cd /home/lelo/conectades
cat .gitignore | grep -E "^\.env$|^\.env\.local$"
```

Se não estiver, adicione:

```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## 📦 Configuração no Servidor de Produção

No servidor (`srv1037558.hstgr.cloud`), você precisa criar o `.env` também:

```bash
# SSH no servidor
ssh lelo@srv1037558.hstgr.cloud

# Criar .env
cd /var/www/conectades-dev
nano .env

# Cole as configurações (use as mesmas do local):
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
DEFAULT_FROM_EMAIL=noreply@conectades.com
SERVER_EMAIL=admin@conectades.com
SITE_URL=http://srv1037558.hstgr.cloud:8001
FRONTEND_URL=http://seu-frontend.com

# Salvar (Ctrl+O, Enter, Ctrl+X)

# Definir permissões seguras
chmod 600 .env

# Reiniciar container
docker compose restart web
```

---

## 📚 Referências

- **Google App Passwords:** https://myaccount.google.com/apppasswords
- **Gmail SMTP Settings:** https://support.google.com/a/answer/176600
- **Django Email Backend:** https://docs.djangoproject.com/en/4.2/topics/email/

---

## 📞 Suporte

Se ainda tiver problemas após seguir este guia:

1. Execute o script de teste: `python test_email.py`
2. Copie a mensagem de erro completa
3. Verifique o checklist acima
4. Compartilhe o erro (sem a senha!) para análise

---

**Documentação atualizada em:** 2025-11-03

