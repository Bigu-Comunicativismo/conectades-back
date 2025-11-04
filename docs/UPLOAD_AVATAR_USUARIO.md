# 📸 Upload de Avatar no Cadastro de Usuário

## 🎯 Objetivo

Permitir que usuários enviem uma foto de perfil (avatar) durante o cadastro ou ao atualizar o perfil.

---

## ✅ O que foi alterado

### 1. **Serializer** (`backend/pessoas/serializers.py`)

```python
# Campo avatar configurado como ImageField
avatar = serializers.ImageField(
    required=False,  # Opcional no cadastro
    help_text="Foto de perfil"
)
```

### 2. **View de Cadastro** (`backend/pessoas/views.py`)

```python
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])  # ✅ Aceita multipart
@permission_classes([AllowAny])
def iniciar_registro(request):
    # ...
```

### 3. **View de Atualização de Perfil**

```python
@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser, JSONParser])  # ✅ Aceita multipart
@permission_classes([IsAuthenticated])
def atualizar_perfil(request):
    # ...
```

---

## 📋 Como Usar no Swagger UI

### **1. Cadastro de Usuário (`POST /api/auth/registro/`)**

1. Abra o Swagger em: `http://srv1037558.hstgr.cloud:8001/api/docs/`
2. Vá para o endpoint `POST /api/auth/registro/`
3. Clique em **"Try it out"**
4. **IMPORTANTE**: Mude o formato para **`multipart/form-data`**
   - Procure pelo dropdown que está em `application/json`
   - Selecione: **`multipart/form-data`**

5. Preencha os campos:

```
email: usuario@exemplo.com
username: usuario123
password: senhaforte123
nome_completo: Maria Silva
cpf: 123.456.789-00
telefone: (11) 98765-4321
tipo_usuario: 1
genero: 1
cidade: Recife
bairro: Boa Viagem
nome_social: Maria
mini_bio: Desenvolvedora apaixonada por tecnologia
avatar: [Clique em "Choose File" e selecione uma imagem]
```

6. Clique em **"Execute"**

---

## 🧪 Como Testar com cURL

### **Cadastro com Avatar**

```bash
curl -X POST "http://srv1037558.hstgr.cloud:8001/api/auth/registro/" \
  -H "Content-Type: multipart/form-data" \
  -F "email=usuario@exemplo.com" \
  -F "username=usuario123" \
  -F "password=senhaforte123" \
  -F "nome_completo=Maria Silva" \
  -F "cpf=123.456.789-00" \
  -F "telefone=(11) 98765-4321" \
  -F "tipo_usuario=1" \
  -F "genero=1" \
  -F "cidade=Recife" \
  -F "bairro=Boa Viagem" \
  -F "nome_social=Maria" \
  -F "mini_bio=Desenvolvedora apaixonada por tecnologia" \
  -F "avatar=@/caminho/para/foto.jpg"
```

### **Atualizar Avatar do Perfil**

```bash
curl -X PATCH "http://srv1037558.hstgr.cloud:8001/api/auth/perfil/" \
  -H "Authorization: Bearer SEU_TOKEN_JWT_AQUI" \
  -H "Content-Type: multipart/form-data" \
  -F "avatar=@/caminho/para/nova_foto.jpg"
```

---

## 🧪 Como Testar com Python

### **Usando `requests`**

```python
import requests

url = "http://srv1037558.hstgr.cloud:8001/api/auth/registro/"

# Dados do formulário
data = {
    'email': 'usuario@exemplo.com',
    'username': 'usuario123',
    'password': 'senhaforte123',
    'nome_completo': 'Maria Silva',
    'cpf': '123.456.789-00',
    'telefone': '(11) 98765-4321',
    'tipo_usuario': 1,
    'genero': 1,
    'cidade': 'Recife',
    'bairro': 'Boa Viagem',
    'nome_social': 'Maria',
    'mini_bio': 'Desenvolvedora apaixonada por tecnologia',
}

# Arquivo de imagem
files = {
    'avatar': open('foto.jpg', 'rb')
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

---

## 📂 Armazenamento de Arquivos

### **Onde as imagens são salvas?**

- **Local**: `backend/media/avatars/`
- **URL de acesso**: `http://srv1037558.hstgr.cloud:8001/media/avatars/foto.jpg`

### **Configuração no `settings.py`**

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### **Configuração no `urls.py`**

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🔍 Validações

### **Tipos de Arquivo Aceitos**

Por padrão, Django aceita:
- JPG / JPEG
- PNG
- GIF
- WebP

### **Tamanho Máximo**

Configurado em `settings.py`:

```python
# Tamanho máximo do arquivo de upload (2.5MB por padrão)
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
```

---

## ⚠️ Problemas Comuns

### ❌ **Erro: "The submitted data was not a file"**

**Causa**: Request enviado como `application/json` ao invés de `multipart/form-data`

**Solução**:
- No Swagger: Selecione `multipart/form-data` no dropdown
- No cURL: Use `-F` ao invés de `-d`
- No Python: Use `files={}` ao invés de `json={}`

### ❌ **Erro: "avatar field is required"**

**Causa**: Campo `avatar` definido como obrigatório no serializer

**Solução**: Campo já está como `required=False` no `RegistroComCodigoSerializer`

### ❌ **Imagem não carrega no navegador**

**Causa**: Nginx não está servindo arquivos de `/media/`

**Solução**: Verificar configuração do Nginx:

```nginx
location /media/ {
    alias /var/www/conectades-dev/backend/media/;
}
```

---

## 📝 Exemplo de Resposta

### **Sucesso (200)**

```json
{
  "message": "Link de ativação enviado para seu email",
  "email": "usuario@exemplo.com",
  "validade": "24 horas",
  "proximo_passo": "Clique no link enviado para ativar sua conta"
}
```

### **Após Ativação**

```json
{
  "message": "🎉 Conta criada com sucesso! Bem-vinda, Maria!",
  "user": {
    "id": 1,
    "username": "usuario123",
    "email": "usuario@exemplo.com",
    "nome_completo": "Maria Silva",
    "nome_social": "Maria",
    "avatar": "http://srv1037558.hstgr.cloud:8001/media/avatars/usuario123_avatar.jpg",
    "mini_bio": "Desenvolvedora apaixonada por tecnologia",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhb...",
    "access": "eyJ0eXAiOiJKV1QiLCJhb..."
  }
}
```

---

## 🎉 Pronto!

Agora o cadastro aceita upload de avatar via `multipart/form-data`! 📸✨

