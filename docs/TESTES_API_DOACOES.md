# 🧪 Testes de API de Doações

## 📋 Visão Geral

Este documento descreve como testar as funcionalidades de doações através da API REST, sem precisar acessar o Django Admin.

## 🎯 Endpoints Disponíveis

### **Doações (Doadora)**

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `GET` | `/api/doacoes/minhas/` | Lista doações criadas pela doadora | Doadora |
| `GET` | `/api/doacoes/<id>/` | Detalhes de uma doação | Doadora/Beneficiária/Admin |
| `PATCH` | `/api/doacoes/<id>/atualizar-status/` | Cancelar doação | Doadora |
| `POST` | `/api/doacoes/criar/` | Criar nova doação | Doadora |

### **Doações (Beneficiária)**

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| `GET` | `/api/doacoes/minhas-campanhas/` | Lista doações recebidas | Beneficiária |
| `PATCH` | `/api/doacoes/<id>/atualizar-status/` | Atualizar status e data de entrega | Beneficiária |

---

## 🚀 Como Usar

### **1. Instalar Dependências**

```bash
cd /home/lelo/conectades
source venv/bin/activate
pip install requests  # Se ainda não estiver instalado
```

### **2. Iniciar o Servidor**

```bash
cd backend
python manage.py runserver 8001
```

### **3. Executar Script de Teste**

```bash
cd /home/lelo/conectades
python backend/test_api_doacoes.py
```

---

## 📝 Testes Manuais com cURL

### **1. Fazer Login e Obter Token**

```bash
# Login como Doadora (Ana Costa)
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ana.costa",
    "password": "senha123"
  }'

# Resposta:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
# }
```

**Salve o token `access` para usar nos próximos comandos!**

---

### **2. Testes como Doadora (Ana Costa)**

#### **Listar Minhas Doações**

```bash
TOKEN="SEU_TOKEN_AQUI"

curl -X GET http://localhost:8001/api/doacoes/minhas/ \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada:**
```json
[
  {
    "id": 21,
    "campanha_titulo": "Roupas de Inverno para Moradores de Rua",
    "doador_nome": "Ana Costa",
    "item_campanha_nome": "Leite em pó",
    "quantidade": 13,
    "unidade": "latas",
    "status": "confirmada",
    "data_doacao": "2025-10-20T02:53:38.696166Z",
    "data_entrega": null
  }
]
```

#### **Cancelar uma Doação**

```bash
TOKEN="SEU_TOKEN_AQUI"
DOACAO_ID=21

curl -X PATCH "http://localhost:8001/api/doacoes/$DOACAO_ID/atualizar-status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelada",
    "observacoes": "Não poderei entregar esta doação"
  }'
```

**Resposta esperada:**
```json
{
  "mensagem": "Doação atualizada com sucesso",
  "doacao": {
    "id": 21,
    "status": "cancelada",
    "observacoes": "Não poderei entregar esta doação"
  }
}
```

#### **Tentar Alterar Data de Entrega (DEVE FALHAR)**

```bash
TOKEN="SEU_TOKEN_AQUI"
DOACAO_ID=21

curl -X PATCH "http://localhost:8001/api/doacoes/$DOACAO_ID/atualizar-status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_entrega": "2025-10-20"
  }'
```

**Resposta esperada (Erro 403):**
```json
{
  "erro": "Doadora não pode alterar a data de entrega"
}
```

---

### **3. Testes como Beneficiária (Carla Oliveira)**

#### **Login**

```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "carla.oliveira",
    "password": "senha123"
  }'
```

#### **Listar Doações Recebidas**

```bash
TOKEN="SEU_TOKEN_BENEFICIARIA_AQUI"

curl -X GET http://localhost:8001/api/doacoes/minhas-campanhas/ \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada:**
```json
[
  {
    "id": 17,
    "campanha_titulo": "Campanha de Alimentos para Famílias Carentes",
    "doador_nome": "Julia Ferreira",
    "item_campanha_nome": "Leite em pó",
    "quantidade": 17,
    "unidade": "latas",
    "status": "confirmada",
    "data_doacao": "2025-10-20T02:53:38.677654Z",
    "data_entrega": null
  },
  {
    "id": 16,
    "campanha_titulo": "Campanha de Alimentos para Famílias Carentes",
    "doador_nome": "Julia Ferreira",
    "item_campanha_nome": "Arroz tipo 1",
    "quantidade": 6,
    "unidade": "kg",
    "status": "entregue",
    "data_doacao": "2025-10-20T02:53:38.667834Z",
    "data_entrega": "2025-10-17"
  }
]
```

#### **Confirmar uma Doação Pendente**

```bash
TOKEN="SEU_TOKEN_BENEFICIARIA_AQUI"
DOACAO_ID=17

curl -X PATCH "http://localhost:8001/api/doacoes/$DOACAO_ID/atualizar-status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmada",
    "observacoes": "Doação confirmada, aguardando entrega"
  }'
```

#### **Atualizar para "Entregue" e Definir Data de Entrega**

