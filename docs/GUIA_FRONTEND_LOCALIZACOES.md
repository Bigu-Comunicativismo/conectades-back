# 📍 Guia de Localizações para o Frontend

## 🎯 Visão Geral

O sistema agora possui uma estrutura **hierárquica** de localizações:
- **Cidades**: Recife, Olinda, Jaboatão dos Guararapes
- **Bairros**: 139 bairros distribuídos pelas 3 cidades
- Estrutura otimizada para **dropdowns dependentes** (seleciona cidade → mostra bairros)

---

## 📡 Endpoints Disponíveis

### **1️⃣ GET `/api/auth/opcoes/`** - Buscar todas as opções de cadastro

**Uso:** Carregar opções ao iniciar o formulário de cadastro

**Resposta:**
```json
{
  "tipos_usuario": [
    {"id": 1, "nome": "Beneficiária", "codigo": "beneficiaria", "ativo": true, "ordem": 1},
    {"id": 2, "nome": "Doadora", "codigo": "doadora", "ativo": true, "ordem": 2}
  ],
  "generos": [
    {"id": 1, "nome": "Mulher Cis", "codigo": "mulher-cis", "ativo": true, "ordem": 1},
    {"id": 2, "nome": "Mulher Trans", "codigo": "mulher-trans", "ativo": true, "ordem": 2},
    ...
  ],
  "categorias_interesse": [
    {"id": 1, "nome": "Alimentação", "codigo": "alimentacao", "ativo": true, "ordem": 1},
    {"id": 2, "nome": "Vestuário", "codigo": "vestuario", "ativo": true, "ordem": 2},
    ...
  ],
  "cidades": [
    {"id": 1, "nome": "Recife", "codigo": "recife-cidade", "estado": "PE"},
    {"id": 2, "nome": "Olinda", "codigo": "olinda-cidade", "estado": "PE"},
    {"id": 3, "nome": "Jaboatão dos Guararapes", "codigo": "jaboatao-dos-guararapes-cidade", "estado": "PE"}
  ],
  "bairros_por_cidade": {
    "Recife": [
      {"id": 100, "nome": "Afogados", "codigo": "afogados-bairro"},
      {"id": 101, "nome": "Água Fria", "codigo": "agua-fria-bairro"},
      {"id": 102, "nome": "Boa Viagem", "codigo": "boa-viagem-bairro"},
      {"id": 103, "nome": "Coque", "codigo": "coque-bairro"},
      ... // 94 bairros de Recife
    ],
    "Olinda": [
      {"id": 200, "nome": "Bairro Novo", "codigo": "bairro-novo-bairro"},
      {"id": 201, "nome": "Casa Caiada", "codigo": "casa-caiada-bairro"},
      ... // 33 bairros de Olinda
    ],
    "Jaboatão dos Guararapes": [
      {"id": 300, "nome": "Candeias", "codigo": "candeias-bairro"},
      {"id": 301, "nome": "Piedade", "codigo": "piedade-bairro"},
      ... // 12 bairros de Jaboatão
    ]
  },
  "localizacoes_interesse": [...] // ⚠️ DEPRECATED - mantido para compatibilidade
}
```

---

### **2️⃣ GET `/api/auth/bairros/<cidade>/`** - Buscar bairros de uma cidade específica

**Uso:** Alternativa para buscar bairros sob demanda (mais leve)

**Exemplos:**
```http
GET /api/auth/bairros/Recife/
GET /api/auth/bairros/Olinda/
GET /api/auth/bairros/Jaboatão dos Guararapes/
```

**Resposta:**
```json
{
  "cidade": "Recife",
  "total": 94,
  "bairros": [
    {"id": 100, "nome": "Afogados", "codigo": "afogados-bairro"},
    {"id": 101, "nome": "Água Fria", "codigo": "agua-fria-bairro"},
    {"id": 102, "nome": "Boa Viagem", "codigo": "boa-viagem-bairro"},
    ...
  ]
}
```

**Erro (cidade não encontrada):**
```json
{
  "error": "Cidade \"NomeCidade\" não encontrada"
}
```

---

## 💻 Implementação no Frontend

### **Opção 1: Carregar tudo de uma vez (RECOMENDADO)**

Melhor para UX - usuário não precisa esperar ao trocar de cidade.

