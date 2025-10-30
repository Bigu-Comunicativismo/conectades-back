# 📋 RESUMO RÁPIDO - Backend para Frontend

## 🚀 O que mudou

### **1. Cadastro agora é por LINK DE ATIVAÇÃO** ✉️
- ❌ **ANTES**: Usuário digitava código de 6 dígitos
- ✅ **AGORA**: Usuário clica no link no email e é ativado automaticamente

### **2. Localizações agora têm ESTRUTURA HIERÁRQUICA** 🏘️
- ❌ **ANTES**: Lista misturada de cidades e bairros
- ✅ **AGORA**: Cidades separadas + bairros agrupados por cidade

---

## 📡 Endpoints Principais

### **Buscar Opções de Cadastro**
```http
GET /api/auth/opcoes/
```
Retorna:
- Tipos de usuário (Beneficiária, Doadora)
- Gêneros
- Categorias de interesse
- **Cidades** (3 cidades)
- **Bairros por cidade** (139 bairros organizados)

### **Criar Conta**
```http
POST /api/auth/registro/iniciar/
```
Envia:
```json
{
  "nome_completo": "Maria Silva",
  "email": "maria@example.com",
  "password": "senha123",
  "cpf": "12345678900",
  "telefone": "81987654321",
  "tipo_usuario": 1,
  "genero": 1,
  "cidade": "Recife",
  "bairro": "Coque"
}
```

Responde:
```json
{
  "message": "Link de ativação enviado para seu email",
  "validade": "24 horas"
}
```

### **Ativar Conta (automático via link)**
```http
GET /api/auth/registro/ativar/<token>/
```
- Usuário clica no link do email
- Backend ativa a conta
- Redireciona para: `/auth/ativacao-sucesso?access=TOKEN&refresh=TOKEN`

---

## 💻 Implementação - Dropdowns de Cidade/Bairro

### **JavaScript Vanilla**
```javascript
// 1. Buscar opções
const response = await fetch('/api/auth/opcoes/');
const data = await response.json();

// 2. Popular cidades
data.cidades.forEach(cidade => {
  cidadeSelect.innerHTML += `<option value="${cidade.nome}">${cidade.nome}</option>`;
});

// 3. Quando selecionar cidade, popular bairros
cidadeSelect.addEventListener('change', (e) => {
  const bairros = data.bairros_por_cidade[e.target.value] || [];
  bairroSelect.innerHTML = '<option>Selecione seu bairro</option>';
  bairros.forEach(bairro => {
    bairroSelect.innerHTML += `<option value="${bairro.id}">${bairro.nome}</option>`;
  });
});
```

### **React**
```jsx
const [cidadeSelecionada, setCidadeSelecionada] = useState('');
const [bairros, setBairros] = useState([]);

useEffect(() => {
  if (cidadeSelecionada && opcoes) {
    setBairros(opcoes.bairros_por_cidade[cidadeSelecionada] || []);
  }
}, [cidadeSelecionada]);
```

---

## 🎨 Fluxo de Cadastro

```
1. Usuário preenche formulário
         ↓
2. POST /api/auth/registro/iniciar/
         ↓
3. Mostrar mensagem: "Email enviado!"
         ↓
4. Usuário clica no link no email
         ↓
5. GET /api/auth/registro/ativar/<token>/
         ↓
6. Redireciona para: /auth/ativacao-sucesso?access=...&refresh=...
         ↓
7. Frontend salva tokens e loga usuário
         ↓
8. Redireciona para home
```

---

## 📊 Dados Disponíveis

### **Cidades (3)**
- Recife
- Olinda  
- Jaboatão dos Guararapes

### **Bairros (139 total)**
- Recife: 94 bairros (Coque, Boa Viagem, Afogados, etc.)
- Olinda: 33 bairros (Casa Caiada, Bairro Novo, etc.)
- Jaboatão: 12 bairros (Piedade, Candeias, etc.)

---

## ⚠️ Importante

### **Campos Obrigatórios no Cadastro**
- `nome_completo`
- `email`
- `password` (mínimo 8 caracteres)
- `cpf` (11 dígitos)
- `telefone`
- `tipo_usuario` (ID: 1 ou 2)
- `genero` (ID)
- `cidade` (string: "Recife", "Olinda", etc.)
- `bairro` (string: "Coque", "Boa Viagem", etc.)

### **Timeouts**
- Link de ativação: **24 horas**
- Access Token: **5 minutos**
- Refresh Token: **7 dias**

### **Validações**
- CPF: 11 dígitos
- Telefone: mínimo 10 dígitos
- Senha: mínimo 8 caracteres
- Email: formato válido

---

## 📚 Documentação Completa

### **Guias Detalhados:**
1. **GUIA_FRONTEND_LOCALIZACOES.md** - Tudo sobre cidades/bairros
   - Exemplos em JavaScript, React, Vue
   - 2 opções de implementação
   - FAQ e troubleshooting

2. **GUIA_FRONTEND_CADASTRO.md** - Fluxo completo de cadastro
   - Código pronto para copiar
   - Tratamento de erros
   - Dicas de UX

### **Swagger (API interativa):**
```
https://api.conectades.com/api/docs/
```

---

## 🎯 Próximos Passos

1. ✅ Implementar dropdowns de cidade → bairro
2. ✅ Atualizar formulário de cadastro (novos campos)
3. ✅ Criar página "Email enviado"
4. ✅ Criar página de ativação bem-sucedida
5. ✅ Salvar tokens JWT após ativação
6. ✅ Testar fluxo completo

---

## 💡 Dicas de UX

### **Página "Email Enviado"**
```
📧 Email enviado!

Enviamos um link de ativação para seu email.

Próximos passos:
1. Abra sua caixa de entrada
2. Procure por "Conectades"
3. Clique no link de ativação
4. Pronto! Sua conta será ativada automaticamente

⚠️ O link expira em 24 horas
💡 Não encontrou? Verifique o spam
```

### **Dropdown de Bairros**
- Usar biblioteca de select com busca (muitos bairros!)
- Desabilitar até selecionar cidade
- Placeholder: "Primeiro selecione uma cidade"

### **Loading States**
- "Carregando opções..."
- "Criando conta..."
- "Ativando conta..."

---

## 🚨 Erros Comuns

### **Email já cadastrado**
```json
{
  "email": ["user with this email already exists."]
}
```
**Ação:** Redirecionar para login ou recuperação de senha

### **Token expirado**
```json
{
  "error": "Token expirado"
}
```
**Ação:** Mostrar mensagem e pedir para se cadastrar novamente

### **CPF já cadastrado**
```json
{
  "cpf": ["pessoa with this cpf already exists."]
}
```
**Ação:** Mostrar erro e sugerir contato com suporte

---

## 📞 Contato

Dúvidas? Problemas? Entre em contato com o time de backend.

**Documentação:** `/api/docs/`  
**Repositório:** https://github.com/Bigu-Comunicativismo/conectades-back

---

**Última atualização:** 30/10/2025  
**Versão:** 1.0.0  
**Status:** ✅ Pronto para integração

