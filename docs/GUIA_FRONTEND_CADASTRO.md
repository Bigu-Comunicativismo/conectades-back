# 📝 Guia de Cadastro e Ativação para o Frontend

## 🎯 Fluxo de Cadastro

O cadastro agora funciona em **2 etapas**:
1. **Usuário preenche formulário** → Backend envia email com link
2. **Usuário clica no link** → Conta é ativada automaticamente

---

## 📡 Endpoints

### **1️⃣ POST `/api/auth/registro/iniciar/`** - Criar conta

**Uso:** Enviar dados do formulário de cadastro

**Request Body:**
```json
{
  // Dados básicos obrigatórios
  "nome_completo": "Maria Silva Santos",
  "nome_social": "Maria Silva",
  "email": "maria@example.com",
  "password": "SenhaSegura123!",
  "cpf": "12345678900",
  "telefone": "81987654321",
  
  // Tipo de usuário e gênero (IDs)
  "tipo_usuario": 1,  // 1 = Beneficiária, 2 = Doadora
  "genero": 1,        // ID do gênero selecionado
  
  // Localização
  "cidade": "Recife",
  "bairro": "Coque",
  
  // Campos opcionais
  "mini_bio": "Texto curto sobre a pessoa",
  "categorias_interesse": [1, 2, 3],        // IDs das categorias
  "localizacoes_interesse": [100, 101, 102] // IDs dos bairros de interesse
}
```

**Resposta de Sucesso (200):**
```json
{
  "message": "Link de ativação enviado para seu email",
  "email": "maria@example.com",
  "validade": "24 horas",
  "proximo_passo": "Clique no link enviado para ativar sua conta"
}
```

**Resposta de Erro (400):**
```json
{
  "email": ["Este campo é obrigatório."],
  "cpf": ["Este CPF já está cadastrado."],
  "password": ["A senha deve ter no mínimo 8 caracteres."]
}
```

---

### **2️⃣ GET `/api/auth/registro/ativar/<token>/`** - Ativar conta

**Uso:** O usuário clica no link recebido por email