```javascript
// 1. Buscar opções ao carregar o formulário
const carregarOpcoes = async () => {
  const response = await fetch('/api/auth/opcoes/');
  const data = await response.json();
  
  return data;
};

// 2. Popular dropdown de cidades
const popularCidades = (cidades) => {
  const cidadeSelect = document.getElementById('cidade');
  
  cidades.forEach(cidade => {
    const option = document.createElement('option');
    option.value = cidade.nome;
    option.text = cidade.nome;
    cidadeSelect.appendChild(option);
  });
};

// 3. Popular dropdown de bairros baseado na cidade selecionada
const popularBairros = (cidadeSelecionada, bairrosPorCidade) => {
  const bairroSelect = document.getElementById('bairro');
  bairroSelect.innerHTML = '<option value="">Selecione seu bairro</option>';
  
  const bairros = bairrosPorCidade[cidadeSelecionada] || [];
  
  bairros.forEach(bairro => {
    const option = document.createElement('option');
    option.value = bairro.id; // Ou bairro.nome, dependendo da necessidade
    option.text = bairro.nome;
    bairroSelect.appendChild(option);
  });
  
  // Habilitar select de bairros
  bairroSelect.disabled = false;
};

// 4. Uso completo
const inicializarFormulario = async () => {
  const opcoes = await carregarOpcoes();
  
  // Popular cidades
  popularCidades(opcoes.cidades);
  
  // Listener para quando selecionar cidade
  const cidadeSelect = document.getElementById('cidade');
  cidadeSelect.addEventListener('change', (e) => {
    const cidadeSelecionada = e.target.value;
    popularBairros(cidadeSelecionada, opcoes.bairros_por_cidade);
  });
};

// Inicializar ao carregar a página
inicializarFormulario();
```

---

### **Opção 2: Buscar bairros sob demanda**

Melhor se houver muitas cidades (economiza banda inicial).

```javascript
// 1. Popular cidades
const carregarCidades = async () => {
  const response = await fetch('/api/auth/opcoes/');
  const data = await response.json();
  
  const cidadeSelect = document.getElementById('cidade');
  data.cidades.forEach(cidade => {
    const option = document.createElement('option');
    option.value = cidade.nome;
    option.text = cidade.nome;
    cidadeSelect.appendChild(option);
  });
};

// 2. Buscar bairros quando selecionar cidade
const buscarBairros = async (cidade) => {
  const response = await fetch(`/api/auth/bairros/${encodeURIComponent(cidade)}/`);
  const data = await response.json();
  
  const bairroSelect = document.getElementById('bairro');
  bairroSelect.innerHTML = '<option value="">Selecione seu bairro</option>';
  
  data.bairros.forEach(bairro => {
    const option = document.createElement('option');
    option.value = bairro.id;
    option.text = bairro.nome;
    bairroSelect.appendChild(option);
  });
  
  bairroSelect.disabled = false;
};

// 3. Listener
document.getElementById('cidade').addEventListener('change', async (e) => {
  const cidade = e.target.value;
  if (cidade) {
    await buscarBairros(cidade);
  }
});
```

---

## 📋 Exemplo com React/Vue/Angular

### **React (Hooks)**

```jsx
import { useState, useEffect } from 'react';

function FormularioCadastro() {
  const [opcoes, setOpcoes] = useState(null);
  const [cidadeSelecionada, setCidadeSelecionada] = useState('');
  const [bairros, setBairros] = useState([]);

  // Carregar opções ao montar
  useEffect(() => {
    fetch('/api/auth/opcoes/')
      .then(res => res.json())
      .then(data => setOpcoes(data));
  }, []);

  // Atualizar bairros quando cidade mudar
  useEffect(() => {
    if (cidadeSelecionada && opcoes) {
      const bairrosDaCidade = opcoes.bairros_por_cidade[cidadeSelecionada] || [];
      setBairros(bairrosDaCidade);
    } else {
      setBairros([]);
    }
  }, [cidadeSelecionada, opcoes]);

  if (!opcoes) return <div>Carregando...</div>;

  return (
    <form>
      {/* Cidade */}
      <select 
        value={cidadeSelecionada} 
        onChange={(e) => setCidadeSelecionada(e.target.value)}
      >
        <option value="">Selecione sua cidade</option>
        {opcoes.cidades.map(cidade => (
          <option key={cidade.id} value={cidade.nome}>
            {cidade.nome}
          </option>
        ))}
      </select>

      {/* Bairro */}
      <select disabled={!cidadeSelecionada}>
        <option value="">Selecione seu bairro</option>
        {bairros.map(bairro => (
          <option key={bairro.id} value={bairro.id}>
            {bairro.nome}
          </option>
        ))}
      </select>
    </form>
  );
}
```

---

### **Vue 3 (Composition API)**

