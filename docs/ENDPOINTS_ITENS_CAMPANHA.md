# 📦 Endpoints de Itens de Campanha

Este documento descreve os endpoints para gerenciar itens de doação em campanhas.

---

## 📌 **Visão Geral**

Os itens de campanha representam os produtos/serviços que uma campanha precisa receber como doação.

**Regras de Negócio:**
- ✅ Apenas a **organizadora** da campanha pode cadastrar, editar ou deletar itens
- ✅ Qualquer pessoa pode **listar** os itens de uma campanha pública
- ✅ Cada item tem quantidade solicitada e quantidade já contribuída
- ✅ Os itens são únicos por campanha (não pode ter item duplicado com mesmo nome)

---

## 🔗 **Endpoints Disponíveis**

### 1. **Listar Itens de uma Campanha**

**Endpoint:** `GET /api/campanhas/{campanha_id}/itens/`

**Autenticação:** Não requerida (público)

**Descrição:** Lista todos os itens solicitados em uma campanha.

**Resposta de Sucesso (200):**

```json
[
  {
    "id": 1,
    "campanha": 5,
    "nome": "Arroz tipo 1",
    "quantidade_solicitada": 50,
    "quantidade_contribuida": 20,
    "unidade": "kg",
    "percentual_atingido": 40.0,
    "data_criacao": "2025-11-01T10:00:00Z"
  },
  {
    "id": 2,
    "campanha": 5,
    "nome": "Feijão carioca",
    "quantidade_solicitada": 30,
    "quantidade_contribuida": 30,
    "unidade": "kg",
    "percentual_atingido": 100.0,
    "data_criacao": "2025-11-01T10:05:00Z"
  }
]
```

---

### 2. **Cadastrar Item em Campanha**

**Endpoint:** `POST /api/campanhas/{campanha_id}/itens/cadastrar/`

**Autenticação:** ✅ Requerida (Bearer Token)

**Permissão:** Apenas a organizadora da campanha

**Descrição:** Cadastra um novo item de doação em uma campanha.

**Body (JSON):**

```json
{
  "nome": "Arroz tipo 1",
  "quantidade_solicitada": 50,
  "unidade": "kg"
}
```

**Campos:**
- `nome` (string, obrigatório): Nome do item
- `quantidade_solicitada` (integer, obrigatório): Quantidade total solicitada
- `unidade` (string, opcional): Unidade de medida (padrão: "unidade")

**Resposta de Sucesso (201):**

```json
{
  "message": "Item \"Arroz tipo 1\" cadastrado com sucesso!",
  "data": {
    "id": 1,
    "campanha": 5,
    "nome": "Arroz tipo 1",
    "quantidade_solicitada": 50,
    "quantidade_contribuida": 0,
    "unidade": "kg",
    "percentual_atingido": 0.0,
    "data_criacao": "2025-11-01T10:00:00Z"
  }
}
```

**Erros Possíveis:**
- **400 Bad Request**: Dados inválidos ou item duplicado
- **403 Forbidden**: Usuário não é a organizadora da campanha
- **404 Not Found**: Campanha não encontrada

---

### 3. **Editar Item de Campanha**

**Endpoint:** `PUT /api/campanhas/itens/{item_id}/` ou `PATCH /api/campanhas/itens/{item_id}/`

**Autenticação:** ✅ Requerida (Bearer Token)

**Permissão:** Apenas a organizadora da campanha

**Descrição:** Edita um item existente.

- `PUT`: Atualização completa (todos os campos obrigatórios)
- `PATCH`: Atualização parcial (apenas campos enviados)

**Body (JSON - exemplo PATCH):**

```json
{
  "quantidade_solicitada": 60,
  "unidade": "pacotes"
}
```

**Resposta de Sucesso (200):**

```json
{
  "message": "Item \"Arroz tipo 1\" atualizado com sucesso!",
  "data": {
    "id": 1,
    "campanha": 5,
    "nome": "Arroz tipo 1",
    "quantidade_solicitada": 60,
    "quantidade_contribuida": 20,
    "unidade": "pacotes",
    "percentual_atingido": 33.33,
    "data_criacao": "2025-11-01T10:00:00Z"
  }
}
```

**Erros Possíveis:**
- **400 Bad Request**: Dados inválidos
- **403 Forbidden**: Usuário não é a organizadora
- **404 Not Found**: Item não encontrado

---

### 4. **Deletar Item de Campanha**

**Endpoint:** `DELETE /api/campanhas/itens/{item_id}/deletar/`

**Autenticação:** ✅ Requerida (Bearer Token)

**Permissão:** Apenas a organizadora da campanha

**Descrição:** Deleta um item de campanha permanentemente.

**⚠️ Atenção:** Esta ação **não pode ser desfeita**!