```bash
TOKEN="SEU_TOKEN_BENEFICIARIA_AQUI"
DOACAO_ID=17

curl -X PATCH "http://localhost:8001/api/doacoes/$DOACAO_ID/atualizar-status/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "entregue",
    "data_entrega": "2025-10-20",
    "observacoes": "Doação recebida com sucesso! Muito obrigada!"
  }'
```

**Resposta esperada:**
```json
{
  "mensagem": "Doação atualizada com sucesso",
  "doacao": {
    "id": 17,
    "status": "entregue",
    "data_entrega": "2025-10-20",
    "observacoes": "Doação recebida com sucesso! Muito obrigada!"
  }
}
```

---

## 🔐 Credenciais para Teste

### **Doadoras:**

| Nome | Email | Senha | Permissões |
|------|-------|-------|-----------|
| Ana Costa | `ana.costa@exemplo.com` | `senha123` | Cancelar suas doações |
| Julia Ferreira | `julia.ferreira@exemplo.com` | `senha123` | Cancelar suas doações |
| Maria Silva | `maria.silva@exemplo.com` | `senha123` | Cancelar suas doações |

### **Beneficiárias:**

| Nome | Email | Senha | Permissões |
|------|-------|-------|-----------|
| Carla Oliveira | `carla.oliveira@exemplo.com` | `senha123` | Atualizar status e data de entrega |
| Fernanda Lima | `fernanda.lima@exemplo.com` | `senha123` | Atualizar status e data de entrega |

### **Admin:**

| Nome | Username | Senha | Permissões |
|------|----------|-------|-----------|
| Admin | `admin` | `admin` | Acesso total |

---

## 📊 Regras de Negócio

### **✅ Doadora Pode:**
- ✅ Criar doações
- ✅ Listar suas próprias doações
- ✅ Cancelar suas doações (status → `cancelada`)
- ✅ Adicionar observações

### **❌ Doadora NÃO Pode:**
- ❌ Alterar data de entrega
- ❌ Alterar status para `confirmada` ou `entregue`
- ❌ Ver doações de outras doadoras
- ❌ Editar quantidade ou item após criação

### **✅ Beneficiária Pode:**
- ✅ Ver doações de suas campanhas
- ✅ Atualizar status (`pendente` → `confirmada` → `entregue`)
- ✅ Definir data de entrega ⭐
- ✅ Adicionar observações
- ✅ Cancelar doações

### **❌ Beneficiária NÃO Pode:**
- ❌ Ver doações de outras beneficiárias
- ❌ Editar quantidade ou item após criação

### **✅ Admin Pode:**
- ✅ Fazer tudo

---

## 🎯 Cenários de Teste

### **Cenário 1: Doadora Cancela Doação**
1. Login como doadora
2. Listar suas doações
3. Cancelar uma doação pendente
4. **Resultado:** Status muda para `cancelada`, progresso da campanha atualiza

### **Cenário 2: Beneficiária Confirma Recebimento**
1. Login como beneficiária
2. Listar doações recebidas
3. Atualizar status para `entregue` e definir data de entrega
4. **Resultado:** Status muda, data é salva, progresso da campanha atualiza

### **Cenário 3: Doadora Tenta Editar Data (Bloqueio)**
1. Login como doadora
2. Tentar atualizar data de entrega de uma doação
3. **Resultado:** Erro 403 - "Doadora não pode alterar a data de entrega"

### **Cenário 4: Beneficiária Vê Apenas Suas Campanhas**
1. Login como Carla (beneficiária)
2. Listar doações
3. **Resultado:** Vê apenas doações de suas campanhas, não de outras

---

## 🐛 Troubleshooting

### **Erro: "Connection refused"**
- ✅ Certifique-se de que o servidor está rodando: `python manage.py runserver 8001`

### **Erro: "Invalid token"**
- ✅ Faça login novamente para obter um token válido
- ✅ Tokens JWT expiram após algum tempo

### **Erro 403: "Você não tem permissão"**
- ✅ Verifique se está usando o token correto (doadora vs beneficiária)
- ✅ Verifique se está tentando acessar uma doação permitida

### **Erro 404: "Doação não encontrada"**
- ✅ Verifique se o ID da doação existe
- ✅ Use `/api/doacoes/minhas/` para listar IDs válidos

---

## 📚 Documentação OpenAPI (Swagger)

Acesse a documentação interativa em:

- **Swagger UI:** http://localhost:8001/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8001/api/schema/redoc/
- **JSON Schema:** http://localhost:8001/api/schema/

---

## ✅ Checklist de Testes

- [ ] Doadora consegue listar suas doações
- [ ] Doadora consegue cancelar suas doações
- [ ] Doadora NÃO consegue alterar data de entrega
- [ ] Beneficiária consegue listar doações de suas campanhas
- [ ] Beneficiária consegue atualizar status para `entregue`
- [ ] Beneficiária consegue definir data de entrega
- [ ] Progresso da campanha atualiza automaticamente
- [ ] Doadora não vê doações de outras doadoras
- [ ] Beneficiária não vê doações de outras beneficiárias

---

**Pronto para testar! 🚀**

