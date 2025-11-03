# 📸 Como Criar Campanha com Upload de Imagem

## ✅ Correção Implementada

O endpoint `POST /api/campanhas/criar/` agora aceita **upload de arquivo de imagem** usando `multipart/form-data`.

---

## 🔧 Configuração do Endpoint

### Endpoint
```
POST /api/campanhas/criar/
```

### Content-Type
```
multipart/form-data
```

### Autenticação
```
Bearer Token (JWT)
```

---

## 📝 Campos do Formulário

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `titulo` | string | ✅ Sim | Título da campanha |
| `subtitulo` | string | ❌ Não | Subtítulo da campanha |
| `descricao` | string | ✅ Sim | Descrição detalhada |
| `beneficiaria_id` | integer | ❌ Não | ID da beneficiária |
| `imagem` | file | ❌ Não | Arquivo de imagem (PNG, JPG, JPEG, GIF, WEBP) |
| `categorias` | array[integer] | ❌ Não | IDs das categorias |
| `whatsapp` | string | ❌ Não | WhatsApp de contato |
| `localizacao` | integer | ❌ Não | ID da localização |
| `data_inicio` | datetime | ✅ Sim | Data de início (ISO 8601) |
| `prazo` | datetime | ✅ Sim | Data de término (ISO 8601) |
| `ativa` | boolean | ❌ Não | Se a campanha está ativa (default: true) |

---

## 🎯 Exemplos de Uso

### 1️⃣ JavaScript (Fetch API)

```javascript
// Criar FormData com arquivo de imagem
const formData = new FormData();
formData.append('titulo', 'Campanha de Natal');
formData.append('subtitulo', 'Ajude crianças carentes');
formData.append('descricao', 'Descrição completa da campanha...');
formData.append('beneficiaria_id', '5');
formData.append('whatsapp', '5511999999999');
formData.append('localizacao', '3550308'); // São Paulo
formData.append('data_inicio', '2025-11-03T00:00:00Z');
formData.append('prazo', '2025-12-31T23:59:59Z');
formData.append('ativa', 'true');

// Adicionar categorias (enviar como array)
formData.append('categorias', '1');
formData.append('categorias', '2');

// Adicionar arquivo de imagem
const fileInput = document.getElementById('imagem');
formData.append('imagem', fileInput.files[0]);

// Fazer requisição
fetch('http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`, // JWT token
  },
  body: formData // NÃO adicionar Content-Type header (browser faz automaticamente)
})
  .then(res => res.json())
  .then(data => console.log('Campanha criada:', data))
  .catch(err => console.error('Erro:', err));
```

---

### 2️⃣ React (com Axios)

```jsx
import axios from 'axios';

const CriarCampanhaForm = () => {
  const [imagem, setImagem] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('titulo', 'Campanha de Natal');
    formData.append('subtitulo', 'Ajude crianças carentes');
    formData.append('descricao', 'Descrição completa da campanha...');
    formData.append('beneficiaria_id', '5');
    formData.append('whatsapp', '5511999999999');
    formData.append('localizacao', '3550308');
    formData.append('data_inicio', '2025-11-03T00:00:00Z');
    formData.append('prazo', '2025-12-31T23:59:59Z');
    formData.append('ativa', 'true');
    
    // Adicionar categorias
    formData.append('categorias', '1');
    formData.append('categorias', '2');

    // Adicionar imagem se selecionada
    if (imagem) {
      formData.append('imagem', imagem);
    }

    try {
      const response = await axios.post(
        'http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            // NÃO adicionar 'Content-Type': axios faz automaticamente
          }
        }
      );
      console.log('Campanha criada:', response.data);
    } catch (error) {
      console.error('Erro:', error.response?.data || error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImagem(e.target.files[0])}
      />
      {/* Outros campos do formulário */}
      <button type="submit">Criar Campanha</button>
    </form>
  );
};
```

---

### 3️⃣ cURL (Linha de Comando)

```bash
curl -X POST http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/ \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -F "titulo=Campanha de Natal" \
  -F "subtitulo=Ajude crianças carentes" \
  -F "descricao=Descrição completa da campanha..." \
  -F "beneficiaria_id=5" \
  -F "whatsapp=5511999999999" \
  -F "localizacao=3550308" \
  -F "data_inicio=2025-11-03T00:00:00Z" \
  -F "prazo=2025-12-31T23:59:59Z" \
  -F "ativa=true" \
  -F "categorias=1" \
  -F "categorias=2" \
  -F "imagem=@/caminho/para/imagem.jpg"
```

---

### 4️⃣ Python (Requests)

```python
import requests

url = 'http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/'
token = 'SEU_TOKEN_JWT'

headers = {
    'Authorization': f'Bearer {token}'
}

data = {
    'titulo': 'Campanha de Natal',
    'subtitulo': 'Ajude crianças carentes',
    'descricao': 'Descrição completa da campanha...',
    'beneficiaria_id': 5,
    'whatsapp': '5511999999999',
    'localizacao': 3550308,
    'data_inicio': '2025-11-03T00:00:00Z',
    'prazo': '2025-12-31T23:59:59Z',
    'ativa': True,
    'categorias': [1, 2]
}

