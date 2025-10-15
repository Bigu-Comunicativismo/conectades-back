# 🔐 Fluxo de Autenticação com Código de Email

Sistema de autenticação em 2 fatores com verificação por email.

---

## 📋 **Sumário**

1. [Cadastro (Registro)](#cadastro-registro)
2. [Login](#login)
3. [Recuperação de Senha](#recuperação-de-senha)
4. [Endpoints Públicos](#endpoints-públicos)
5. [Endpoints Protegidos](#endpoints-protegidos)
6. [Exemplos de Uso](#exemplos-de-uso)

---

## 🆕 **Cadastro (Registro)**

### **Fluxo em 2 Etapas:**

```mermaid
sequenceDiagram
    User->>API: 1️⃣ POST /api/auth/registro/iniciar/
    API->>Validação: Valida dados
    API->>Email: Envia código (123456)
    API-->>User: ✅ Código enviado
    User->>API: 2️⃣ POST /api/auth/registro/confirmar/
    API->>Validação: Verifica código
    API->>DB: Cria conta
    API-->>User: ✅ Conta criada + JWT tokens
```

### **1️⃣ Etapa 1: Iniciar Registro**

**Endpoint:** `POST /api/auth/registro/iniciar/`  
**Autenticação:** ❌ **Pública** (não requer token)

**Body (JSON):**
```json
{
  "email": "maria@example.com",
  "username": "maria_silva",
  "password": "SenhaForte123!",
  "nome_completo": "Maria Silva",
  "cpf": "123.456.789-00",
  "telefone": "(81) 98765-4321",
  "tipo_usuario": 1,
  "genero": 1,
  "cidade": "Recife",
  "bairro": "Boa Viagem",
  "nome_social": "Maria",
  "mini_bio": "Apaixonada por ajudar o próximo",
  "categorias_interesse": [1, 2, 3],
  "localizacoes_interesse": [5, 10]
}
```

**Resposta (200 OK):**
```json
{
  "message": "Código de verificação enviado para seu email",
  "email": "maria@example.com",
  "validade": "10 minutos",
  "proximo_passo": "Use o endpoint /api/auth/confirmar-registro/ com o código recebido"
}
```

### **2️⃣ Etapa 2: Confirmar Registro**

**Endpoint:** `POST /api/auth/registro/confirmar/`  
**Autenticação:** ❌ **Pública** (não requer token)

**Body (JSON):**
```json
{
  "email": "maria@example.com",
  "codigo": "123456"
}
```

**Resposta (201 Created):**
```json
{
  "message": "🎉 Conta criada com sucesso! Bem-vinda, Maria!",
  "user": {
    "id": 5,
    "username": "maria_silva",
    "nome_completo": "Maria Silva",
    "email": "maria@example.com",
    "nome_social": "Maria",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 🔐 **Login**

### **Login Simples (Email + Senha)**

**Endpoint:** `POST /api/auth/login/`  
**Autenticação:** ❌ **Pública** (não requer token)

**Body (JSON):**
```json
{
  "email": "maria@example.com",
  "password": "SenhaForte123!"
}
```

**Resposta (200 OK):**
```json
{
  "message": "Bem-vinda de volta, Maria!",
  "user": {
    "id": 5,
    "username": "maria_silva",
    "nome_completo": "Maria Silva",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 🔑 **Recuperação de Senha**

### **Fluxo em 2 Etapas:**

```mermaid
sequenceDiagram
    User->>API: 1️⃣ POST /api/auth/senha/recuperar/
    API->>Validação: Verifica se email existe
    API->>Email: Envia código (654321)
    API-->>User: ✅ Código enviado
    User->>API: 2️⃣ POST /api/auth/senha/redefinir/
    API->>Validação: Verifica código
    API->>DB: Atualiza senha
    API-->>User: ✅ Senha redefinida + JWT tokens
```

### **1️⃣ Etapa 1: Solicitar Recuperação**

**Endpoint:** `POST /api/auth/senha/recuperar/`  
**Autenticação:** ❌ **Pública** (não requer token)

**Body (JSON):**
```json
{
  "email": "maria@example.com"
}
```

**Resposta (200 OK):**
```json
{
  "message": "Código de recuperação enviado para seu email",
  "email": "maria@example.com",
  "validade": "10 minutos",
  "proximo_passo": "Use o endpoint /api/auth/senha/redefinir/ com o código recebido"
}
```

### **2️⃣ Etapa 2: Redefinir Senha**

**Endpoint:** `POST /api/auth/senha/redefinir/`  
**Autenticação:** ❌ **Pública** (não requer token)

**Body (JSON):**
```json
{
  "email": "maria@example.com",
  "codigo": "654321",
  "nova_senha": "NovaSenha123!",
  "confirmar_senha": "NovaSenha123!"
}
```

**Resposta (200 OK):**
```json
{
  "message": "✅ Senha redefinida com sucesso! Você já está logada, Maria!",
  "user": {
    "id": 5,
    "username": "maria_silva",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

## 🌐 **Endpoints Públicos**

Todos esses endpoints **NÃO REQUEREM** token JWT:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/auth/opcoes/` | Lista opções de cadastro (tipos, gêneros, etc) |
| POST | `/api/auth/registro/iniciar/` | Inicia registro (envia código) |
| POST | `/api/auth/registro/confirmar/` | Confirma registro (verifica código) |
| POST | `/api/auth/login/` | Login (retorna JWT) |
| POST | `/api/auth/senha/recuperar/` | Solicita recuperação de senha (envia código) |
| POST | `/api/auth/senha/redefinir/` | Redefine senha (verifica código e atualiza) |
| POST | `/api/auth/codigo/solicitar/` | Solicita novo código |
| POST | `/api/auth/codigo/verificar/` | Verifica código |

---

## 🔒 **Endpoints Protegidos**

Esses endpoints **REQUEREM** token JWT no header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/auth/perfil/` | Ver meu perfil |
| PUT/PATCH | `/api/auth/perfil/atualizar/` | Atualizar meu perfil |

---

## 📝 **Exemplos de Uso**

### **Exemplo 1: Cadastro Completo**

```bash
# 1. Listar opções disponíveis
curl -X GET http://localhost/api/auth/opcoes/

# 2. Iniciar registro
curl -X POST http://localhost/api/auth/registro/iniciar/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joana@example.com",
    "username": "joana",
    "password": "Senha123!",
    "nome_completo": "Joana Santos",
    "cpf": "111.222.333-44",
    "telefone": "(81) 91234-5678",
    "tipo_usuario": 1,
    "genero": 1,
    "cidade": "Recife",
    "bairro": "Boa Viagem",
    "nome_social": "Joana",
    "mini_bio": "Olá!"
  }'

# Você receberá um código no email (em dev, aparece no console do Docker)

# 3. Confirmar com código
curl -X POST http://localhost/api/auth/registro/confirmar/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joana@example.com",
    "codigo": "123456"
  }'

# Resposta terá os tokens JWT
```

### **Exemplo 2: Login**

```bash
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joana@example.com",
    "password": "Senha123!"
  }'
```

### **Exemplo 3: Recuperação de Senha**

```bash
# 1. Solicitar recuperação de senha
curl -X POST http://localhost/api/auth/senha/recuperar/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joana@example.com"
  }'

# Você receberá um código no email (em dev, aparece no console do Docker)

# 2. Redefinir senha com código
curl -X POST http://localhost/api/auth/senha/redefinir/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joana@example.com",
    "codigo": "654321",
    "nova_senha": "NovaSenhaSegura456!",
    "confirmar_senha": "NovaSenhaSegura456!"
  }'

# Resposta terá os tokens JWT (login automático após redefinir senha)
```

### **Exemplo 4: Acessar Perfil (Com Token)**

```bash
# Primeiro, faça login e pegue o token access
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Use o token para acessar endpoint protegido
curl -X GET http://localhost/api/auth/perfil/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔄 **Fluxo de Refresh Token**

Quando o access token expirar (após 1 hora):

```bash
curl -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

## ⚙️ **Configuração de Email**

### **Desenvolvimento (Padrão)**

Por padrão, os emails são exibidos no **console do Docker**:

```bash
# Ver emails enviados
docker-compose logs -f web
```

### **Produção (SMTP Real)**

Edite `backend/core/settings.py`:

```python
# Trocar para SMTP real
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
```

---

## 🛡️ **Segurança**

### **Proteções Implementadas:**

✅ **Códigos com tempo de vida** - Expiram em 10 minutos  
✅ **Limite de tentativas** - Máximo 3 tentativas por código  
✅ **Uso único** - Código não pode ser reutilizado  
✅ **Invalidação automática** - Códigos antigos são invalidados ao gerar novo  
✅ **Limpeza automática** - Códigos com +24h são removidos  

### **Validações:**

- ✅ Email único
- ✅ Username único  
- ✅ CPF único e validado
- ✅ Senha forte (mínimo 8 caracteres)
- ✅ Telefone validado

---

## 🐛 **Troubleshooting**

### **Código não chegou?**

1. Em **desenvolvimento**, o código aparece nos logs:
   ```bash
   docker-compose logs -f web
   ```

2. Verifique se o email está correto

3. Solicite um novo código:
   ```bash
   curl -X POST http://localhost/api/auth/codigo/solicitar/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "seu-email@example.com",
       "tipo": "cadastro"
     }'
   ```

### **Código expirado?**

Solicite um novo código (o anterior será invalidado automaticamente).

### **Muitas tentativas?**

Aguarde 10 minutos ou solicite um novo código.

---

## 📊 **Admin Django**

Visualize os códigos gerados em:

**URL:** http://localhost/admin/pessoas/codigoverificacao/

**Funcionalidades:**
- ✅ Ver todos os códigos
- ✅ Filtrar por tipo/status
- ✅ Marcar como usado
- ✅ Limpar códigos expirados

---

## 🎯 **Resumo**

| Ação | Endpoint | Auth |
|------|----------|------|
| **Ver opções** | GET `/api/auth/opcoes/` | ❌ Pública |
| **Iniciar cadastro** | POST `/api/auth/registro/iniciar/` | ❌ Pública |
| **Confirmar cadastro** | POST `/api/auth/registro/confirmar/` | ❌ Pública |
| **Login** | POST `/api/auth/login/` | ❌ Pública |
| **Recuperar senha** | POST `/api/auth/senha/recuperar/` | ❌ Pública |
| **Redefinir senha** | POST `/api/auth/senha/redefinir/` | ❌ Pública |
| **Refresh token** | POST `/api/token/refresh/` | ❌ Pública |
| **Ver perfil** | GET `/api/auth/perfil/` | ✅ JWT |
| **Atualizar perfil** | PUT `/api/auth/perfil/atualizar/` | ✅ JWT |

---

**✨ Sistema totalmente funcional e seguro!**

