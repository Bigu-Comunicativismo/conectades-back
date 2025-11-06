# 📤 Guia: Enviando Multipart/Form-Data Corretamente

Este documento explica como enviar dados via `multipart/form-data` para os endpoints da API que requerem upload de arquivos.

---

## 🚨 **Problema Comum**

### **Erro: "Invalid boundary in multipart: None"**

```
django.http.multipartparser.MultiPartParserError: Invalid boundary in multipart: None
```

**Causa:** O cliente está enviando `Content-Type: multipart/form-data` **sem o boundary** correto.

**Solução:** Configure seu cliente HTTP corretamente (veja exemplos abaixo).

---

## 📋 **Endpoints que Requerem Multipart/Form-Data**

| Endpoint | Método | Motivo |
|----------|--------|--------|
| `/api/auth/registro/iniciar/` | POST | Upload de avatar |
| `/api/auth/perfil/` | PUT/PATCH | Upload de avatar |
| `/api/campanhas/criar/` | POST | Upload de imagem da campanha |
| `/api/campanhas/{id}/itens/cadastrar/` | POST | (Aceita JSON também) |

---

## ✅ **Como Enviar Corretamente**

### **1. Swagger UI (Navegador)**

Ao testar no Swagger UI (`/api/docs/`):

1. **Clique em "Try it out"**
2. **Preencha os campos de texto** normalmente
3. **Para arquivos:** Clique em **"Choose File"** e selecione o arquivo
4. **NÃO** mude o Content-Type manualmente
5. Clique em **"Execute"**

O Swagger UI configura automaticamente o `boundary` correto! ✅

---

### **2. cURL (Terminal)**

Use a flag `-F` para cada campo:

```bash
curl -X POST "http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "email=maria@example.com" \
  -F "username=maria.silva" \
  -F "password=SenhaForte123!" \
  -F "nome_completo=Maria Silva" \
  -F "cpf=123.456.789-00" \
  -F "telefone=(11) 98765-4321" \
  -F "tipo_usuario=1" \
  -F "genero=1" \
  -F "cidade=São Paulo" \
  -F "bairro=Centro" \
  -F "mini_bio=Desenvolvedora apaixonada por tecnologia" \
  -F "avatar=@/caminho/para/foto.jpg" \
  -F "categorias_interesse=1" \
  -F "categorias_interesse=2" \
  -F "localizacoes_interesse=1"
```

**⚠️ NÃO use:**
```bash
# ❌ ERRADO - não especifica boundary
curl -H "Content-Type: multipart/form-data" ...
```

---

### **3. JavaScript (Fetch API)**

```javascript
// ✅ CORRETO - FormData gera boundary automaticamente
const formData = new FormData();

// Campos de texto
formData.append('email', 'maria@example.com');
formData.append('username', 'maria.silva');
formData.append('password', 'SenhaForte123!');
formData.append('nome_completo', 'Maria Silva');
formData.append('cpf', '123.456.789-00');
formData.append('telefone', '(11) 98765-4321');
formData.append('tipo_usuario', '1');
formData.append('genero', '1');
formData.append('cidade', 'São Paulo');
formData.append('bairro', 'Centro');
formData.append('mini_bio', 'Desenvolvedora apaixonada por tecnologia');

// Arquivo (de um input type="file")
const fileInput = document.querySelector('#avatarInput');
if (fileInput.files[0]) {
  formData.append('avatar', fileInput.files[0]);
}

// Arrays (categorias_interesse e localizacoes_interesse)
formData.append('categorias_interesse', '1');
formData.append('categorias_interesse', '2');
formData.append('localizacoes_interesse', '1');

// Enviar
fetch('http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer SEU_TOKEN'
    // ⚠️ NÃO adicione Content-Type manualmente!
    // O navegador adiciona automaticamente com boundary correto
  },
  body: formData
})
  .then(response => response.json())
  .then(data => console.log('Sucesso:', data))
  .catch(error => console.error('Erro:', error));
```

**❌ NÃO FAÇA:**
```javascript
// ERRADO - Não funciona com FormData
fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'multipart/form-data' // ❌ ERRADO!
  },
  body: formData
})
```

---

### **4. Axios (JavaScript)**

```javascript
import axios from 'axios';

const formData = new FormData();
formData.append('email', 'maria@example.com');
formData.append('username', 'maria.silva');
// ... outros campos ...
formData.append('avatar', fileObject); // File object do input

axios.post('http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/', formData, {
  headers: {
    'Authorization': 'Bearer SEU_TOKEN',
    // Axios configura Content-Type automaticamente!
  }
})
  .then(response => {
    console.log('Sucesso:', response.data);
  })
  .catch(error => {
    console.error('Erro:', error.response.data);
  });
```

---

### **5. Python (requests)**

```python
import requests

url = 'http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/'
headers = {
    'Authorization': 'Bearer SEU_TOKEN'
}

# Dados do formulário
data = {
    'email': 'maria@example.com',
    'username': 'maria.silva',
    'password': 'SenhaForte123!',
    'nome_completo': 'Maria Silva',
    'cpf': '123.456.789-00',
    'telefone': '(11) 98765-4321',
    'tipo_usuario': '1',
    'genero': '1',
    'cidade': 'São Paulo',
    'bairro': 'Centro',
    'mini_bio': 'Desenvolvedora apaixonada por tecnologia',
    'categorias_interesse': ['1', '2'],
    'localizacoes_interesse': ['1']
}

# Arquivo
files = {
    'avatar': open('foto.jpg', 'rb')
}

# Enviar (requests configura Content-Type automaticamente!)
response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())
```

