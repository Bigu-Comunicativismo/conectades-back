# 👩‍💼 Lógica da Organizadora - Conectades

Este documento explica como funciona a lógica de Organizadora no sistema.

---

## 🎯 **Conceito Principal**

**Organizadora NÃO é um tipo de usuário**, mas sim uma **Doadora que cria campanhas**.

---

## 📊 **Tipos de Usuário (Apenas 2)**

### **1. Beneficiária**
- 👤 Pessoa que **recebe** doações
- ❌ **NÃO pode** criar campanhas
- ✅ Pode ter campanhas criadas para ela

### **2. Doadora**
- 👤 Pessoa que **faz** doações
- ✅ **PODE** criar campanhas
- ✅ Ao criar a primeira campanha, automaticamente vira **Organizadora**

---

## 🔄 **Como uma Doadora se torna Organizadora**

### **Fluxo Automático:**

```
1. Usuária se cadastra como "Doadora"
   ↓
2. Doadora decide criar uma campanha
   ↓
3. Sistema verifica: "É Doadora?" ✅
   ↓
4. Sistema cria perfil de Organizadora automaticamente
   ↓
5. Campanha é criada e associada à Organizadora
   ↓
6. Doadora agora também é Organizadora! 🎉
```

---

## 🏗️ **Estrutura no Banco de Dados**

### **Tabela: `pessoas_pessoa`**
```sql
Pessoa (tipo_usuario = "Doadora")
  ↓
  ├── pode fazer doações
  └── pode criar campanhas
```

### **Tabela: `campanhas_organizadora`**
```sql
Organizadora (pessoa_id → Pessoa)
  ↓
  └── é uma Doadora que criou pelo menos 1 campanha
```

### **Relação:**
```
Pessoa (Doadora)
    ↓ (1:1)
Organizadora
    ↓ (1:N)
Campanhas
```

---

## 💻 **Implementação no Admin Django**

### **Menu "Usuáries":**
- ✅ Tipos de Usuário (2: Beneficiária, Doadora)
- ✅ Gêneros (10 opções)
- ✅ Categorias de Interesse (11 categorias)
- ✅ Localizações de Interesse (103+ localizações)
- ✅ Pessoas (lista de todos os usuários)

### **Menu "Campanhas":**
- ✅ Campanhas (com lógica automática)
- ❌ ~~Organizadoras~~ (NÃO aparece - criada automaticamente)

---

## 🛡️ **Proteções Implementadas**

### **1. Verificação de Tipo de Usuário:**

```python
# Antes de criar campanha
if usuario.tipo_usuario != "Doadora":
    return Error("Apenas Doadoras podem criar campanhas!")
```

### **2. Criação Automática:**

```python
# Ao criar campanha
organizadora, created = Organizadora.objects.get_or_create(
    pessoa=request.user
)

if created:
    mensagem = "🎉 Parabéns! Você agora é uma Organizadora!"
```

---

## 🌐 **Exemplos de Uso**

### **1. Via Admin Django:**

#### **Beneficiária tenta criar campanha:**
1. Login como Beneficiária
2. Tenta acessar "Adicionar Campanha"
3. ❌ Sistema bloqueia: "Apenas Doadoras podem criar campanhas!"

#### **Doadora cria primeira campanha:**
1. Login como Doadora
2. Vai em "Campanhas" → "Adicionar Campanha"
3. Preenche:
   - Título: "Ajuda para Mulheres"
   - Descrição: "..."
   - Beneficiária: (seleciona uma)
   - Data início/fim
4. Salva
5. ✨ Sistema automaticamente:
   - Cria perfil de Organizadora
   - Associa campanha à Organizadora
   - Mostra: "🎉 Parabéns! Você agora é uma Organizadora!"

#### **Doadora cria segunda campanha:**
1. Vai em "Campanhas" → "Adicionar Campanha"
2. Preenche dados
3. Salva
4. ✅ Usa o perfil de Organizadora existente (sem criar novo)

---

### **2. Via API:**

#### **Cadastrar como Doadora:**
```bash
POST /api/cadastro/criar/
{
  "username": "maria",
  "password": "Senha123",
  "nome_completo": "Maria Silva",
  "cpf": "123.456.789-00",
  "telefone": "(81) 99999-9999",
  "email": "maria@email.com",
  "tipo_usuario": 2,  # ID do tipo "Doadora"
  "genero": 1,
  "cidade": "Recife",
  "bairro": "Boa Viagem",
  "nome_social": "Maria",
  "mini_bio": "...",
  "categorias_interesse": [1, 2],
  "localizacoes_interesse": [1]
}
```

