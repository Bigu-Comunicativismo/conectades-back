# 🐛 Debug: Email SMTP Não Está Enviando

## 🚨 Problema

Usuário é cadastrado no Django Admin, mas **o email de verificação não chega** (nem no spam).

---

## ✅ Checklist de Diagnóstico

### **1. Verificar Configurações do `.env` no Servidor**

SSH no servidor:
```bash
ssh lelo@srv1037558.hstgr.cloud
cd /var/www/conectades-dev
cat .env
```

**Verifique se está assim:**
```bash
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=contato@bigu.org.br
EMAIL_HOST_PASSWORD=jgvruoezudcvkuwt
DEFAULT_FROM_EMAIL=contato@bigu.org.br
SITE_URL=http://srv1037558.hstgr.cloud:8001
```

⚠️ **IMPORTANTE:** 
- `EMAIL_BACKEND=smtp` (não `console` ou `file`)
- `EMAIL_HOST_PASSWORD` deve ser uma **senha de app do Gmail** (não a senha normal)

---

### **2. Testar SMTP com Script**

Execute o script de teste no container:

```bash
cd /var/www/conectades-dev
docker compose exec web python test_smtp_vps.py
```

**O que o script faz:**
- ✅ Verifica se `EMAIL_BACKEND=smtp`
- ✅ Verifica se credenciais estão definidas
- ✅ Tenta enviar um email de teste
- ✅ Mostra erros detalhados se falhar

---

### **3. Verificar Logs do Container**

```bash
cd /var/www/conectades-dev
docker compose logs web | grep -i mail
docker compose logs web | grep -i email
docker compose logs web | grep -i smtp
```

**Procure por:**
- ❌ Erros de autenticação: `Authentication failed`
- ❌ Timeout de conexão: `Connection timed out`
- ❌ Senha incorreta: `Username and Password not accepted`

---

### **4. Verificar se o Django Está Lendo o `.env`**

Execute no container:

```bash
docker compose exec web python -c "
import os
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
django.setup()

print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_HOST:', settings.EMAIL_HOST)
print('EMAIL_HOST_USER:', settings.EMAIL_HOST_USER)
print('EMAIL_HOST_PASSWORD:', '*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'VAZIO')
print('DEFAULT_FROM_EMAIL:', settings.DEFAULT_FROM_EMAIL)
"
```

**Saída esperada:**
```
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST: smtp.gmail.com
EMAIL_HOST_USER: contato@bigu.org.br
EMAIL_HOST_PASSWORD: ****************
DEFAULT_FROM_EMAIL: contato@bigu.org.br
```

---

### **5. Testar Manualmente no Shell do Django**

```bash
docker compose exec web python backend/manage.py shell
```

Dentro do shell:

```python
from django.core.mail import send_mail
from django.conf import settings

# Verificar configurações
print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)
print("EMAIL_HOST:", settings.EMAIL_HOST)
print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)

# Tentar enviar email
try:
    send_mail(
        subject='Teste Manual SMTP',
        message='Este é um teste manual do Django shell.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['contato@bigu.org.br'],
        fail_silently=False,
    )
    print("✅ Email enviado com sucesso!")
except Exception as e:
    print("❌ Erro:", e)
```

---

### **6. Verificar Firewall e Porta 587**

Teste se a porta 587 (SMTP do Gmail) está acessível:

```bash
telnet smtp.gmail.com 587
```

**Saída esperada:**
```
Trying 142.250.xxx.xxx...
Connected to smtp.gmail.com.
Escape character is '^]'.
220 smtp.google.com ESMTP ...
```

Se **não conectar**, o firewall pode estar bloqueando.

**Solução:**
```bash
sudo ufw allow out 587/tcp
```

---

## 🔧 Soluções Comuns

### **Problema 1: `EMAIL_BACKEND=console`**

**Sintoma:** Emails aparecem no log do container, mas não são enviados.

**Solução:**
```bash
# Editar .env no servidor
EMAIL_BACKEND=smtp
```

```bash
# Reiniciar container
docker compose restart web
```

---

### **Problema 2: Senha do Gmail Incorreta**

**Sintoma:** Erro `Username and Password not accepted`

**Solução:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma **nova senha de app**
3. Atualize no `.env`:
   ```bash
   EMAIL_HOST_PASSWORD=nova_senha_app_aqui
   ```
4. Reinicie: `docker compose restart web`

---

### **Problema 3: `.env` Não Está Sendo Lido**

**Sintoma:** Configurações não mudam mesmo editando `.env`

**Solução:**
```bash
# Parar container
docker compose down

# Rebuild forçado
docker compose build --no-cache web

# Subir novamente
docker compose up -d
```

---

### **Problema 4: Gmail Bloqueou o Acesso**

**Sintoma:** Erro `Less secure app access`

**Solução:**
- ✅ Use **senha de app** (não a senha normal)
- ✅ Ative **verificação em 2 etapas**
- ✅ Gere senha de app em: https://myaccount.google.com/apppasswords

---

### **Problema 5: Variável de Ambiente com Espaço ou Aspas**

