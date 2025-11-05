# 🔒 Segurança: CSRF e APIs REST

## 🎯 Solução Implementada

Foi criado um **middleware customizado** para desabilitar verificação CSRF apenas para endpoints da API REST (`/api/*`), mantendo a proteção ativa para o Django Admin.

---

## 📋 O que é CSRF?

**CSRF (Cross-Site Request Forgery)** é um ataque onde um site malicioso engana o navegador do usuário a fazer requisições não autorizadas para outro site onde o usuário está autenticado.

**Exemplo:**
```
Usuário está logado no admin do site A.
Site malicioso B faz o navegador enviar um POST para site A.
Como o navegador envia cookies automaticamente, a requisição parece legítima.
```

---

## 🔐 Por que CSRF é Importante?

### **CSRF é necessário para:**
- ✅ **Formulários web tradicionais** (Django Admin, formulários HTML)
- ✅ **Requisições baseadas em sessão/cookies**
- ✅ **Aplicações web server-side rendering**

### **CSRF NÃO é necessário para:**
- ❌ **APIs REST com JWT/Token** (não usam cookies)
- ❌ **APIs stateless** (cada requisição é independente)
- ❌ **Aplicações SPA** (React, Vue, Angular) que consomem APIs

---

## ⚙️ Implementação

### **Arquivo:** `backend/core/middleware.py`

```python
class DisableCSRFForAPI(MiddlewareMixin):
    """
    Desabilita verificação CSRF apenas para endpoints da API (/api/*).
    
    Isso permite que:
    - APIs REST funcionem sem CSRF token (padrão para APIs)
    - Django Admin continue protegido com CSRF
    - Swagger UI funcione sem problemas
    """
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
```

### **Configuração:** `backend/core/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'backend.core.middleware.DisableCSRFForAPI',  # 👈 ANTES do CsrfViewMiddleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ...
]
```

**⚠️ IMPORTANTE:** O middleware `DisableCSRFForAPI` deve vir **ANTES** de `CsrfViewMiddleware` para funcionar!

---

## 🔍 Como Funciona?

### **1. Requisição para `/api/*`:**
```
Requisição → DisableCSRFForAPI → marca como isenta
           → CsrfViewMiddleware → vê que está isenta, não verifica
           → View processa normalmente ✅
```

### **2. Requisição para `/admin/*`:**
```
Requisição → DisableCSRFForAPI → não marca (não é /api/)
           → CsrfViewMiddleware → verifica CSRF token
           → Se token válido: processa ✅
           → Se token inválido: retorna 403 ❌
```

---

## ✅ Benefícios desta Abordagem

### **1. Segurança Mantida:**
- ✅ Django Admin **continua protegido** com CSRF
- ✅ Formulários web tradicionais continuam protegidos
- ✅ Apenas APIs REST são isentas (que já usam JWT)

### **2. Compatibilidade:**
- ✅ Swagger UI funciona sem problemas
- ✅ APIs REST seguem padrão da indústria (stateless, sem CSRF)
- ✅ Frontend (React, Vue, etc.) pode consumir a API facilmente

### **3. Flexibilidade:**
- ✅ Fácil de desabilitar (remover middleware)
- ✅ Pode ser ajustado para proteger endpoints específicos
- ✅ Não afeta outras proteções (CORS, JWT, permissões)

---

## 🧪 Testando

### **1. Testar API (deve funcionar SEM CSRF):**

```bash
curl -X POST "http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "nome_completo": "Teste API"
  }'
```

**Resultado esperado:** ✅ `200 OK` (email enviado)

---

### **2. Testar Django Admin (deve exigir CSRF):**

1. Acesse: `http://srv1037558.hstgr.cloud:8001/admin/`
2. Faça login
3. Tente criar/editar algo
4. ✅ Deve funcionar normalmente (com CSRF token)

Se tentar fazer POST sem CSRF token no admin, deve retornar **403 Forbidden**.

---

### **3. Testar Swagger UI:**

1. Acesse: `http://srv1037558.hstgr.cloud:8001/api/docs/`
2. Teste qualquer endpoint POST
3. ✅ Deve funcionar sem erro de CSRF

---

## 🔒 Outras Proteções Ativas

Mesmo sem CSRF nas APIs, o sistema ainda tem múltiplas camadas de segurança:

### **1. JWT Authentication:**
```python
# Endpoints protegidos requerem token JWT
Authorization: Bearer <token>
```

### **2. CORS (Cross-Origin Resource Sharing):**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://srv1037558.hstgr.cloud:8001',
    # Apenas origens específicas
]
```

### **3. Permissões DRF:**
```python
@permission_classes([IsAuthenticated])
# Só usuários autenticados podem acessar
```

### **4. Rate Limiting (Futuro):**
```python
# Limitar número de requisições por IP/usuário
```

---

## 📊 Matriz de Proteção

| Endpoint | CSRF | JWT | Permissões | CORS |
|----------|------|-----|------------|------|
| `/api/auth/registro/` | ❌ | ❌ | Público | ✅ |
| `/api/auth/login/` | ❌ | ❌ | Público | ✅ |
| `/api/pessoas/perfil/` | ❌ | ✅ | Autenticado | ✅ |
| `/api/campanhas/criar/` | ❌ | ✅ | Autenticado | ✅ |
| `/admin/*` | ✅ | ❌ | Session | ✅ |

---

## 🚨 Quando Usar CSRF?

### **USE CSRF para:**
- ✅ Formulários HTML tradicionais
- ✅ Django Admin
- ✅ Aplicações web com sessão/cookies
- ✅ Server-side rendering (SSR)

### **NÃO USE CSRF para:**
- ❌ APIs REST stateless
- ❌ APIs com JWT/Token authentication
- ❌ SPAs (Single Page Applications)
- ❌ Mobile apps que consomem APIs

---

## 🔧 Troubleshooting

### **Erro: CSRF token missing or incorrect**

**Causa:** O middleware não está funcionando corretamente.

**Solução:**
```bash
# 1. Verificar ordem dos middlewares em settings.py
# DisableCSRFForAPI deve vir ANTES de CsrfViewMiddleware

# 2. Reiniciar servidor
docker compose restart web

# 3. Verificar logs
docker compose logs web | grep -i csrf
```

---

### **Django Admin não funciona**

**Causa:** O middleware está desabilitando CSRF para todos os endpoints.

**Solução:** Verifique que a condição é `request.path.startswith('/api/')` (não `/`).

---

## 📚 Referências

- [Django CSRF Documentation](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [OWASP CSRF](https://owasp.org/www-community/attacks/csrf)

---

## ✅ Checklist de Segurança

Após implementar esta solução:

- [x] APIs REST funcionam sem CSRF
- [x] Django Admin continua protegido
- [x] Swagger UI funciona sem erros
- [x] JWT authentication ativo para endpoints protegidos
- [x] CORS configurado corretamente
- [x] Documentação atualizada

---

## 🎉 Conclusão

Esta implementação segue as **melhores práticas da indústria**:
- ✅ APIs REST não usam CSRF (padrão)
- ✅ Admin web continua protegido
- ✅ Múltiplas camadas de segurança (JWT + CORS + Permissões)
- ✅ Código limpo e manutenível
- ✅ Compatível com frontend moderno (React, Vue, Angular)

**Segurança é um equilíbrio entre proteção e usabilidade!** 🔒✨