#### **Criar primeira campanha (vira Organizadora):**
```bash
POST /api/campanhas/criar/
Authorization: Bearer {token_da_maria}
{
  "titulo": "Campanha Solidária",
  "descricao": "Ajuda para mulheres...",
  "beneficiaria_id": 5,
  "data_inicio": "2025-10-20",
  "data_fim": "2025-11-20"
}

# Resposta:
{
  "message": "Campanha criada com sucesso! 🎉 Você agora é uma Organizadora!",
  "organizadora_criada": true,
  "data": { ... }
}
```

#### **Beneficiária tenta criar campanha:**
```bash
POST /api/campanhas/criar/
Authorization: Bearer {token_da_beneficiaria}
{ ... }

# Resposta:
{
  "error": "Apenas Doadoras podem criar campanhas!",
  "tipo_usuario_atual": "Beneficiária",
  "tipo_necessario": "Doadora"
}

Status: 403 FORBIDDEN
```

---

## 🔍 **Verificando se uma Pessoa é Organizadora**

### **Via Python/Django:**
```python
from backend.campanhas.models import Organizadora

# Verificar se usuária é organizadora
if Organizadora.objects.filter(pessoa=usuario, ativo=True).exists():
    print("Usuária é uma Organizadora!")
else:
    print("Usuária ainda não criou campanhas")
```

### **Via API:**
```bash
# Listar minhas campanhas (só funciona se for organizadora)
GET /api/campanhas/minhas/
Authorization: Bearer {token}

# Se não tiver campanhas, retorna lista vazia []
# Se tiver, lista todas as campanhas criadas
```

---

## 📋 **Regras de Negócio**

### ✅ **Permitido:**
- Beneficiária receber doações
- Doadora fazer doações
- Doadora criar campanhas (vira Organizadora)
- Organizadora criar múltiplas campanhas
- Organizadora desativar/editar suas campanhas

### ❌ **Bloqueado:**
- Beneficiária criar campanhas
- Beneficiária se tornar Organizadora
- Criar Organizadora manualmente no admin
- Editar o tipo de uma Organizadora de "Doadora" para "Beneficiária"

---

## 🎨 **Diagrama de Estados**

```
┌─────────────────┐
│  Beneficiária   │
│                 │
│ - Recebe ajuda  │
│ - NÃO cria      │
│   campanhas     │
└─────────────────┘

┌─────────────────┐      ┌──────────────────┐
│    Doadora      │ ───► │  Organizadora    │
│                 │      │  (perfil extra)  │
│ - Faz doações   │      │                  │
│ - PODE criar    │      │ - Gerencia       │
│   campanhas     │      │   campanhas      │
└─────────────────┘      └──────────────────┘
                             ▲
                             │
                    Criada automaticamente
                    ao criar 1ª campanha
```

---

## 🔧 **Para Desenvolvedores**

### **Arquivos Modificados:**

1. **`backend/campanhas/admin.py`**:
   - Removido `@admin.register(Organizadora)`
   - Adicionada verificação de tipo em `save_model()`
   - Campo organizadora oculto no form

2. **`backend/campanhas/views.py`**:
   - Verificação de tipo antes de criar campanha
   - Criação automática de Organizadora
   - Mensagem de sucesso personalizada

3. **`backend/pessoas/models.py`**:
   - Apenas 2 tipos: Beneficiária e Doadora
   - Sem tipo "Organizadora"

---

## 🧪 **Testando a Lógica**

### **Teste 1: Doadora cria campanha**
```bash
# 1. Criar usuária Doadora
# 2. Fazer login
# 3. Criar campanha
# ✅ Esperado: Campanha criada + Organizadora criada automaticamente
```

### **Teste 2: Beneficiária tenta criar campanha**
```bash
# 1. Criar usuária Beneficiária
# 2. Fazer login
# 3. Tentar criar campanha
# ✅ Esperado: Erro 403 - "Apenas Doadoras podem criar campanhas!"
```

### **Teste 3: Organizadora cria segunda campanha**
```bash
# 1. Login como Doadora que já criou campanha
# 2. Criar nova campanha
# ✅ Esperado: Campanha criada (sem criar nova Organizadora)
```

---

## 📝 **Resumo**

| Item | Descrição | Status |
|------|-----------|--------|
| **Tipos de Usuário** | Beneficiária e Doadora | ✅ |
| **Organizadora** | Perfil automático de Doadora | ✅ |
| **Criação Manual** | Bloqueada no admin | ✅ |
| **Criação Automática** | Ao criar primeira campanha | ✅ |
| **Verificação de Tipo** | Apenas Doadora pode criar | ✅ |
| **Admin Limpo** | Organizadora não aparece | ✅ |

---

**A lógica está correta e segue o fluxo natural do negócio!** ✅

**Desenvolvido por Bigu Comunicativismo**