**ERRADO:**
```bash
EMAIL_HOST_USER = "contato@bigu.org.br"
EMAIL_HOST_PASSWORD = "jgvruoezudcvkuwt"
```

**CORRETO:**
```bash
EMAIL_HOST_USER=contato@bigu.org.br
EMAIL_HOST_PASSWORD=jgvruoezudcvkuwt
```

---

## 🧪 Teste Completo de Cadastro

### **1. Criar um usuário via API:**

```bash
curl -X POST http://srv1037558.hstgr.cloud:8001/api/pessoas/registro/iniciar/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "nome_completo": "Teste SMTP"
  }'
```

**Resposta esperada:**
```json
{
  "message": "Link de ativação enviado para seu email",
  "email": "teste@exemplo.com"
}
```

---

### **2. Verificar logs do envio:**

```bash
docker compose logs web --tail=50 | grep -E "(mail|email|smtp)" -i
```

**Procure por:**
- ✅ `Email enviado` (sucesso)
- ❌ `SMTPAuthenticationError` (senha incorreta)
- ❌ `ConnectionRefusedError` (porta bloqueada)
- ❌ `SMTPServerDisconnected` (timeout)

---

### **3. Verificar banco de dados:**

```bash
docker compose exec web python backend/manage.py shell
```

```python
from backend.pessoas.models import CodigoVerificacao

# Verificar códigos gerados
codigos = CodigoVerificacao.objects.filter(email='teste@exemplo.com')
for codigo in codigos:
    print(f"Código: {codigo.codigo}")
    print(f"Token: {codigo.token}")
    print(f"Criado: {codigo.data_criacao}")
    print(f"Usado: {codigo.usado}")
```

Se o código foi gerado mas o email não chegou, o problema é no SMTP.

---

## 📊 Análise de Logs Detalhada

### **Logs do Django:**

```bash
docker compose logs web -f
```

**O que procurar:**
```
⚠️  EMAIL_BACKEND está configurado como 'smtp', mas EMAIL_HOST_USER ou EMAIL_HOST_PASSWORD não foram definidos.
```

Se aparecer este aviso, as credenciais não estão sendo lidas!

---

### **Logs do SMTP (verbose):**

Ative debug SMTP temporariamente em `settings.py`:

```python
EMAIL_DEBUG = True
```

Ou adicione no `.env`:
```bash
DJANGO_LOG_LEVEL=DEBUG
```

Reinicie e veja logs detalhados:
```bash
docker compose restart web
docker compose logs web -f
```

---

## 🎯 Checklist Final

Antes de testar novamente, confirme:

- [ ] `.env` existe em `/var/www/conectades-dev/`
- [ ] `EMAIL_BACKEND=smtp` (sem aspas, sem espaços)
- [ ] `EMAIL_HOST_USER=contato@bigu.org.br` (sem aspas)
- [ ] `EMAIL_HOST_PASSWORD=jgvruoezudcvkuwt` (senha de app do Gmail)
- [ ] Container foi reiniciado: `docker compose restart web`
- [ ] Porta 587 está acessível: `telnet smtp.gmail.com 587`
- [ ] Script de teste executou: `docker compose exec web python test_smtp_vps.py`
- [ ] Logs não mostram erros: `docker compose logs web | grep -i error`

---

## 🔍 Script de Diagnóstico Automático

Execute tudo de uma vez:

```bash
cd /var/www/conectades-dev

echo "1️⃣  Verificando .env..."
cat .env | grep EMAIL

echo ""
echo "2️⃣  Verificando se Django lê as configs..."
docker compose exec -T web python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
django.setup()
from django.conf import settings
print('Backend:', settings.EMAIL_BACKEND)
print('Host:', settings.EMAIL_HOST)
print('User:', settings.EMAIL_HOST_USER)
print('Password:', 'OK' if settings.EMAIL_HOST_PASSWORD else 'VAZIO')
"

echo ""
echo "3️⃣  Testando conexão SMTP..."
timeout 5 telnet smtp.gmail.com 587 < /dev/null

echo ""
echo "4️⃣  Executando teste de envio..."
docker compose exec -T web python test_smtp_vps.py

echo ""
echo "5️⃣  Verificando logs de erro..."
docker compose logs web --tail=20 | grep -i error
```

---

## 📞 Suporte

Se nada funcionar, forneça:

1. **Saída do script de teste:** `docker compose exec web python test_smtp_vps.py`
2. **Logs recentes:** `docker compose logs web --tail=100`
3. **Configurações (sem senha):** `cat .env | grep EMAIL | sed 's/PASSWORD=.*/PASSWORD=***/'`

---

## ✅ Resultado Esperado

Quando tudo estiver funcionando:

```
✅ EMAIL ENVIADO COM SUCESSO!

🔍 PRÓXIMOS PASSOS:
   1. Verifique a caixa de entrada de: contato@bigu.org.br
   2. Se não encontrar, verifique a pasta de SPAM
   3. Aguarde até 2 minutos (atraso normal de SMTP)
```

E o usuário deve receber o email! 📧✨

