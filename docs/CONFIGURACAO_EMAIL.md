# 📧 Configuração de Email no Conectades

## 📋 Status Atual

### **Desenvolvimento (Local)**

**Backend Configurado:** `console` (emails impressos no terminal)

```python
# settings_local.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Comportamento:**
- ✅ Emails são "enviados" mas aparecem apenas no **terminal do servidor**
- ✅ Perfeito para **testes** sem configurar SMTP
- ❌ **NÃO envia emails reais**

**Onde ver os emails:**
```bash
# Terminal onde o servidor está rodando
# Você verá algo como:

Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: 🎯 Nova Solicitação de Campanha - Campanha de Alimentos
From: noreply@conectades.com
To: samc22@gmail.com
Date: Mon, 20 Oct 2025 04:30:00 -0000
Message-ID: <...>

Olá, Samara Costa! 👋

Você recebeu uma nova solicitação para ser beneficiária de uma campanha!

📋 Campanha: Campanha de Alimentos
👤 Organizadora: Maria Silva
...
```

---

## 🔧 Como Configurar Email Real

### **Opção 1: Gmail (Desenvolvimento/Testes)**

#### **1. Criar Senha de App no Gmail**

1. Acesse: https://myaccount.google.com/security
2. Ativar "Verificação em duas etapas"
3. Ir em "Senhas de app"
4. Gerar senha para "Conectades"
5. Copiar a senha gerada (ex: `abcd efgh ijkl mnop`)

#### **2. Configurar Django**

Editar `backend/core/settings_local.py`:

```python
# Configuração de Email (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'  # Seu email do Gmail
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # Senha de app gerada
DEFAULT_FROM_EMAIL = 'Conectades <seu-email@gmail.com>'
SITE_URL = 'http://localhost:8001'
```

#### **3. Testar Envio**

```bash
cd /home/lelo/conectades/backend
source ../venv/bin/activate
PYTHONPATH=/home/lelo/conectades DJANGO_SETTINGS_MODULE=backend.core.settings_local python manage.py shell

# No shell:
from django.core.mail import send_mail
send_mail(
    '🧪 Teste de Email',
    'Este é um email de teste do Conectades!',
    'seu-email@gmail.com',
    ['samc22@gmail.com'],
    fail_silently=False,
)
# Se não der erro, funcionou! Verifique a caixa de entrada
```

---

### **Opção 2: SendGrid (Produção Recomendado)**

#### **Por que SendGrid?**
- ✅ 100 emails/dia grátis
- ✅ Alta taxa de entrega
- ✅ Dashboard com estatísticas
- ✅ API simples

#### **1. Criar Conta SendGrid**

1. Acesse: https://signup.sendgrid.com/
2. Criar conta grátis
3. Verificar email
4. Criar API Key: Settings → API Keys → Create API Key
5. Copiar a API Key (ex: `SG.abc123...`)

#### **2. Instalar Biblioteca**

```bash
cd /home/lelo/conectades
source venv/bin/activate
pip install sendgrid
```

#### **3. Configurar Django**

Editar `backend/core/settings_production.py`:

```python
# Configuração de Email (SendGrid)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # Sempre 'apikey'
EMAIL_HOST_PASSWORD = 'SG.abc123...'  # Sua API Key
DEFAULT_FROM_EMAIL = 'Conectades <noreply@conectades.com>'
SITE_URL = 'https://api.conectades.com'
```

---

### **Opção 3: Mailtrap (Desenvolvimento)**

#### **Por que Mailtrap?**
- ✅ Inbox fake para testes
- ✅ Visualiza emails sem enviar de verdade
- ✅ Perfeito para desenvolvimento

#### **1. Criar Conta**

1. Acesse: https://mailtrap.io/
2. Criar conta grátis
3. Ir em: Inboxes → My Inbox
4. Copiar credenciais SMTP

#### **2. Configurar Django**

```python
# settings_local.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-username-mailtrap'
EMAIL_HOST_PASSWORD = 'sua-senha-mailtrap'
DEFAULT_FROM_EMAIL = 'noreply@conectades.com'
SITE_URL = 'http://localhost:8001'
```

---

## 🧪 Como Testar Agora (Modo Console)

### **1. Criar uma campanha com beneficiária no admin**

```bash
# 1. Abrir navegador
http://localhost:8001/admin/

