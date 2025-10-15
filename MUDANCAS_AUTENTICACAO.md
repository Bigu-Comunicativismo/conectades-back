# 🔐 Mudanças no Sistema de Autenticação

## ✅ **Problemas Corrigidos**

### **Antes (❌ Problemas):**
1. ❌ APIs de cadastro exigiam token JWT para se cadastrar
2. ❌ Não era possível criar conta sem estar logado (paradoxo)
3. ❌ Sem verificação de email
4. ❌ Sem sistema de código de verificação

### **Agora (✅ Corrigido):**
1. ✅ APIs de cadastro são **públicas** (sem token)
2. ✅ Login é **público** (sem token)
3. ✅ Verificação por **código de email** (6 dígitos)
4. ✅ Sistema de 2FA (Two-Factor Authentication)
5. ✅ Códigos expiram em 10 minutos
6. ✅ Máximo 3 tentativas por código

---

## 🆕 **Novos Endpoints PÚBLICOS**

Todos esses endpoints **NÃO REQUEREM** autenticação:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/auth/opcoes/` | Lista opções de cadastro |
| POST | `/api/auth/registro/iniciar/` | Etapa 1: Envia código por email |
| POST | `/api/auth/registro/confirmar/` | Etapa 2: Confirma código e cria conta |
| POST | `/api/auth/login/` | Login com email + senha |
| POST | `/api/auth/senha/recuperar/` | Etapa 1: Solicita recuperação (envia código) |
| POST | `/api/auth/senha/redefinir/` | Etapa 2: Redefine senha (verifica código) |
| POST | `/api/auth/codigo/solicitar/` | Solicita novo código |
| POST | `/api/auth/codigo/verificar/` | Verifica se código é válido |

---

## 🚀 **Fluxo de Cadastro (2 Etapas)**

### **1️⃣ Iniciar Registro**
```bash
POST /api/auth/registro/iniciar/

{
  "email": "maria@example.com",
  "username": "maria",
  "password": "Senha123!",
  "nome_completo": "Maria Silva",
  "cpf": "123.456.789-00",
  "telefone": "(81) 98765-4321",
  "tipo_usuario": 1,
  "genero": 1,
  "cidade": "Recife",
  "bairro": "Boa Viagem",
  "nome_social": "Maria",
  "mini_bio": "Olá!",
  "categorias_interesse": [1, 2],
  "localizacoes_interesse": [5]
}
```

**Resposta:**
```json
{
  "message": "Código de verificação enviado para seu email",
  "email": "maria@example.com",
  "validade": "10 minutos"
}
```

### **2️⃣ Confirmar com Código**
```bash
POST /api/auth/registro/confirmar/

{
  "email": "maria@example.com",
  "codigo": "123456"
}
```

**Resposta:**
```json
{
  "message": "🎉 Conta criada com sucesso!",
  "user": { ... },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

---

## 🔐 **Login**

```bash
POST /api/auth/login/

{
  "email": "maria@example.com",
  "password": "Senha123!"
}
```

**Resposta:**
```json
{
  "message": "Bem-vinda de volta, Maria!",
  "user": { ... },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

---

## 🔑 **Recuperação de Senha (2 Etapas)**

### **1️⃣ Solicitar Recuperação**
```bash
POST /api/auth/senha/recuperar/

{
  "email": "maria@example.com"
}
```

**Resposta:**
```json
{
  "message": "Código de recuperação enviado para seu email",
  "email": "maria@example.com",
  "validade": "10 minutos"
}
```

### **2️⃣ Redefinir com Código**
```bash
POST /api/auth/senha/redefinir/

{
  "email": "maria@example.com",
  "codigo": "654321",
  "nova_senha": "NovaSenha123!",
  "confirmar_senha": "NovaSenha123!"
}
```

**Resposta:**
```json
{
  "message": "✅ Senha redefinida com sucesso!",
  "user": { ... },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

**Observação:** Após redefinir a senha, você recebe tokens JWT para login automático!

---

## 📧 **Como Funciona o Email**

### **Em Desenvolvimento:**
- Emails aparecem no **console do Docker**
- Não são enviados para email real
- Ideal para testes locais

```bash
# Ver emails no console
docker-compose logs -f web
```

### **Em Produção:**
Editar `backend/core/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
```

---

## 🛡️ **Segurança**

✅ **Códigos únicos** - Gerados aleatoriamente (6 dígitos)  
✅ **Tempo de expiração** - 10 minutos  
✅ **Limite de tentativas** - Máximo 3 tentativas  
✅ **Uso único** - Código não pode ser reutilizado  
✅ **Invalidação automática** - Novo código invalida o anterior  
✅ **Limpeza automática** - Códigos >24h são removidos  

---

## 📊 **Admin Django**

Novos recursos no admin:

**URL:** http://localhost/admin/pessoas/codigoverificacao/

- ✅ Ver todos os códigos gerados
- ✅ Filtrar por tipo/status
- ✅ Ver tentativas de uso
- ✅ Marcar como usado
- ✅ Limpar códigos expirados

---

## 🔄 **Mudanças nas Rotas**

### **Antes:**
- `/api/cadastro/` - Exigia autenticação ❌

### **Agora:**
- `/api/auth/` - Endpoints públicos ✅

---

## ✨ **Novos Arquivos Criados**

1. `backend/pessoas/models.py` - Modelo `CodigoVerificacao`
2. `backend/pessoas/email_service.py` - Serviço de envio de email
3. `backend/pessoas/views.py` - Reescrito com endpoints públicos
4. `backend/pessoas/serializers.py` - Novos serializers
5. `backend/pessoas/admin.py` - Admin de `CodigoVerificacao`
6. `docs/FLUXO_AUTENTICACAO.md` - Documentação completa

---

## 📚 **Documentação**

- 📘 [Fluxo Completo de Autenticação](docs/FLUXO_AUTENTICACAO.md)
- 🧪 [Testes com Postman/Insomnia](docs/TESTES_INSOMNIA_POSTMAN.md)

---

## 🎯 **Resumo**

| Antes | Agora |
|-------|-------|
| ❌ Cadastro exigia token | ✅ Cadastro público |
| ❌ Login exigia token | ✅ Login público |
| ❌ Sem verificação de email | ✅ Código por email |
| ❌ Sem 2FA | ✅ Sistema 2FA |
| ❌ Rotas em `/api/cadastro/` | ✅ Rotas em `/api/auth/` |

---

**🎉 Sistema totalmente funcional e pronto para uso!**

