# 🎯 Sistema de Confirmação de Beneficiária

## 📋 Visão Geral

Sistema que implementa um fluxo de confirmação onde a beneficiária precisa aceitar ser associada a uma campanha.

---

## ✨ Funcionalidades Implementadas

### **1. Modelo `SolicitacaoBeneficiaria`**

Gerencia as solicitações de associação:
- ⏳ **Pendente**: Aguardando resposta da beneficiária
- ✅ **Aceita**: Beneficiária aceitou
- ❌ **Recusada**: Beneficiária recusou

### **2. Campo `beneficiaria_confirmada` em `Campanha`**

- `False`: Beneficiária ainda não confirmou
- `True`: Beneficiária confirmou a associação

### **3. Criação Automática de Solicitações**

Quando uma organizadora adiciona uma beneficiária a uma campanha:
1. Uma **solicitação** é criada automaticamente
2. A beneficiária recebe uma **notificação** (via API)
3. O campo `beneficiaria_confirmada` fica como `False`

### **4. Fluxo de Aceitação/Recusa**

**Aceitar:**
- Beneficiária aceita via API
- `beneficiaria_confirmada` vira `True`
- Solicitação fica como "Aceita"

**Recusar:**
- Beneficiária recusa via API  
- Beneficiária é **removida** da campanha
- Solicitação fica como "Recusada"

---

## 🔌 Endpoints da API

### **1. Listar Minhas Solicitações (Beneficiária)**

```bash
GET /api/campanhas/solicitacoes/minhas/
Authorization: Bearer TOKEN
```

**Resposta:**
```json
[
  {
    "id": 1,
    "campanha": {
      "id": 5,
      "titulo": "Campanha de Alimentos",
      "descricao": "...",
      "imagem": "https://..."
    },
    "organizadora": {
      "id": 2,
      "nome": "Maria Silva"
    },
    "status": "pendente",
    "status_display": "⏳ Pendente",
    "mensagem_organizadora": "Gostaríamos de associar você...",
    "mensagem_resposta": "",
    "data_criacao": "2025-10-20T10:00:00Z",
    "data_resposta": null
  }
]
```

### **2. Aceitar Solicitação**

```bash
POST /api/campanhas/solicitacoes/<id>/aceitar/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "mensagem": "Aceito com prazer! Obrigada pela indicação."
}
```

**Resposta:**
```json
{
  "mensagem": "Solicitação aceita com sucesso!",
  "campanha": {
    "id": 5,
    "titulo": "Campanha de Alimentos"
  }
}
```

### **3. Recusar Solicitação**

```bash
POST /api/campanhas/solicitacoes/<id>/recusar/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "mensagem": "Infelizmente não posso aceitar no momento."
}
```

**Resposta:**
```json
{
  "mensagem": "Solicitação recusada. Você foi removida como beneficiária desta campanha.",
  "campanha": {
    "id": 5,
    "titulo": "Campanha de Alimentos"
  }
}
```

---

## 🎨 Visualização no Admin

### **Lista de Campanhas**

```
Título                          Beneficiária                       Progresso
─────────────────────────────────────────────────────────────────────────────
Campanha de Alimentos    ✅ Carla Oliveira              🟢 75%
Roupas de Inverno        ⏳ Fernanda Lima (aguardando)  🟡 50%
```

**Legenda:**
- ✅ = Beneficiária confirmada
- ⏳ = Aguardando confirmação

### **Solicitações de Beneficiária (Novo Admin)**

```
Solicitação                              Beneficiária    Status        Data
──────────────────────────────────────────────────────────────────────────────
Campanha X → Carla Oliveira         Carla           ✅ Aceita      20/10
Campanha Y → Fernanda Lima          Fernanda        ⏳ Pendente    19/10
Campanha Z → Ana Santos             Ana             ❌ Recusada    18/10
```

---

## 🔄 Fluxo Completo

### **1. Organizadora Cria Campanha**

```python
# Organizadora Maria cria campanha e adiciona Carla como beneficiária
Campanha.objects.create(
    titulo="Campanha de Alimentos",
    organizadora=maria_organizadora,
    beneficiaria=carla,  # ← Adiciona beneficiária
    ...
)
```

### **2. Sinal Cria Solicitação Automaticamente**

```python
# Django Signal cria automaticamente
SolicitacaoBeneficiaria.objects.create(
    campanha=campanha,
    beneficiaria=carla,
    organizadora=maria_organizadora,
    status='pendente',
    mensagem_organizadora="..."
)

# Marca campanha como não confirmada
campanha.beneficiaria_confirmada = False
```

### **3. Carla Recebe Notificação**

```bash
# Carla faz login e vê suas solicitações
GET /api/campanhas/solicitacoes/minhas/
```

### **4. Carla Decide**

**Opção A: Aceitar**
```bash
POST /api/campanhas/solicitacoes/1/aceitar/
{
  "mensagem": "Aceito com prazer!"
}
```
✅ `campanha.beneficiaria_confirmada = True`

**Opção B: Recusar**
```bash
POST /api/campanhas/solicitacoes/1/recusar/
{
  "mensagem": "Não posso no momento"
}
```
❌ `campanha.beneficiaria = None`

---

## 🧪 Como Testar

### **1. Criar Solicitação Manualmente (Admin)**

```bash
# Login no admin como organizadora
http://localhost:8001/admin/

# Criar nova campanha
# Adicionar uma beneficiária (ex: Carla Oliveira)
# Salvar
```

✅ **Solicitação criada automaticamente!**

### **2. Verificar Solicitação (Admin)**

```bash
# Ir para: Solicitações de Beneficiária
http://localhost:8001/admin/campanhas/solicitacaobeneficiaria/
```

### **3. Testar API (Beneficiária)**

```bash
# 1. Login como beneficiária
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "carla.oliveira", "password": "senha123"}'

# 2. Listar solicitações
curl -X GET http://localhost:8001/api/campanhas/solicitacoes/minhas/ \
  -H "Authorization: Bearer TOKEN"

# 3. Aceitar solicitação
curl -X POST http://localhost:8001/api/campanhas/solicitacoes/1/aceitar/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Aceito!"}'
```

---

## 📊 Benefícios

### **1. Transparência**
- Beneficiária sabe que foi indicada
- Pode aceitar ou recusar

### **2. Controle**
- Beneficiária tem autonomia sobre sua participação
- Histórico de solicitações aceitas/recusadas

### **3. Segurança**
- Não é possível adicionar alguém sem seu consentimento
- Todas as ações ficam registradas

### **4. Comunicação**
- Mensagens entre organizadora e beneficiária
- Explicação do motivo da indicação

---

## 🎯 Próximos Passos

- [ ] Notificações por email quando solicitação é criada
- [ ] Notificações push quando solicitação é respondida
- [ ] Dashboard para organizadora ver status de solicitações
- [ ] Prazo de validade para solicitações pendentes

---

**✅ IMPLEMENTAÇÃO CONCLUÍDA!**