```vue
<template>
  <form>
    <select v-model="cidadeSelecionada">
      <option value="">Selecione sua cidade</option>
      <option v-for="cidade in cidades" :key="cidade.id" :value="cidade.nome">
        {{ cidade.nome }}
      </option>
    </select>

    <select :disabled="!cidadeSelecionada">
      <option value="">Selecione seu bairro</option>
      <option v-for="bairro in bairros" :key="bairro.id" :value="bairro.id">
        {{ bairro.nome }}
      </option>
    </select>
  </form>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const opcoes = ref(null);
const cidadeSelecionada = ref('');

const cidades = computed(() => opcoes.value?.cidades || []);
const bairros = computed(() => {
  if (!cidadeSelecionada.value || !opcoes.value) return [];
  return opcoes.value.bairros_por_cidade[cidadeSelecionada.value] || [];
});

onMounted(async () => {
  const response = await fetch('/api/auth/opcoes/');
  opcoes.value = await response.json();
});
</script>
```

---

## 📊 Dados Disponíveis

### **Cidades (3)**
- Recife
- Olinda
- Jaboatão dos Guararapes

### **Bairros (139 total)**
- **Recife**: 94 bairros (Afogados, Água Fria, Boa Viagem, Coque, Casa Forte, etc.)
- **Olinda**: 33 bairros (Bairro Novo, Casa Caiada, Cidade Tabajara, etc.)
- **Jaboatão**: 12 bairros (Candeias, Piedade, Prazeres, etc.)

---

## ✅ Validação no Frontend

```javascript
const validarLocalizacao = (cidade, bairro) => {
  if (!cidade) {
    return { valido: false, mensagem: 'Selecione uma cidade' };
  }
  
  if (!bairro) {
    return { valido: false, mensagem: 'Selecione um bairro' };
  }
  
  return { valido: true };
};
```

---

## 🚀 Envio para o Backend

Ao enviar o formulário de cadastro, inclua:

```json
{
  "nome_completo": "Maria Silva",
  "email": "maria@example.com",
  "cidade": "Recife",
  "bairro": "Coque",
  "localizacoes_interesse": [100, 101, 102], // IDs dos bairros de interesse
  ...
}
```

**⚠️ IMPORTANTE:**
- `cidade`: String com o nome da cidade
- `bairro`: String com o nome do bairro
- `localizacoes_interesse`: Array de IDs (opcional) para interesses de múltiplos bairros

---

## 🎨 Sugestões de UX

### **1. Estado Inicial**
```
Cidade:  [Selecione sua cidade ▼]
Bairro:  [Primeiro selecione uma cidade] (desabilitado)
```

### **2. Após selecionar cidade**
```
Cidade:  [Recife ▼]
Bairro:  [Selecione seu bairro ▼] (habilitado)
         ├─ Afogados
         ├─ Água Fria
         ├─ Boa Viagem
         ├─ Coque
         └─ ... (94 bairros)
```

### **3. Loading ao buscar bairros (Opção 2)**
```
Cidade:  [Recife ▼]
Bairro:  [⏳ Carregando bairros...]
```

### **4. Busca dentro do select**
Considere usar bibliotecas como:
- **Select2** (jQuery)
- **React Select** (React)
- **Vue Select** (Vue)
- **ng-select** (Angular)

Isso permite buscar bairros por nome (útil pois Recife tem 94 bairros!).

---

## 🔄 Cache e Performance

- ✅ API já implementa cache de 1 hora
- ✅ Bairros são pré-agrupados por cidade
- ✅ Carregamento único de opções é suficiente

**Recomendação:** Cache no frontend também:
```javascript
// LocalStorage para cache
const CACHE_KEY = 'conectades_opcoes_cadastro';
const CACHE_TTL = 60 * 60 * 1000; // 1 hora

const carregarOpcoesComCache = async () => {
  const cached = localStorage.getItem(CACHE_KEY);
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < CACHE_TTL) {
      return data;
    }
  }
  
  const response = await fetch('/api/auth/opcoes/');
  const data = await response.json();
  
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    data,
    timestamp: Date.now()
  }));
  
  return data;
};
```

---

## ❓ FAQ

### **P: Posso enviar o ID do bairro ao invés do nome?**
R: Não recomendado. O modelo `Pessoa` espera `cidade` e `bairro` como strings. Use os nomes.

### **P: E se o usuário não encontrar seu bairro?**
R: Atualmente temos 139 bairros principais. Se necessário, adicione uma opção "Outro" e um campo de texto livre.

### **P: Posso buscar bairros por termo de busca?**
R: Não há endpoint específico, mas você pode implementar busca client-side no array de bairros.

### **P: Os dados mudam frequentemente?**
R: Não. Cidades e bairros são relativamente estáticos. Cache de 1 hora é seguro.

### **P: Preciso validar se o bairro pertence à cidade selecionada?**
R: Sim, no frontend. No backend já há validação.

---

## 📞 Suporte

Dúvidas ou problemas? Entre em contato com o time de backend.

**Documentação da API completa:** `/api/docs/` (Swagger)

---

**Última atualização:** 30/10/2025  
**Versão da API:** 1.0.0