**URL Exemplo:**
```
https://api.conectades.com/api/auth/registro/ativar/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

**Comportamento:**
1. Backend valida o token
2. Cria a conta do usuário
3. Retorna página HTML bonita
4. Redireciona automaticamente para o frontend com os tokens JWT

**Redirecionamento:**
```
https://app.conectades.com/auth/ativacao-sucesso?access=TOKEN_ACCESS&refresh=TOKEN_REFRESH
```

**Resposta de Erro (400):**
```json
{
  "error": "Token inválido ou já utilizado"
}
```

```json
{
  "error": "Token expirado"
}
```

```json
{
  "error": "Dados de registro expirados. Inicie o registro novamente."
}
```

---

## 💻 Implementação no Frontend

### **1. Página de Cadastro**

```javascript
const cadastrar = async (formData) => {
  try {
    const response = await fetch('/api/auth/registro/iniciar/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Sucesso - mostrar mensagem
      mostrarMensagemSucesso(
        'Email enviado!',
        `Enviamos um link de ativação para ${data.email}. ` +
        `Clique no link para ativar sua conta. ` +
        `O link expira em ${data.validade}.`
      );
      
      // Redirecionar para página de confirmação
      router.push('/cadastro/email-enviado');
    } else {
      // Erro de validação
      mostrarErrosValidacao(data);
    }
  } catch (error) {
    console.error('Erro ao cadastrar:', error);
    mostrarErroGenerico('Erro ao criar conta. Tente novamente.');
  }
};
```

---

### **2. Página "Email Enviado"**

Criar uma página informativa após o cadastro:

```jsx
function EmailEnviado() {
  return (
    <div className="confirmacao-email">
      <h1>📧 Email enviado!</h1>
      <p>
        Enviamos um link de ativação para seu email.
      </p>
      <p>
        <strong>Próximos passos:</strong>
      </p>
      <ol>
        <li>Abra sua caixa de entrada</li>
        <li>Procure por um email de "Conectades"</li>
        <li>Clique no link de ativação</li>
        <li>Sua conta será ativada automaticamente!</li>
      </ol>
      
      <div className="aviso">
        ⚠️ O link expira em 24 horas
      </div>
      
      <div className="spam-warning">
        💡 Não encontrou o email? Verifique sua pasta de spam
      </div>
    </div>
  );
}
```

---

### **3. Página de Ativação Bem-Sucedida**

O backend redireciona para: `/auth/ativacao-sucesso?access=...&refresh=...`

```javascript
function AtivacaoSucesso() {
  const [status, setStatus] = useState('processando');
  
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access');
    const refreshToken = params.get('refresh');
    
    if (accessToken && refreshToken) {
      // Salvar tokens no localStorage/cookies
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      
      setStatus('sucesso');
      
      // Buscar dados do usuário
      buscarPerfilUsuario(accessToken);
      
      // Redirecionar para home em 3 segundos
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      setStatus('erro');
    }
  }, []);
  
  if (status === 'processando') {
    return <div>Ativando sua conta...</div>;
  }
  
  if (status === 'erro') {
    return (
      <div>
        <h1>❌ Erro na ativação</h1>
        <p>Não foi possível ativar sua conta.</p>
        <button onClick={() => router.push('/cadastro')}>
          Tentar novamente
        </button>
      </div>
    );
  }
  
  return (
    <div className="ativacao-sucesso">
      <h1>✅ Conta ativada com sucesso!</h1>
      <p>Bem-vinda à Conectades!</p>
      <p>Redirecionando para o início...</p>
      <div className="spinner"></div>
    </div>
  );
}
```

---

### **4. Buscar Perfil do Usuário**

Após ativar, busque os dados do usuário:

```javascript
const buscarPerfilUsuario = async (accessToken) => {
  try {
    const response = await fetch('/api/auth/perfil/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    const userData = await response.json();
    
    // Salvar dados do usuário no estado global
    setUser(userData);
    
  } catch (error) {
    console.error('Erro ao buscar perfil:', error);
  }
};
```

---

## 📧 Conteúdo do Email

O usuário receberá um email assim:

```
Assunto: 🌟 Conectades - Ative sua conta

Olá! 👋

Bem-vinda à plataforma Conectades!

Para ativar sua conta, clique no link abaixo:

https://api.conectades.com/api/auth/registro/ativar/a1b2c3d4-e5f6-7890/

Ou copie e cole este link no seu navegador.

⏰ Este link é válido por 24 horas.

Se você não solicitou este cadastro, ignore este email.

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
```

---

## 🔄 Fluxo Visual

```
[Formulário de Cadastro]
         ↓
    Preencher dados
         ↓
  POST /api/auth/registro/iniciar/
         ↓
[Página: Email Enviado]
         ↓
    Usuário abre email
         ↓
    Clica no link
         ↓
  GET /api/auth/registro/ativar/<token>/
         ↓
[Página HTML de Confirmação] (backend)
         ↓
    Redirecionamento automático (2s)
         ↓
  /auth/ativacao-sucesso?access=...&refresh=...
         ↓
    Frontend salva tokens
         ↓
    Busca dados do usuário
         ↓
[Redireciona para Home]
         ↓
    Usuário logado!
```

---

## ⏱️ Timeouts e Validades

| Item | Validade | Observação |
|------|----------|------------|
| **Link de ativação** | 24 horas | Após expirar, precisa se cadastrar novamente |
| **Dados no cache** | 24 horas | Sincronizado com o link |
| **Access Token JWT** | 5 minutos | Use refresh token para renovar |
| **Refresh Token JWT** | 7 dias | Após expirar, precisa fazer login novamente |

---

## 🚨 Tratamento de Erros

### **Erro: Email já cadastrado**
```javascript
if (data.email?.includes('já está cadastrado')) {
  mostrarErro('Este email já possui uma conta. Faça login ou recupere sua senha.');
  redirecionarParaLogin();
}
```

### **Erro: CPF já cadastrado**
```javascript
if (data.cpf?.includes('já está cadastrado')) {
  mostrarErro('Este CPF já está cadastrado. Entre em contato com o suporte.');
}
```

### **Erro: Token expirado**
```javascript
if (data.error?.includes('expirado')) {
  mostrarErro('O link de ativação expirou. Por favor, cadastre-se novamente.');
  redirecionarParaCadastro();
}
```

---

## ✅ Validações no Frontend

Valide antes de enviar para economizar requisições:

```javascript
const validarCadastro = (dados) => {
  const erros = {};
  
  // Nome completo
  if (!dados.nome_completo || dados.nome_completo.length < 3) {
    erros.nome_completo = 'Nome completo deve ter no mínimo 3 caracteres';
  }
  
  // Email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(dados.email)) {
    erros.email = 'Email inválido';
  }
  
  // Senha
  if (!dados.password || dados.password.length < 8) {
    erros.password = 'Senha deve ter no mínimo 8 caracteres';
  }
  
  // CPF (básico)
  const cpfLimpo = dados.cpf.replace(/\D/g, '');
  if (cpfLimpo.length !== 11) {
    erros.cpf = 'CPF inválido';
  }
  
  // Telefone
  const telLimpo = dados.telefone.replace(/\D/g, '');
  if (telLimpo.length < 10) {
    erros.telefone = 'Telefone inválido';
  }
  
  // Cidade e bairro
  if (!dados.cidade) {
    erros.cidade = 'Selecione uma cidade';
  }
  if (!dados.bairro) {
    erros.bairro = 'Selecione um bairro';
  }
  
  return {
    valido: Object.keys(erros).length === 0,
    erros
  };
};
```

---

## 🎨 Sugestões de UX

### **1. Loading durante cadastro**
```jsx
<button disabled={isLoading}>
  {isLoading ? 'Criando conta...' : 'Cadastrar'}
