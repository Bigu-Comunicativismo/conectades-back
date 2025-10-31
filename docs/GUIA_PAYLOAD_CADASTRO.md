# 📝 Guia de Payload para Cadastro de Usuário

## ⚠️ IMPORTANTE: IDs Numéricos, NÃO Strings!

O endpoint `/api/auth/registro/iniciar/` espera **IDs numéricos** para campos relacionais, não strings.

## ❌ Errado vs ✅ Correto

### ❌ ERRADO - Usando strings:
```json
{
  "tipo_usuario": "beneficiaria",  // ❌ String
  "genero": "feminino",            // ❌ String
  "categorias_interesse": ["saude", "educacao"]  // ❌ Strings
}
```

### ✅ CORRETO - Usando IDs numéricos:
```json
{
  "tipo_usuario": 1,               // ✅ ID (number)
  "genero": 2,                     // ✅ ID (number)
  "categorias_interesse": [1, 3]   // ✅ Array de IDs
}
```

## 📋 Payload Completo Correto

```json
{
  "email": "usuario@example.com",
  "username": "usuario123",
  "password": "senhaSegura123",
  "nome_completo": "Maria Silva Santos",
  "cpf": "123.456.789-00",
  "telefone": "(81)9 9999-0000",
  "tipo_usuario": 1,
  "genero": 2,
  "cidade": "Recife",
  "bairro": "Boa Viagem",
  "nome_social": "Maria",
  "mini_bio": "Sou uma profissional dedicada e apaixonada por ajudar a comunidade.",
  "categorias_interesse": [1, 3, 5]
}
```

## 🔍 Como Descobrir os IDs Disponíveis?

### Endpoint: `GET /api/auth/opcoes/`

Este endpoint retorna TODAS as opções disponíveis com seus respectivos IDs:

```bash
curl http://seu-servidor/api/auth/opcoes/
```

### Resposta Exemplo:

```json
{
  "tipos_usuario": [
    {
      "id": 1,
      "nome": "Beneficiária",
      "codigo": "beneficiaria",
      "descricao": "Pessoa que busca auxílio",
      "ativo": true
    },
    {
      "id": 2,
      "nome": "Doadora",
      "codigo": "doadora",
      "descricao": "Pessoa que oferece auxílio",
      "ativo": true
    }
  ],
  "generos": [
    {
      "id": 1,
      "nome": "Cisgênero Feminino",
      "codigo": "cis_feminino",
      "ativo": true
    },
    {
      "id": 2,
      "nome": "Cisgênero Masculino",
      "codigo": "cis_masculino",
      "ativo": true
    },
    {
      "id": 3,
      "nome": "Transgênero Feminino",
      "codigo": "trans_feminino",
      "ativo": true
    }
  ],
  "categorias_interesse": [
    {
      "id": 1,
      "nome": "Saúde",
      "codigo": "saude",
      "ativo": true
    },
    {
      "id": 2,
      "nome": "Educação",
      "codigo": "educacao",
      "ativo": true
    }
  ],
  "cidades": [
    {
      "id": 1,
      "nome": "Recife",
      "codigo": "recife",
      "estado": "PE"
    }
  ],
  "bairros_por_cidade": {
    "Recife": [
      {
        "id": 101,
        "nome": "Boa Viagem",
        "codigo": "boa_viagem"
      },
      {
        "id": 102,
        "nome": "Coque",
        "codigo": "coque"
      }
    ]
  }
}
```

## 🎯 Estratégia de Implementação no Frontend

### 1. Buscar Opções na Montagem do Componente

```typescript
// React/Next.js exemplo
import { useEffect, useState } from 'react';

interface OpcoesRegistro {
  tipos_usuario: Array<{id: number, nome: string, codigo: string}>;
  generos: Array<{id: number, nome: string, codigo: string}>;
  categorias_interesse: Array<{id: number, nome: string, codigo: string}>;
  cidades: Array<{id: number, nome: string, codigo: string}>;
  bairros_por_cidade: Record<string, Array<{id: number, nome: string}>>;
}

function RegistroForm() {
  const [opcoes, setOpcoes] = useState<OpcoesRegistro | null>(null);
  
  useEffect(() => {
    fetch('http://seu-servidor/api/auth/opcoes/')
      .then(res => res.json())
      .then(data => setOpcoes(data));
  }, []);
  
  // Renderizar formulário com opcoes.tipos_usuario, opcoes.generos, etc.
}
```

