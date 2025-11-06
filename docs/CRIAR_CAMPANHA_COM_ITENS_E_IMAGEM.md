# 🎯 Criar Campanha com Itens e Imagem

Este documento explica como criar uma campanha **completa** (com imagem e itens) em um único endpoint usando `multipart/form-data`.

---

## 🚀 **Endpoint**

**URL:** `POST /api/campanhas/criar/`

**Autenticação:** ✅ Requerida (Bearer Token)

**Content-Type:** `multipart/form-data`

---

## 📋 **Campos do Formulário**

### **Campos Obrigatórios:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `titulo` | string | Título da campanha |
| `descricao` | string | Descrição detalhada |
| `data_inicio` | datetime | Data/hora de início (ISO 8601) |
| `prazo` | datetime | Data/hora de término (ISO 8601) |

### **Campos Opcionais:**

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `subtitulo` | string | Subtítulo da campanha | "Ajude Maria a reconstruir sua vida" |
| `beneficiaria_id` | integer | ID da beneficiária | 5 |
| `imagem_arquivo` | file | Arquivo de imagem (PNG, JPG, JPEG, GIF, WEBP) | (arquivo binário) |
| `imagem_alt` | string | Texto alternativo da imagem | "Foto de Maria sorrindo" |
| `categorias` | string | IDs separados por vírgula | "1,2,3" |
| `whatsapp` | string | WhatsApp de contato | "(11) 98765-4321" |
| `localizacao` | integer | ID da localização | 2 |
| `ativa` | boolean | Se a campanha está ativa | true |
| `itens_cadastro` | string | JSON com lista de itens | Ver abaixo ⬇️ |

---

## 📦 **Cadastrando Itens Junto com a Campanha**

O campo `itens_cadastro` deve ser uma **string JSON** contendo um array de objetos:

```json
[
  {
    "nome": "Arroz tipo 1",
    "quantidade_solicitada": 50,
    "unidade": "kg"
  },
  {
    "nome": "Feijão carioca",
    "quantidade_solicitada": 30,
    "unidade": "kg"
  },
  {
    "nome": "Óleo de soja",
    "quantidade_solicitada": 20,
    "unidade": "litros"
  }
]
```

### **Campos de cada item:**

- **`nome`** (string, obrigatório): Nome do item
- **`quantidade_solicitada`** (integer, obrigatório): Quantidade total solicitada
- **`unidade`** (string, opcional): Unidade de medida (padrão: "unidade")

---

## 🖼️ **Upload de Imagem**

A imagem é enviada como arquivo binário no campo `imagem_arquivo`:

- **Formatos aceitos:** PNG, JPG, JPEG, GIF, WEBP
- **Tamanho máximo:** Depende da configuração do servidor
- **Campo opcional:** Se não enviar, a campanha ficará sem imagem

**Texto alternativo (`imagem_alt`):**
- Campo opcional para acessibilidade
- Padrão: "Imagem da campanha"
- Recomendação: Descrever o conteúdo da imagem

---

## 💻 **Exemplos de Uso**

### **Exemplo 1: cURL (sem itens)**

```bash
curl -X POST "http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "titulo=Campanha de Alimentos" \
  -F "subtitulo=Ajudando famílias em situação de vulnerabilidade" \
  -F "descricao=Esta campanha visa arrecadar alimentos para 50 famílias..." \
  -F "imagem_arquivo=@/caminho/para/imagem.jpg" \
  -F "imagem_alt=Foto de cestas básicas organizadas" \
  -F "categorias=1,2" \
  -F "whatsapp=(11) 98765-4321" \
  -F "localizacao=1" \
  -F "data_inicio=2025-11-10T00:00:00Z" \
  -F "prazo=2025-12-31T23:59:59Z"
```

### **Exemplo 2: cURL (com itens)**

```bash
curl -X POST "http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -F "titulo=Campanha de Alimentos" \
  -F "descricao=Esta campanha visa arrecadar alimentos..." \
  -F "imagem_arquivo=@/caminho/para/imagem.jpg" \
  -F "categorias=1,2" \
  -F "data_inicio=2025-11-10T00:00:00Z" \
  -F "prazo=2025-12-31T23:59:59Z" \
  -F 'itens_cadastro=[{"nome":"Arroz tipo 1","quantidade_solicitada":50,"unidade":"kg"},{"nome":"Feijão carioca","quantidade_solicitada":30,"unidade":"kg"}]'
```

