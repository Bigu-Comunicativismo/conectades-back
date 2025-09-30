# 🧪 Guia de Testes - Insomnia & Postman

Instruções passo a passo para testar a API Conectades usando Insomnia ou Postman.

---

## 📋 Índice

- [Testando com Insomnia](#testando-com-insomnia)
- [Testando com Postman](#testando-com-postman)
- [Collection Pronta](#collection-pronta-json)
- [Fluxos de Teste](#fluxos-de-teste)

---

## 🎨 Testando com Insomnia

### ⚡ OPÇÃO RÁPIDA: Importar Collection Pronta

1. Abra o Insomnia
2. Clique em **"Application" → "Preferences" → "Data"**
3. Clique em **"Import Data" → "From File"**
4. Selecione o arquivo **`insomnia_collection.json`**
5. Pronto! Todos os requests estão configurados

**Pule para o PASSO 4** se importou a collection pronta.

---

### PASSO 1: Instalar Insomnia (se ainda não tem)

**Baixar:**
- Site oficial: https://insomnia.rest/download
- Disponível para: Linux, macOS, Windows

**Instalar:**
- Linux: `sudo dpkg -i insomnia-*.deb` ou `sudo snap install insomnia`
- macOS: Arrastar para Applications
- Windows: Executar instalador `.exe`

### PASSO 2: Criar Workspace

1. Abra o Insomnia
2. Clique em **"Create" → "Request Collection"**
3. Nome: **"Conectades API"**
4. Clique em **"Create"**

### PASSO 3: Configurar Variáveis de Ambiente

1. Clique no ícone de **engrenagem** (Manage Environments)
2. Em **"Base Environment"**, adicione:

```json
{
  "base_url": "http://localhost",
  "api_base": "http://localhost/api",
  "token": ""
}
```

3. Clique em **"Done"**

### PASSO 4: Criar Requests de Autenticação

#### Request 1: Login (Obter Token JWT)

1. Clique em **"New HTTP Request"**
2. Nome: **"1. Login - Obter Token"**
3. Método: **POST**
4. URL: `{{ _.api_base }}/token/`
5. **Headers:**
   - Clique em **"Header" tab**
   - Adicione: `Content-Type: application/json`
6. **Body:**
   - Selecione **"JSON"**
   - Cole:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
7. Clique em **"Send"**

**Resposta esperada (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Request 2: Salvar Token

1. **Copie** o valor de `access` da resposta
2. Vá em **Manage Environments** (ícone engrenagem)
3. Cole o token na variável `token`:
   ```json
   {
     "base_url": "http://localhost",
     "api_base": "http://localhost/api",
     "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```
4. Clique em **"Done"**

### PASSO 5: Criar Requests de Campanhas

#### Request 3: Listar Campanhas

1. **New HTTP Request**
2. Nome: **"2. Listar Campanhas"**
3. Método: **GET**
4. URL: `{{ _.api_base }}/campanhas/listar/`
5. **Headers:**
   - `Authorization: Bearer {{ _.token }}`
6. Clique em **"Send"**

**Resposta esperada (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "titulo": "Campanha Teste",
      "descricao": "...",
      "organizadora": {...},
      "beneficiaria": {...},
      "data_inicio": "2024-01-01",
      "data_fim": "2024-12-31"
    }
  ]
}
```

#### Request 4: Minhas Campanhas

1. **New HTTP Request**
2. Nome: **"3. Minhas Campanhas"**
3. Método: **GET**
4. URL: `{{ _.api_base }}/campanhas/minhas/`
5. **Headers:**
   - `Authorization: Bearer {{ _.token }}`
6. Clique em **"Send"**

#### Request 5: Criar Campanha

1. **New HTTP Request**
2. Nome: **"4. Criar Campanha"**
3. Método: **POST**
4. URL: `{{ _.api_base }}/campanhas/criar/`
5. **Headers:**
   - `Authorization: Bearer {{ _.token }}`
   - `Content-Type: application/json`
6. **Body (JSON):**
   ```json
   {
     "titulo": "Campanha de Alimentos",
     "descricao": "Arrecadação de alimentos para comunidade",
     "data_inicio": "2024-01-01",
     "data_fim": "2024-12-31",
     "beneficiaria_id": 1
   }
   ```
7. Clique em **"Send"**

**Resposta esperada (201 Created):**
```json
{
  "message": "Campanha \"Campanha de Alimentos\" criada com sucesso!",
  "data": {
    "id": 2,
    "titulo": "Campanha de Alimentos",
    ...
  }
}
```

### PASSO 6: Criar Requests de Doações

#### Request 6: Criar Doação

1. **New HTTP Request**
2. Nome: **"5. Criar Doação"**
3. Método: **POST**
4. URL: `{{ _.api_base }}/doacoes/criar/`
5. **Headers:**
   - `Authorization: Bearer {{ _.token }}`
   - `Content-Type: application/json`
6. **Body (JSON):**
   ```json
   {
     "campanha_id": 1,
     "tipo": "alimento",
     "descricao": "10kg de arroz e 5kg de feijão"
   }
   ```
7. Clique em **"Send"**

#### Request 7: Listar Doações por Campanha

1. **New HTTP Request**
2. Nome: **"6. Listar Doações"**
3. Método: **GET**
4. URL: `{{ _.api_base }}/doacoes/listar/1/`
5. **Headers:**
   - `Authorization: Bearer {{ _.token }}`
6. Clique em **"Send"**

### PASSO 7: Testar Performance e Cache

#### Teste de Cache:

1. Execute **"2. Listar Campanhas"** pela primeira vez
   - Anote o **tempo de resposta** (ex: 150ms)
   
2. Execute **"2. Listar Campanhas"** novamente
   - Tempo deve ser muito menor (ex: 5ms)
   - **Melhoria esperada: 10-30x mais rápido!**

3. Verificar cache no Redis:
```bash
docker-compose exec redis redis-cli KEYS "*campanhas*"
```

#### Teste de Múltiplas Requisições:

1. Selecione múltiplos requests
2. Clique com **botão direito**
3. Selecione **"Send All"**
4. Observe os tempos de resposta

---

## 📮 Testando com Postman

### ⚡ OPÇÃO RÁPIDA: Importar Collection Pronta

1. Abra o Postman
2. Clique em **"Import"** (canto superior esquerdo)
3. Clique em **"Upload Files"**
4. Selecione o arquivo **`postman_collection.json`**
5. Clique em **"Import"**
6. Pronto! Todos os requests com testes automáticos estão configurados

**Pule para o PASSO 4** se importou a collection pronta.

---

### PASSO 1: Instalar Postman (se ainda não tem)

**Baixar:**
- Site oficial: https://www.postman.com/downloads/
- Disponível para: Linux, macOS, Windows

**Instalar:**
- Linux: Baixe e descompacte, ou use Snap: `sudo snap install postman`
- macOS: Arrastar para Applications
- Windows: Executar instalador

### PASSO 2: Criar Collection

1. Abra o Postman
2. Clique em **"New" → "Collection"**
3. Nome: **"Conectades API"**
4. Clique em **"Create"**

### PASSO 3: Configurar Variáveis

1. Selecione a collection **"Conectades API"**
2. Vá na aba **"Variables"**
3. Adicione as variáveis:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost` | `http://localhost` |
| `api_base` | `http://localhost/api` | `http://localhost/api` |
| `token` | *(deixe vazio)* | *(deixe vazio)* |

4. Clique em **"Save"**

### PASSO 4: Criar Request de Login

1. Na collection, clique em **"Add request"**
2. Nome: **"1. Login - Obter Token"**
3. Método: **POST**
4. URL: `{{api_base}}/token/`
5. **Headers:**
   - Key: `Content-Type` | Value: `application/json`
6. **Body:**
   - Selecione **"raw"** e **"JSON"**
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
7. Clique em **"Send"**

### PASSO 5: Salvar Token Automaticamente

1. Na request **"1. Login - Obter Token"**
2. Vá na aba **"Tests"**
3. Cole o script:
```javascript
// Salvar token automaticamente
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.collectionVariables.set("token", jsonData.access);
    console.log("Token salvo:", jsonData.access);
}
```
4. Clique em **"Save"**
5. Execute novamente a request
6. O token será salvo automaticamente na variável `token`

### PASSO 6: Criar Request de Campanhas

#### Request: Listar Campanhas

1. **Add request** → Nome: **"2. Listar Campanhas"**
2. Método: **GET**
3. URL: `{{api_base}}/campanhas/listar/`
4. **Authorization:**
   - Type: **Bearer Token**
   - Token: `{{token}}`
5. Clique em **"Send"**

#### Request: Criar Campanha

1. **Add request** → Nome: **"3. Criar Campanha"**
2. Método: **POST**
3. URL: `{{api_base}}/campanhas/criar/`
4. **Authorization:**
   - Type: **Bearer Token**
   - Token: `{{token}}`
5. **Headers:**
   - Key: `Content-Type` | Value: `application/json`
6. **Body (JSON):**
```json
{
  "titulo": "Campanha de Roupas",
  "descricao": "Arrecadação de roupas para inverno",
  "data_inicio": "2024-01-01",
  "data_fim": "2024-12-31",
  "beneficiaria_id": 1
}
```
7. Clique em **"Send"**

### PASSO 7: Criar Request de Doações

#### Request: Criar Doação

1. **Add request** → Nome: **"4. Criar Doação"**
2. Método: **POST**
3. URL: `{{api_base}}/doacoes/criar/`
4. **Authorization:**
   - Type: **Bearer Token**
   - Token: `{{token}}`
5. **Body (JSON):**
```json
{
  "campanha_id": 1,
  "tipo": "roupa",
  "descricao": "5 casacos de inverno"
}
```
6. Clique em **"Send"**

#### Request: Listar Doações

1. **Add request** → Nome: **"5. Listar Doações"**
2. Método: **GET**
3. URL: `{{api_base}}/doacoes/listar/1/`
4. **Authorization:**
   - Type: **Bearer Token**
   - Token: `{{token}}`
5. Clique em **"Send"**

---

## 📊 Collection Pronta (JSON)

### Para Insomnia:

Crie um arquivo `insomnia_collection.json`:

```json
{
  "name": "Conectades API",
  "requests": [
    {
      "name": "1. Login",
      "method": "POST",
      "url": "{{ _.api_base }}/token/",
      "headers": [
        {"name": "Content-Type", "value": "application/json"}
      ],
      "body": {
        "mimeType": "application/json",
        "text": "{\"username\":\"admin\",\"password\":\"admin123\"}"
      }
    },
    {
      "name": "2. Listar Campanhas",
      "method": "GET",
      "url": "{{ _.api_base }}/campanhas/listar/",
      "headers": [
        {"name": "Authorization", "value": "Bearer {{ _.token }}"}
      ]
    },
    {
      "name": "3. Criar Campanha",
      "method": "POST",
      "url": "{{ _.api_base }}/campanhas/criar/",
      "headers": [
        {"name": "Authorization", "value": "Bearer {{ _.token }}"},
        {"name": "Content-Type", "value": "application/json"}
      ],
      "body": {
        "mimeType": "application/json",
        "text": "{\"titulo\":\"Campanha Teste\",\"descricao\":\"Descrição\",\"data_inicio\":\"2024-01-01\"}"
      }
    }
  ]
}
```

**Importar no Insomnia:**
1. Clique em **"Application" → "Preferences" → "Data"**
2. Clique em **"Import Data" → "From File"**
3. Selecione o arquivo `insomnia_collection.json`

### Para Postman:

Crie um arquivo `postman_collection.json`:

```json
{
  "info": {
    "name": "Conectades API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Login - Obter Token",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "if (pm.response.code === 200) {",
              "    const jsonData = pm.response.json();",
              "    pm.collectionVariables.set('token', jsonData.access);",
              "    console.log('Token salvo:', jsonData.access);",
              "}"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"username\":\"admin\",\"password\":\"admin123\"}"
        },
        "url": {
          "raw": "{{api_base}}/token/",
          "host": ["{{api_base}}"],
          "path": ["token"]
        }
      }
    },
    {
      "name": "2. Listar Campanhas",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{api_base}}/campanhas/listar/",
          "host": ["{{api_base}}"],
          "path": ["campanhas", "listar"]
        },
        "auth": {
          "type": "bearer",
          "bearer": [
            {"key": "token", "value": "{{token}}"}
          ]
        }
      }
    },
    {
      "name": "3. Criar Campanha",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"titulo\":\"Campanha Teste\",\"descricao\":\"Descrição da campanha\",\"data_inicio\":\"2024-01-01\",\"data_fim\":\"2024-12-31\"}"
        },
        "url": {
          "raw": "{{api_base}}/campanhas/criar/",
          "host": ["{{api_base}}"],
          "path": ["campanhas", "criar"]
        },
        "auth": {
          "type": "bearer",
          "bearer": [
            {"key": "token", "value": "{{token}}"}
          ]
        }
      }
    },
    {
      "name": "4. Criar Doação",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"campanha_id\":1,\"tipo\":\"alimento\",\"descricao\":\"Doação de alimentos\"}"
        },
        "url": {
          "raw": "{{api_base}}/doacoes/criar/",
          "host": ["{{api_base}}"],
          "path": ["doacoes", "criar"]
        },
        "auth": {
          "type": "bearer",
          "bearer": [
            {"key": "token", "value": "{{token}}"}
          ]
        }
      }
    },
    {
      "name": "5. Listar Doações",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{api_base}}/doacoes/listar/1/",
          "host": ["{{api_base}}"],
          "path": ["doacoes", "listar", "1"]
        },
        "auth": {
          "type": "bearer",
          "bearer": [
            {"key": "token", "value": "{{token}}"}
          ]
        }
      }
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost"},
    {"key": "api_base", "value": "http://localhost/api"},
    {"key": "token", "value": ""}
  ]
}
```

**Importar no Postman:**
1. Clique em **"Import"** (canto superior esquerdo)
2. Arraste o arquivo `postman_collection.json` ou clique em **"Upload Files"**
3. Clique em **"Import"**

---

## 🔄 Fluxos de Teste

### Fluxo 1: Autenticação Completa

1. **Login** → Obter token
2. **Listar Campanhas** → Verificar autenticação funcionando
3. **Refresh Token** → Renovar token (opcional)

**Validações:**
- ✅ Login retorna 200 OK com `access` e `refresh`
- ✅ Requests autenticadas retornam 200 OK
- ✅ Requests sem token retornam 401 Unauthorized

### Fluxo 2: CRUD de Campanhas

1. **Criar Campanha** → POST
2. **Listar Campanhas** → Verificar nova campanha na lista
3. **Minhas Campanhas** → Verificar campanha do usuário
4. **Campanhas Beneficiária** → Verificar campanhas onde sou beneficiária

**Validações:**
- ✅ Criar retorna 201 Created
- ✅ Lista contém a campanha criada
- ✅ Dados estão corretos (título, descrição, datas)

### Fluxo 3: CRUD de Doações

1. **Criar Campanha** → Obter ID da campanha
2. **Criar Doação** → Vincular à campanha
3. **Listar Doações** → Verificar doação na lista

**Validações:**
- ✅ Doação criada com 201 Created
- ✅ Doação vinculada à campanha correta
- ✅ Doador é o usuário autenticado

### Fluxo 4: Teste de Cache Redis

**Objetivo:** Verificar se o cache está reduzindo latência

1. **Limpar cache** (opcional):
```bash
docker-compose exec redis redis-cli FLUSHALL
```

2. **Primeira execução** (cache miss):
   - Execute: **"2. Listar Campanhas"**
   - Anote tempo: `___ms` (ex: 150ms)

3. **Segunda execução** (cache hit):
   - Execute: **"2. Listar Campanhas"** novamente
   - Anote tempo: `___ms` (ex: 5ms)

4. **Calcular melhoria:**
   - Melhoria = Tempo1 / Tempo2
   - **Esperado: 10-30x mais rápido**

5. **Verificar chave no Redis:**
```bash
docker-compose exec redis redis-cli GET campanhas_all
```

### Fluxo 5: Teste de Invalidação de Cache

**Objetivo:** Verificar se cache é invalidado ao criar dados

1. **Listar Campanhas** → Cache hit (rápido)
2. **Criar Campanha** → Nova campanha
3. **Listar Campanhas** → Cache miss (mais lento, mas com dados atualizados)
4. **Listar Campanhas** → Cache hit novamente (rápido)

**Validações:**
- ✅ Nova campanha aparece na listagem
- ✅ Cache é invalidado após criação
- ✅ Cache é reconstruído na próxima consulta

### Fluxo 6: Teste de Throttling

**Objetivo:** Verificar rate limiting

1. Duplique a request **"2. Listar Campanhas"** 50 vezes
2. Selecione todas e clique em **"Send All"** ou **"Run Collection"**
3. Observe as respostas

**Validações:**
- ✅ Primeiras requests: 200 OK
- ✅ Após limite: 429 Too Many Requests
- ✅ Header `Retry-After` presente

### Fluxo 7: Teste de Paginação

1. **Criar múltiplas campanhas** (20+)
2. **Listar Campanhas** → Verificar paginação

**Request com paginação:**
- URL: `{{api_base}}/campanhas/listar/?page=1&page_size=10`

**Validações:**
- ✅ Resposta contém `count`, `next`, `previous`
- ✅ `results` tem no máximo `page_size` itens
- ✅ Link `next` aponta para próxima página

---

## 📈 Testes Avançados com Scripts

### Script de Teste no Postman (Tests tab):

```javascript
// Verificar status code
pm.test("Status code é 200", function () {
    pm.response.to.have.status(200);
});

// Verificar tempo de resposta
pm.test("Resposta em menos de 100ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(100);
});

// Verificar estrutura da resposta
pm.test("Resposta tem campo 'results'", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('results');
});

// Verificar paginação
pm.test("Paginação está ativa", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('count');
    pm.expect(jsonData).to.have.property('next');
    pm.expect(jsonData).to.have.property('previous');
});

// Salvar ID para próximas requests
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.collectionVariables.set("campanha_id", jsonData.data.id);
}
```

---

## 🧪 Runner de Collection (Postman)

### Executar todos os testes:

1. Clique na collection **"Conectades API"**
2. Clique em **"Run"** (▶️)
3. Selecione todas as requests
4. Defina **Iterations**: 10 (para teste de carga)
5. Defina **Delay**: 100ms
6. Clique em **"Run Conectades API"**

### Analisar resultados:

- **Passed**: Testes que passaram
- **Failed**: Testes que falharam
- **Average Response Time**: Tempo médio de resposta
- **Total Time**: Tempo total de execução

**Meta para aprovar:**
- ✅ 100% testes passados
- ✅ Tempo médio < 100ms
- ✅ Sem erros 5xx

---

## 🎯 Checklist de Testes Completo

### ✅ Autenticação
- [ ] Login retorna token JWT (200 OK)
- [ ] Token é aceito em requests autenticadas
- [ ] Request sem token retorna 401 Unauthorized
- [ ] Token inválido retorna 401 Unauthorized

### ✅ Campanhas
- [ ] Listar campanhas retorna 200 OK
- [ ] Criar campanha retorna 201 Created
- [ ] Minhas campanhas retorna só minhas campanhas
- [ ] Campanhas beneficiária filtra corretamente

### ✅ Doações
- [ ] Criar doação retorna 201 Created
- [ ] Listar doações por campanha retorna 200 OK
- [ ] Doação está vinculada à campanha correta
- [ ] Doador é o usuário autenticado

### ✅ Performance e Cache
- [ ] Segunda requisição é 10-30x mais rápida (cache hit)
- [ ] Cache é invalidado ao criar dados
- [ ] Latência média < 100ms
- [ ] Throughput > 100 RPS

### ✅ Paginação
- [ ] Listagens retornam paginação
- [ ] page_size funciona corretamente
- [ ] Links next/previous estão corretos

### ✅ Rate Limiting
- [ ] Muitas requests retornam 429
- [ ] Header Retry-After presente
- [ ] Limit reseta após tempo

### ✅ Validações
- [ ] Campos obrigatórios validados
- [ ] Formatos de data validados
- [ ] Foreign keys válidas

---

## 📊 Exemplo de Teste de Carga

### Com Insomnia Runner:

1. Selecione múltiplos requests
2. Clique com botão direito → **"Run Tests"**
3. Configure:
   - **Iterations**: 100
   - **Delay**: 10ms
4. Execute e analise resultados

### Com Postman Collection Runner:

1. Clique em **"Run Collection"**
2. Configure:
   - **Iterations**: 100
   - **Delay**: 10ms
   - **Data file**: (opcional) CSV com dados de teste
3. Execute
4. Veja **"Run Results"** para métricas

### Métricas esperadas (100 iterações):

| Métrica | Valor Esperado |
|---------|----------------|
| **Success Rate** | ≥95% |
| **Avg Response Time** | ≤50ms |
| **P95 Response Time** | ≤100ms |
| **Throughput** | ≥200 RPS |
| **Errors 4xx/5xx** | <5% |

---

## 🐛 Troubleshooting dos Testes

### Token expira durante os testes

**Solução:** Aumentar tempo de vida do token em `backend/core/settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
}
```

### Cache não está funcionando

**Verificar Redis:**
```bash
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli KEYS "*"
```

**Ver logs do Django:**
```bash
docker-compose logs web | grep cache
```

### Requests retornam 502 Bad Gateway

**Verificar se app está rodando:**
```bash
docker-compose ps
docker-compose logs web
curl http://localhost:8000/api/docs/  # Testar direto no app
```

### Performance muito baixa

**Verificar cache hit:**
```bash
# Fazer request
curl -H "Authorization: Bearer TOKEN" http://localhost/api/campanhas/listar/

# Verificar se está no cache
docker-compose exec redis redis-cli EXISTS campanhas_all
# Deve retornar: 1 (existe)
```

---

## 📝 Dicas Profissionais

### Insomnia:

1. **Use folders** para organizar requests por domínio
2. **Template tags** `{{ _.variavel }}` para reutilizar valores
3. **Code snippets** para gerar código de consumo da API
4. **Ambiente Staging/Produção** para testar múltiplos ambientes

### Postman:

1. **Environments** separados (Dev, Staging, Prod)
2. **Pre-request Scripts** para gerar dados dinâmicos
3. **Tests Scripts** para validação automatizada
4. **Newman** (CLI) para CI/CD:
   ```bash
   newman run postman_collection.json -e environment.json
   ```

### Testes de Performance:

1. **Warm-up** antes de testar (primeiras requests são mais lentas)
2. **Múltiplas iterações** para médias confiáveis
3. **Monitorar recursos** do servidor durante testes
4. **Variar payload** para simular cenários reais

---

## 🎓 Recursos de Aprendizado

- **Swagger UI**: http://localhost/api/docs/ - Documentação interativa
- **ReDoc**: http://localhost/api/redoc/ - Documentação alternativa
- **Django Admin**: http://localhost/admin/ - Interface administrativa
- **Postman Learning**: https://learning.postman.com/
- **Insomnia Docs**: https://docs.insomnia.rest/

---

**🚀 Agora você está pronto para testar a API Conectades com Insomnia ou Postman!**