### 2. Criar Dropdowns/Selects com IDs

```tsx
// Select de Tipo de Usuário
<select name="tipo_usuario" onChange={handleChange}>
  {opcoes?.tipos_usuario.map(tipo => (
    <option key={tipo.id} value={tipo.id}>
      {tipo.nome}
    </option>
  ))}
</select>

// Select de Gênero
<select name="genero" onChange={handleChange}>
  {opcoes?.generos.map(genero => (
    <option key={genero.id} value={genero.id}>
      {genero.nome}
    </option>
  ))}
</select>

// Multi-select de Categorias
<Select
  multiple
  name="categorias_interesse"
  options={opcoes?.categorias_interesse || []}
  getOptionLabel={(option) => option.nome}
  getOptionValue={(option) => option.id}
/>
```

### 3. Enviar Payload com IDs Numéricos

```typescript
async function handleSubmit(formData: FormData) {
  const payload = {
    email: formData.get('email'),
    username: formData.get('username'),
    password: formData.get('password'),
    nome_completo: formData.get('nome_completo'),
    cpf: formData.get('cpf'),
    telefone: formData.get('telefone'),
    tipo_usuario: Number(formData.get('tipo_usuario')),  // ✅ Converter para number!
    genero: Number(formData.get('genero')),              // ✅ Converter para number!
    cidade: formData.get('cidade'),
    bairro: formData.get('bairro'),
    nome_social: formData.get('nome_social'),
    mini_bio: formData.get('mini_bio'),
    categorias_interesse: formData.getAll('categorias_interesse').map(Number)  // ✅ Array de numbers
  };
  
  const response = await fetch('http://seu-servidor/api/auth/registro/iniciar/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload)
  });
  
  if (response.ok) {
    const data = await response.json();
    alert(data.message);  // "Link de ativação enviado para seu email"
  } else {
    const error = await response.json();
    console.error('Erro:', error);
  }
}
```

## 📊 Validação de Campos

### Campos Obrigatórios:
- ✅ `email` (string, formato email válido)
- ✅ `username` (string, mínimo 3 caracteres)
- ✅ `password` (string, mínimo 8 caracteres)
- ✅ `nome_completo` (string)
- ✅ `cpf` (string, formato XXX.XXX.XXX-XX)
- ✅ `telefone` (string, com DDD)
- ✅ `tipo_usuario` (number, ID válido)
- ✅ `genero` (number, ID válido)
- ✅ `cidade` (string)
- ✅ `bairro` (string)
- ✅ `nome_social` (string)
- ✅ `mini_bio` (string)

### Campos Opcionais:
- `avatar` (file, imagem)
- `categorias_interesse` (array of numbers)
- `localizacoes_interesse` (array of numbers)

## 🚨 Erros Comuns

### Erro 400: "tipo_usuario: Expected a number"
```json
// ❌ Enviado:
{"tipo_usuario": "beneficiaria"}

// ✅ Correto:
{"tipo_usuario": 1}
```

### Erro 500: "TypeError: Object of type TipoUsuario is not JSON serializable"
- **Causa:** Backend com cache corrompido
- **Solução Automática:** Middleware detecta e limpa automaticamente
- **Você receberá:** HTTP 503 com `retry_after: 2`
- **Ação:** Aguardar 2 segundos e tentar novamente

### Erro 400: "Invalid pk '999'"
```json
// ❌ ID inexistente:
{"tipo_usuario": 999}

// ✅ Use IDs retornados por /api/auth/opcoes/
{"tipo_usuario": 1}
```

## 📞 Suporte

Se tiver dúvidas sobre:
- Estrutura de dados: Consulte `GET /api/auth/opcoes/`
- Documentação interativa: `http://seu-servidor/api/docs/`
- Swagger/OpenAPI: `http://seu-servidor/api/schema/swagger-ui/`