### **Exemplo 3: JavaScript (Fetch API)**

```javascript
const formData = new FormData();

// Campos obrigatórios
formData.append('titulo', 'Campanha de Alimentos');
formData.append('descricao', 'Esta campanha visa arrecadar alimentos...');
formData.append('data_inicio', '2025-11-10T00:00:00Z');
formData.append('prazo', '2025-12-31T23:59:59Z');

// Imagem (FileInput)
const imageFile = document.querySelector('#imageInput').files[0];
formData.append('imagem_arquivo', imageFile);
formData.append('imagem_alt', 'Descrição da imagem');

// Categorias
formData.append('categorias', '1,2,3');

// Itens
const itens = [
  {
    nome: 'Arroz tipo 1',
    quantidade_solicitada: 50,
    unidade: 'kg'
  },
  {
    nome: 'Feijão carioca',
    quantidade_solicitada: 30,
    unidade: 'kg'
  }
];
formData.append('itens_cadastro', JSON.stringify(itens));

// Enviar request
fetch('http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer SEU_TOKEN_AQUI'
  },
  body: formData
})
  .then(response => response.json())
  .then(data => console.log('Sucesso:', data))
  .catch(error => console.error('Erro:', error));
```

### **Exemplo 4: Python (requests)**

```python
import requests
import json

url = 'http://srv1037558.hstgr.cloud:8001/api/campanhas/criar/'
headers = {
    'Authorization': 'Bearer SEU_TOKEN_AQUI'
}

# Dados do formulário
data = {
    'titulo': 'Campanha de Alimentos',
    'descricao': 'Esta campanha visa arrecadar alimentos...',
    'categorias': '1,2',
    'data_inicio': '2025-11-10T00:00:00Z',
    'prazo': '2025-12-31T23:59:59Z',
    'itens_cadastro': json.dumps([
        {
            'nome': 'Arroz tipo 1',
            'quantidade_solicitada': 50,
            'unidade': 'kg'
        },
        {
            'nome': 'Feijão carioca',
            'quantidade_solicitada': 30,
            'unidade': 'kg'
        }
    ])
}

# Arquivo de imagem
files = {
    'imagem_arquivo': open('imagem.jpg', 'rb')
}

response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())
```

---

## ✅ **Resposta de Sucesso (201)**

```json
{
  "message": "Campanha \"Campanha de Alimentos\" criada com sucesso! ✅ Campanha publicada e visível para todos! 📦 2 item(ns) cadastrado(s)!",
  "data": {
    "id": 10,
    "titulo": "Campanha de Alimentos",
    "subtitulo": "Ajudando famílias",
    "descricao": "Esta campanha visa arrecadar alimentos...",
    "organizadora": {
      "id": 5,
      "pessoa": {
        "id": 8,
        "username": "maria.silva",
        "nome_completo": "Maria Silva",
        "nome_social": "Maria"
      },
      "data_cadastro": "2025-11-01T10:00:00Z",
      "ativo": true
    },
    "beneficiaria": null,
    "beneficiaria_id": null,
    "beneficiaria_nome": null,
    "imagem_url": "http://srv1037558.hstgr.cloud:8001/media/campanhas/imagens/imagem_abc123.jpg",
    "categorias": [1, 2],
    "whatsapp": "(11) 98765-4321",
    "localizacao": 1,
    "data_inicio": "2025-11-10T00:00:00Z",
    "prazo": "2025-12-31T23:59:59Z",
    "dias_restantes": 55,
    "percentual_atingido": 0.0,
    "status_campanha": "⚪ Aguardando",
    "total_itens": 2,
    "itens_completos": 0,
    "itens": [
      {
        "id": 15,
        "campanha": 10,
        "nome": "Arroz tipo 1",
        "quantidade_solicitada": 50,
        "quantidade_contribuida": 0,
        "unidade": "kg",
        "percentual_atingido": 0.0,
        "data_criacao": "2025-11-06T12:00:00Z"
      },
      {
        "id": 16,
        "campanha": 10,
        "nome": "Feijão carioca",
        "quantidade_solicitada": 30,
        "quantidade_contribuida": 0,
        "unidade": "kg",
        "percentual_atingido": 0.0,
        "data_criacao": "2025-11-06T12:00:00Z"
      }
    ],
    "doacoes": [],
    "ativa": true
  },
  "organizadora_criada": false,
  "publicada": true,
  "total_itens_cadastrados": 2
}
```