**❌ NÃO FAÇA:**
```python
# ERRADO - Não especifique Content-Type manualmente
headers = {
    'Content-Type': 'multipart/form-data'  # ❌ ERRADO!
}
```

---

### **6. Postman**

1. **Selecione o método:** POST
2. **URL:** `http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/`
3. **Headers:**
   - `Authorization`: `Bearer SEU_TOKEN`
   - **NÃO** adicione `Content-Type` manualmente!
4. **Body:**
   - Selecione: **form-data** (não raw ou binary)
   - Adicione cada campo como linha separada
   - Para arquivo: Mude o tipo de "Text" para "File" e selecione o arquivo
5. **Send**

O Postman configura o boundary automaticamente! ✅

---

### **7. Insomnia**

1. **Método:** POST
2. **URL:** `http://srv1037558.hstgr.cloud:8001/api/auth/registro/iniciar/`
3. **Headers:**
   - `Authorization`: `Bearer SEU_TOKEN`
4. **Body:** Selecione **"Multipart Form"**
5. Adicione cada campo
6. Para arquivo: Clique em "File" e selecione
7. **Send**

---

## 🐛 **Erros Comuns e Soluções**

### **Erro 1: "Invalid boundary in multipart: None"**

**Causa:** Content-Type foi definido manualmente como `multipart/form-data` sem boundary.

**Solução:** **NÃO** defina `Content-Type` manualmente. Deixe o cliente HTTP configurar automaticamente.

---

### **Erro 2: "Content-Type incorreto"**

```json
{
  "error": "Content-Type incorreto",
  "recebido": "application/json",
  "esperado": "multipart/form-data"
}
```

**Causa:** Você está enviando JSON puro para um endpoint que requer multipart.

**Solução:** Use FormData ou configure o cliente para enviar multipart/form-data.

---

### **Erro 3: "The submitted data was not a file"**

```json
{
  "avatar": ["The submitted data was not a file. Check the encoding type on the form."]
}
```

**Causa:** O campo de arquivo foi enviado como string (Base64 ou URL) ao invés de arquivo binário.

**Solução:** Envie o arquivo como **File object** (JavaScript) ou **file handle** (Python), não como string.

---

### **Erro 4: Arrays não funcionam**

**Problema:** Enviando `categorias_interesse` como `[1,2]` (JSON array) em multipart.

**Solução:** Envie múltiplas vezes com o mesmo nome:

```javascript
// ✅ CORRETO
formData.append('categorias_interesse', '1');
formData.append('categorias_interesse', '2');

// ❌ ERRADO
formData.append('categorias_interesse', [1, 2]);
```

---

## 🎯 **Regras de Ouro**

### ✅ **SEMPRE:**

1. Use `FormData` em JavaScript
2. Use flag `-F` em cURL
3. Use `files=` em Python requests
4. Deixe o cliente HTTP configurar o `Content-Type` automaticamente
5. Envie arquivos como **objetos File**, não strings

### ❌ **NUNCA:**

1. Defina `Content-Type: multipart/form-data` manualmente
2. Envie arquivos como Base64 ou strings
3. Use `JSON.stringify()` no body do FormData
4. Tente enviar JSON puro para endpoints de upload

---

## 📊 **Anatomia do Content-Type Correto**

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryABC123XYZ
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                    Este é o boundary (gerado automaticamente)
```

**Exemplo completo:**

```http
POST /api/auth/registro/iniciar/ HTTP/1.1
Host: srv1037558.hstgr.cloud:8001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 12345

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="email"

maria@example.com
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="avatar"; filename="foto.jpg"
Content-Type: image/jpeg

[binary data here]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

---

## 🌐 **Testando Localmente**

### **Teste rápido com cURL:**

```bash
# Baixar uma imagem de teste
wget https://via.placeholder.com/150 -O avatar.jpg

# Testar endpoint
curl -X POST "http://localhost:8001/api/auth/registro/iniciar/" \
  -F "email=test@example.com" \
  -F "username=testuser" \
  -F "password=Test123456!" \
  -F "nome_completo=Test User" \
  -F "cpf=123.456.789-00" \
  -F "telefone=(11) 99999-9999" \
  -F "tipo_usuario=1" \
  -F "genero=1" \
  -F "cidade=São Paulo" \
  -F "bairro=Centro" \
  -F "mini_bio=Testing" \
  -F "avatar=@avatar.jpg" \
  -F "categorias_interesse=1" \
  -F "localizacoes_interesse=1"
```

---

## 📝 **Resumo**

| Ferramenta | Como Configurar |
|------------|-----------------|
| **Swagger UI** | Use "Choose File", não mude Content-Type |
| **cURL** | Use `-F` para cada campo |
| **JavaScript Fetch** | Use `FormData`, **não** defina Content-Type |
| **Axios** | Use `FormData`, Axios configura automaticamente |
| **Python requests** | Use `files=` param, **não** defina Content-Type |
| **Postman** | Selecione "form-data", não raw |
| **Insomnia** | Selecione "Multipart Form" |

**Lembre-se:** O cliente HTTP **DEVE** gerar o boundary automaticamente! ✅

---

**📝 Atualizado em:** 06/11/2025

