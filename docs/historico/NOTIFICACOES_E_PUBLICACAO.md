# 📬 Sistema de Notificações e Publicação de Campanhas

## 📋 Visão Geral

Sistema completo de notificações por email e controle de publicação de campanhas baseado na confirmação da beneficiária.

---

## ✨ Funcionalidades Implementadas

### **1. Notificação por Email** 📧

Quando uma organizadora adiciona uma beneficiária a uma campanha:

1. ✅ **Solicitação criada automaticamente** (Django Signal)
2. ✅ **Email enviado automaticamente** para a beneficiária
3. ✅ **Email contém:**
   - Nome da campanha
   - Nome da organizadora
   - Mensagem da organizadora
   - Instruções para aceitar/recusar
   - Link para a API

**Exemplo de Email:**
```
Assunto: 🎯 Nova Solicitação de Campanha - Campanha de Alimentos

Olá, Carla Oliveira! 👋

Você recebeu uma nova solicitação para ser beneficiária de uma campanha!

📋 Campanha: Campanha de Alimentos
👤 Organizadora: Maria Silva

�� Mensagem da Organizadora:
A organizadora Maria Silva gostaria de associar você como beneficiária...

Para aceitar ou recusar:
1. Acesse o aplicativo Conectades
2. Vá em "Minhas Solicitações"
3. Veja os detalhes
4. Escolha "Aceitar" ou "Recusar"
```

---

### **2. Campo `publicada` em Campanha** 🚀

**Regra de Negócio:**
- Campanha SEM beneficiária: pode ser publicada imediatamente
- Campanha COM beneficiária: **só pode ser publicada após confirmação**

**Propriedades:**
- `pode_ser_publicada`: Verifica se pode publicar
- `status_publicacao`: Retorna status visual
- `publicar()`: Publica se as condições forem atendidas
- `despublicar()`: Despublica a campanha

**Status Possíveis:**
- ✅ **Publicada**: Visível para doadores
- ⏳ **Rascunho**: Sem beneficiária
- ⏳ **Pronta para publicar**: Beneficiária confirmou
- ⏳ **Aguardando confirmação**: Beneficiária ainda não respondeu

---

### **3. Validação de Publicação** 🔒

**No Admin:**
- Checkbox "Publicada" só funciona se `pode_ser_publicada == True`
- Mensagem de erro se tentar publicar sem confirmação
- Mensagem de sucesso quando publicar

**Na API:**
- Endpoint `/api/campanhas/listar/` mostra apenas campanhas **publicadas e ativas**
- Endpoint `/api/campanhas/minhas/` mostra todas as campanhas da organizadora (incluindo rascunhos)

---

## 🔄 Fluxo Completo

### **Cenário 1: Campanha SEM Beneficiária**

```
1. Organizadora cria campanha
2. Não adiciona beneficiária
3. ✅ Pode publicar imediatamente
4. Marca como "Publicada"
5. ✅ Aparece na lista pública
```

### **Cenário 2: Campanha COM Beneficiária (Fluxo Feliz)**

```
1. Organizadora cria campanha
2. Adiciona beneficiária (Carla)
3. 🔔 Sistema cria solicitação automaticamente
4. 📧 Email enviado para Carla
5. ⏳ Campanha fica como "Aguardando confirmação"
6. ❌ Campanha NÃO pode ser publicada ainda
7. Carla faz login
8. Carla vê solicitação pendente
9. ✅ Carla aceita a solicitação
10. ✅ Campo `beneficiaria_confirmada = True`
11. ✅ Campanha pode ser publicada
12. Organizadora marca como "Publicada"
13. ✅ Aparece na lista pública
```

### **Cenário 3: Beneficiária Recusa**

```
1-7. (igual ao cenário 2)
8. ❌ Carla recusa a solicitação
9. Carla é removida da campanha
10. Campanha volta para "Rascunho"
11. Organizadora pode:
    - Adicionar outra beneficiária
    - Publicar sem beneficiária
    - Cancelar a campanha
```

---

## 🎨 Visualização no Admin

### **Lista de Campanhas**

```
Título          Beneficiária              Status Publicação                Progresso
─────────────────────────────────────────────────────────────────────────────────
Campanha A   ✅ Carla Oliveira         ✅ Publicada                     🟢 75%
Campanha B   ⏳ Fernanda (aguardando)  ⏳ Aguardando confirmação        🟡 50%
Campanha C   -                         ⏳ Rascunho (sem beneficiária)  🔵 25%
```