files = {
    'imagem': open('/caminho/para/imagem.jpg', 'rb')
}

response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())
```

---

### 5️⃣ Swagger UI

1. Acesse: http://srv1037558.hstgr.cloud:8001/api/docs/
2. Procure: `POST /api/campanhas/criar/`
3. Clique **"Try it out"**
4. Clique **"Authorize"** e insira o token JWT
5. Preencha os campos do formulário
6. Clique em **"Choose File"** para selecionar a imagem
7. Clique **"Execute"**

---

## 📤 Resposta de Sucesso (201 Created)

```json
{
  "message": "Campanha \"Campanha de Natal\" criada com sucesso!",
  "data": {
    "id": 42,
    "titulo": "Campanha de Natal",
    "subtitulo": "Ajude crianças carentes",
    "descricao": "Descrição completa da campanha...",
    "organizadora": {
      "id": 10,
      "pessoa": {
        "id": 15,
        "nome_completo": "Maria Silva",
        "email": "maria@example.com"
      }
    },
    "beneficiaria": {
      "id": 5,
      "nome_completo": "Ana Souza"
    },
    "imagem": "http://srv1037558.hstgr.cloud:8001/media/campanhas/imagem_123.jpg",
    "categorias": [1, 2],
    "whatsapp": "5511999999999",
    "localizacao": 3550308,
    "data_inicio": "2025-11-03T00:00:00Z",
    "prazo": "2025-12-31T23:59:59Z",
    "dias_restantes": 58,
    "percentual_atingido": 0.0,
    "status_campanha": "em_andamento",
    "total_itens": 0,
    "itens_completos": 0,
    "itens": [],
    "ativa": true
  },
  "organizadora_criada": false
}
```

---

## ⚠️ Erros Comuns

### 1. Content-Type Incorreto

❌ **Erro:**
```javascript
headers: {
  'Content-Type': 'application/json' // ERRADO!
}
```

✅ **Correto:**
```javascript
// NÃO adicionar Content-Type quando usar FormData
// O browser/axios/fetch adiciona automaticamente
```

---

### 2. Enviar Imagem como String Base64

❌ **Erro:**
```javascript
{
  "imagem": "data:image/png;base64,iVBORw0KG..." // ERRADO!
}
```

✅ **Correto:**
```javascript
const formData = new FormData();
formData.append('imagem', fileInput.files[0]); // File object
```

---

### 3. Não Enviar Categorias como Array

❌ **Erro:**
```javascript
formData.append('categorias', '[1, 2]'); // ERRADO! (string)
```

✅ **Correto:**
```javascript
formData.append('categorias', 1);
formData.append('categorias', 2);
// ou
data.categorias = [1, 2]; // Em JSON
```

---

### 4. Formato de Data Inválido

❌ **Erro:**
```javascript
data_inicio: '03/11/2025' // ERRADO!
```

✅ **Correto:**
```javascript
data_inicio: '2025-11-03T00:00:00Z' // ISO 8601
```

---

## 🔒 Permissões

- ✅ Apenas usuários **autenticados**
- ✅ Apenas **Doadoras** e **Beneficiárias** podem criar campanhas
- ✅ A organizadora é preenchida **automaticamente** com o usuário atual

---

## 📂 Onde a Imagem é Salva?

### No Container Docker:
```
/app/media/campanhas/
```

### Na URL pública:
```
http://srv1037558.hstgr.cloud:8001/media/campanhas/imagem_123.jpg
```

### Formatos Suportados:
- PNG
- JPG / JPEG
- GIF
- WEBP

---

## 🧪 Testar Localmente

1. **Iniciar servidor:**
```bash
cd /home/lelo/conectades/backend
source ../venv/bin/activate
PYTHONPATH=/home/lelo/conectades DJANGO_SETTINGS_MODULE=backend.core.settings_local python manage.py runserver 8001
```

2. **Testar no Swagger:**
```
http://localhost:8001/api/docs/
```

3. **Criar campanha com imagem:**
   - Clique em `POST /api/campanhas/criar/`
   - Clique "Try it out"
   - Preencha os campos
   - Selecione uma imagem
   - Clique "Execute"

---

## 🚀 Deploy no Servidor

Após fazer push para o repositório:

```bash
# No servidor (srv1037558.hstgr.cloud)
cd /var/www/conectades-dev
git pull origin develop
docker compose build web
docker compose restart web

# Limpar cache
docker compose exec web python backend/manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('✅ Cache limpo!')
"
```

---

## 📋 Checklist de Implementação

- ✅ Serializer configurado com `ImageField`
- ✅ View configurada com `MultiPartParser`, `FormParser`, `JSONParser`
- ✅ Documentação Swagger atualizada
- ✅ Campo `imagem` é opcional (não obrigatório)
- ✅ Suporte a upload de arquivo real
- ✅ MEDIA_URL e MEDIA_ROOT configurados
- ✅ Nginx configurado para servir arquivos de media

---

## 🎉 Resumo

Antes:
```json
{
  "imagem": 0  // ❌ Esperava número
}
```

Depois:
```javascript
formData.append('imagem', fileObject);  // ✅ Aceita arquivo real
```

---

**Documentação atualizada em:** 2025-11-03