</button>
```

### **2. Feedback visual de sucesso**
Use animações (confetti, checkmark animado) ao mostrar "Email enviado!"

### **3. Opção de reenviar email**
Se o usuário não recebeu:
```jsx
<button onClick={() => reenviarEmail(email)}>
  📧 Reenviar email de ativação
</button>
```

### **4. Timer visual**
Mostrar countdown de 24h na página "Email Enviado"

---

## 🔐 Segurança

- ✅ Tokens são UUID únicos e imprevisíveis
- ✅ Tokens expiram em 24 horas
- ✅ Tokens são marcados como usados após ativação
- ✅ Um token só pode ser usado uma vez
- ✅ Dados sensíveis não são expostos no email

---

## 📱 Mobile

O link de ativação funciona perfeitamente em dispositivos móveis:
1. Usuário abre email no celular
2. Clica no link
3. Abre no navegador
4. Redireciona para o app (se usar deep linking)

**Deep Linking (opcional):**
Configure para abrir o app ao invés do navegador:
```
conectades://auth/ativacao-sucesso?access=...&refresh=...
```

---

## ❓ FAQ

### **P: O que acontece se o usuário não clicar no link?**
R: A conta não é criada. Ele precisa se cadastrar novamente.

### **P: Posso reenviar o link de ativação?**
R: Não há endpoint específico ainda. Usuário deve se cadastrar novamente (os dados antigos são sobrescritos).

### **P: O link funciona múltiplas vezes?**
R: Não. Após a primeira ativação, o token é marcado como usado.

### **P: E se o usuário tentar se cadastrar com um email já ativo?**
R: Backend retorna erro: "Este email já está cadastrado."

---

## 📞 Próximos Passos

Após implementar o cadastro, implemente também:
- **Login**: `/api/auth/login/` (POST)
- **Recuperação de senha**: `/api/auth/senha/recuperar/` (POST)
- **Atualizar perfil**: `/api/auth/perfil/atualizar/` (PUT/PATCH)

Veja documentação completa em: `/api/docs/`

---

**Última atualização:** 30/10/2025  
**Versão da API:** 1.0.0