---

## 🐛 **Tratamento de Erros**

### **400 Bad Request - Categorias inválidas**

```json
{
  "error": "Formato inválido para categorias. Use IDs separados por vírgula (ex: \"1,2,3\")"
}
```

**Solução:** Envie categorias como string: `"1,2,3"`

---

### **400 Bad Request - JSON de itens inválido**

```json
{
  "error": "Formato inválido para itens_cadastro. Use JSON válido."
}
```

**Solução:** Certifique-se de que `itens_cadastro` é um JSON válido em formato string.

---

### **400 Bad Request - Campos faltando**

```json
{
  "titulo": ["This field is required."],
  "descricao": ["This field is required."]
}
```

**Solução:** Envie todos os campos obrigatórios.

---

### **403 Forbidden - Tipo de usuário incorreto**

```json
{
  "error": "Apenas Doadoras e Beneficiárias podem criar campanhas!",
  "tipo_usuario_atual": "Gestora",
  "tipos_permitidos": ["Doadora", "Beneficiária"]
}
```

**Solução:** Apenas usuários com tipo `doadora` ou `beneficiaria` podem criar campanhas.

---

## 🎯 **Dicas Importantes**

### ✅ **Categorias como String**

No `multipart/form-data`, envie as categorias como **string separada por vírgula**:

```
categorias: "1,2,3"
```

### ✅ **Itens como JSON String**

No `multipart/form-data`, o `itens_cadastro` deve ser uma **string JSON**:

```
itens_cadastro: '[{"nome":"Arroz","quantidade_solicitada":50,"unidade":"kg"}]'
```

### ✅ **Formato de Data**

Use formato ISO 8601:

```
data_inicio: "2025-11-10T00:00:00Z"
prazo: "2025-12-31T23:59:59Z"
```

### ✅ **Imagem Opcional**

Se não enviar `imagem_arquivo`, a campanha será criada sem imagem.

### ✅ **Itens Opcionais**

Se não enviar `itens_cadastro`, a campanha será criada sem itens. Você pode adicionar itens depois usando:

```
POST /api/campanhas/{campanha_id}/itens/cadastrar/
```

---

## 🌐 **Testando no Swagger UI**

Acesse: `http://srv1037558.hstgr.cloud:8001/api/docs/`

1. **Authorize** com seu Bearer Token
2. Encontre: `POST /api/campanhas/criar/`
3. Clique em **"Try it out"**
4. Preencha os campos:
   - `titulo`, `descricao`, `data_inicio`, `prazo` (obrigatórios)
   - `imagem_arquivo`: Clique em "Choose File"
   - `categorias`: Digite "1,2,3"
   - `itens_cadastro`: Cole o JSON dos itens
5. Clique em **"Execute"**

---

## 📊 **Comparação: Antes vs. Depois**

### ❌ **ANTES (3 requests):**

```bash
# 1. Criar campanha
POST /api/campanhas/criar/
# (sem imagem, erro 500 com multipart)

# 2. Cadastrar item 1
POST /api/campanhas/5/itens/cadastrar/

# 3. Cadastrar item 2
POST /api/campanhas/5/itens/cadastrar/
```

### ✅ **AGORA (1 request):**

```bash
# Tudo de uma vez!
POST /api/campanhas/criar/
# Com imagem, itens, categorias...
```

---

## 🎉 **Resumo**

| Recurso | Status |
|---------|--------|
| Upload de imagem via multipart | ✅ Funcionando |
| Cadastrar itens junto com campanha | ✅ Funcionando |
| Processar categorias como string | ✅ Funcionando |
| Retornar URL da imagem | ✅ Funcionando |
| Auto-publicação | ✅ Funcionando |
| Validações completas | ✅ Funcionando |

---

**📝 Atualizado em:** 06/11/2025