### **Formulário de Edição**

```
🚀 Publicação
────────────────────────────────────────
Status Publicação: ⏳ Aguardando confirmação da beneficiária
Pode Publicar?: ❌ Aguardando confirmação da beneficiária

☑️ Publicada  (checkbox bloqueado até confirmação)

⚠️ Esta campanha só pode ser publicada após a beneficiária confirmar
```

---

## 🔌 API Endpoints

### **1. Listar Campanhas Públicas**

```bash
GET /api/campanhas/listar/
```

**Retorna:** Apenas campanhas com `publicada=True` e `ativa=True`

### **2. Listar Minhas Campanhas (Organizadora)**

```bash
GET /api/campanhas/minhas/
Authorization: Bearer TOKEN
```

**Retorna:** Todas as campanhas da organizadora (incluindo rascunhos)

### **3. Minhas Solicitações (Beneficiária)**

```bash
GET /api/campanhas/solicitacoes/minhas/
Authorization: Bearer TOKEN
```

**Retorna:** Todas as solicitações pendentes/aceitas/recusadas

---

## 📧 Configuração de Email

**Arquivo:** `backend/pessoas/email_service.py`

**Função:** `enviar_notificacao_solicitacao_beneficiaria(solicitacao)`

**Configuração Django:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'
DEFAULT_FROM_EMAIL = 'Conectades <noreply@conectades.com>'
SITE_URL = 'http://localhost:8001'  # ou domínio de produção
```

---

## 🧪 Como Testar

### **Teste 1: Criar Campanha com Beneficiária**

```bash
# 1. Login como organizadora no admin
http://localhost:8001/admin/
# maria.silva / senha123

# 2. Criar nova campanha
# 3. Adicionar beneficiária: Carla Oliveira
# 4. Salvar

# ✅ Verifique:
# - Solicitação criada automaticamente
# - Email enviado (verificar console/logs)
# - Campanha com status "Aguardando confirmação"
# - Checkbox "Publicada" marcado mas campanha não pode ser publicada
```

### **Teste 2: Beneficiária Aceita**

```bash
# 1. Login como beneficiária via API
curl -X POST http://localhost:8001/api/token/ \
  -d '{"username": "carla.oliveira", "password": "senha123"}'

# 2. Ver solicitações
curl http://localhost:8001/api/campanhas/solicitacoes/minhas/ \
  -H "Authorization: Bearer TOKEN"

# 3. Aceitar solicitação
curl -X POST http://localhost:8001/api/campanhas/solicitacoes/1/aceitar/ \
  -H "Authorization: Bearer TOKEN" \
  -d '{"mensagem": "Aceito!"}'

# 4. Voltar ao admin
# ✅ Status mudou para "Pronta para publicar"
# ✅ Beneficiária: ✅ Carla Oliveira
# ✅ Pode publicar agora!
```

### **Teste 3: Publicar Campanha**

```bash
# 1. No admin, editar a campanha
# 2. Marcar checkbox "Publicada"
# 3. Salvar

# ✅ Mensagem: "Campanha publicada com sucesso!"
# ✅ Status: ✅ Publicada
# ✅ Aparece na API pública (/api/campanhas/listar/)
```

---

## 📊 Benefícios

### **1. Segurança**
- Beneficiária tem controle sobre sua associação
- Não pode ser associada sem consentimento

### **2. Transparência**
- Beneficiária é notificada imediatamente
- Sabe quem a indicou e para qual campanha

### **3. Qualidade**
- Apenas campanhas confirmadas são públicas
- Evita campanhas com informações incorretas

### **4. Comunicação**
- Email automático
- Instruções claras
- API para app mobile

---

## 🔄 Diagrama de Estados

```
┌─────────────┐
│  Campanha   │
│   Criada    │
└──────┬──────┘
       │
       ├──► SEM Beneficiária
       │     └─► ✅ Pode Publicar
       │
       └──► COM Beneficiária
             ├─► 📧 Email Enviado
             ├─► ⏳ Aguardando
             │
             ├──► ✅ Aceita
             │     └─► ✅ Pode Publicar
             │
             └──► ❌ Recusa
                   └─► Volta para Rascunho
```

---

**✅ IMPLEMENTAÇÃO CONCLUÍDA!**