**Resposta de Sucesso (200):**

```json
{
  "message": "Item \"Arroz tipo 1\" deletado com sucesso!"
}
```

**Erros Possíveis:**
- **403 Forbidden**: Usuário não é a organizadora
- **404 Not Found**: Item não encontrado

---

## 📋 **Exemplo de Fluxo Completo**

### **Cenário:** Organizadora criando campanha com itens

```bash
# 1. Criar campanha (retorna campanha_id = 5)
POST /api/campanhas/criar/
Authorization: Bearer {token}

# 2. Cadastrar primeiro item
POST /api/campanhas/5/itens/cadastrar/
Authorization: Bearer {token}
{
  "nome": "Arroz tipo 1",
  "quantidade_solicitada": 50,
  "unidade": "kg"
}

# 3. Cadastrar segundo item
POST /api/campanhas/5/itens/cadastrar/
Authorization: Bearer {token}
{
  "nome": "Feijão carioca",
  "quantidade_solicitada": 30,
  "unidade": "kg"
}

# 4. Editar quantidade do primeiro item
PATCH /api/campanhas/itens/1/
Authorization: Bearer {token}
{
  "quantidade_solicitada": 60
}

# 5. Listar todos os itens (público)
GET /api/campanhas/5/itens/

# 6. Deletar item (se necessário)
DELETE /api/campanhas/itens/2/deletar/
Authorization: Bearer {token}
```

---

## 🔒 **Segurança e Validações**

### **Validações Automáticas:**

1. **Unicidade:** Não pode haver dois itens com o mesmo nome na mesma campanha
2. **Quantidade:** `quantidade_solicitada` deve ser um número positivo
3. **Permissões:** Apenas a organizadora pode modificar itens
4. **Integridade:** `quantidade_contribuida` é read-only (atualizado automaticamente pelas doações)

### **Cache:**

Os endpoints invalidam automaticamente o cache quando há modificações:
- Cache da campanha específica
- Cache das campanhas do usuário

---

## 📊 **Campos Calculados**

### `percentual_atingido`

Calcula automaticamente o percentual de doações recebidas:

```python
percentual = (quantidade_contribuida / quantidade_solicitada) * 100
```

**Exemplo:**
- Solicitado: 50 kg
- Contribuído: 20 kg
- Percentual: 40%

---

## 🌐 **Testando no Swagger UI**

Acesse: `http://srv1037558.hstgr.cloud:8001/api/docs/`

**Endpoints disponíveis na seção "Campanhas":**

1. `POST /api/campanhas/{campanha_id}/itens/cadastrar/` - Cadastrar Item
2. `PUT /api/campanhas/itens/{item_id}/` - Editar Item (completo)
3. `PATCH /api/campanhas/itens/{item_id}/` - Editar Item (parcial)
4. `DELETE /api/campanhas/itens/{item_id}/deletar/` - Deletar Item
5. `GET /api/campanhas/{campanha_id}/itens/` - Listar Itens

**Para testar com autenticação:**
1. Clique em "Authorize" (canto superior direito)
2. Insira: `Bearer {seu_token}`
3. Clique em "Authorize"
4. Agora você pode testar os endpoints autenticados ✅

---

## 🐛 **Tratamento de Erros Comuns**

### **400 Bad Request - Item Duplicado**

```json
{
  "campanha": [
    "Os campos campanha, nome must make a unique set."
  ]
}
```

**Solução:** Altere o nome do item ou edite o item existente.

---

### **403 Forbidden - Não é organizadora**

```json
{
  "error": "Apenas a organizadora pode adicionar itens à campanha"
}
```

**Solução:** Apenas quem criou a campanha pode modificar seus itens.

---

### **404 Not Found - Campanha não existe**

```json
{
  "error": "Campanha não encontrada"
}
```

**Solução:** Verifique se o `campanha_id` está correto.

---

## ✅ **Resumo**

| Endpoint | Método | Autenticação | Descrição |
|----------|--------|-------------|-----------|
| `/api/campanhas/{campanha_id}/itens/` | GET | ❌ Não | Listar itens |
| `/api/campanhas/{campanha_id}/itens/cadastrar/` | POST | ✅ Sim | Cadastrar item |
| `/api/campanhas/itens/{item_id}/` | PUT/PATCH | ✅ Sim | Editar item |
| `/api/campanhas/itens/{item_id}/deletar/` | DELETE | ✅ Sim | Deletar item |

---

**🎯 Próximos Passos:**

Agora que os itens estão cadastrados, você pode:
1. Publicar a campanha
2. Permitir que doadoras façam doações para os itens
3. Acompanhar o progresso através do `percentual_atingido`

---

**📝 Atualizado em:** 06/11/2025