# 2. Login: samc22 / senha123

# 3. Ir em: Campanhas → Adicionar Campanha

# 4. Preencher:
   - Título: "Teste de Email"
   - Descrição: "Testando notificação"
   - Adicionar itens
   - Beneficiária: Carla Oliveira ou Fernanda Lima

# 5. Salvar
```

### **2. Verificar o terminal do servidor**

**Olhe para o terminal onde o servidor está rodando!**

Você verá algo como:

```
Content-Type: text/plain; charset="utf-8"
Subject: 🎯 Nova Solicitação de Campanha - Teste de Email
From: noreply@conectades.com
To: carla.oliveira@exemplo.com

Olá, Carla Oliveira! 👋

Você recebeu uma nova solicitação para ser beneficiária de uma campanha!

📋 Campanha: Teste de Email
👤 Organizadora: Samara Costa

💬 Mensagem da Organizadora:
A organizadora Samara Costa gostaria de associar você como beneficiária...
```

---

## 📊 Comparação de Backends

| Backend | Uso | Emails Reais? | Configuração | Custo |
|---------|-----|---------------|--------------|-------|
| **Console** | Desenvolvimento | ❌ Não | Nenhuma | Grátis |
| **FileBase** | Desenvolvimento | ❌ Não | Pasta de arquivos | Grátis |
| **Mailtrap** | Desenvolvimento | ❌ Não (inbox fake) | SMTP simples | Grátis |
| **Gmail** | Testes | ✅ Sim | Senha de app | Grátis |
| **SendGrid** | Produção | ✅ Sim | API Key | 100/dia grátis |
| **AWS SES** | Produção | ✅ Sim | AWS credentials | ~$0.10/1000 emails |

---

## 🚀 Recomendação

### **Desenvolvimento/Testes (Agora):**
✅ **Mantenha Console Backend**
- Rápido para testar
- Sem configuração extra
- Emails aparecem no terminal

### **Produção:**
✅ **Use SendGrid ou AWS SES**
- Confiável
- Estatísticas
- Alta taxa de entrega

---

## 📝 Exemplo de Teste

### **Vou criar uma campanha de teste agora para você ver o email!**

Execute este comando em outro terminal (enquanto o servidor roda):

```bash
cd /home/lelo/conectades/backend
source ../venv/bin/activate
PYTHONPATH=/home/lelo/conectades DJANGO_SETTINGS_MODULE=backend.core.settings_local python manage.py shell

# No shell Python:
from backend.campanhas.models import Campanha, Organizadora
from backend.pessoas.models import Pessoa
from datetime import datetime, timedelta

# Buscar organizadora e beneficiária
samara = Pessoa.objects.get(username='samc22')
carla = Pessoa.objects.get(username='carla.oliveira')
org, _ = Organizadora.objects.get_or_create(pessoa=samara, defaults={'ativo': True})

# Criar campanha de teste
campanha = Campanha.objects.create(
    titulo='Teste de Notificação por Email',
    subtitulo='Testando o sistema de emails',
    descricao='Esta é uma campanha de teste para verificar o envio de emails',
    organizadora=org,
    beneficiaria=carla,  # ← Isso dispara o email!
    whatsapp='81987654321',
    data_inicio=datetime.now(),
    prazo=datetime.now() + timedelta(days=30),
    ativa=True
)

print(f'✅ Campanha criada: {campanha.titulo}')
print(f'📧 Email enviado para: {carla.email}')
print(f'\\n⚠️  OLHE O TERMINAL DO SERVIDOR para ver o email!')
```

---

## ✅ **Resumo:**

**Atualmente:** 
- 📺 Emails são **impressos no console do servidor**
- ❌ **NÃO são enviados de verdade**
- ✅ **Perfeito para testes locais**

**Para produção:**
- 📧 Configure **Gmail** (testes) ou **SendGrid** (produção)
- ✅ Emails serão **enviados de verdade**
- 📊 Terá **estatísticas de entrega**

**Onde ver agora:**
- 👀 **Terminal do servidor** (onde você executou `runserver 8001`)
- 🔍 Procure por: `Subject: 🎯 Nova Solicitação`

---

**Quer que eu configure para enviar emails reais via Gmail ou SendGrid?** 🤔

