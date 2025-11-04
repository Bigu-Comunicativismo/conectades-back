# 🔍 Filtros e Query Params nas Campanhas

## 🎯 Objetivo

Permitir filtrar, buscar e ordenar campanhas usando **query parameters** na URL.

---

## ✅ Query Parameters Disponíveis

### **Endpoint:** `GET /api/campanhas/listar/`

| Parâmetro | Tipo | Descrição | Valores Possíveis | Padrão |
|-----------|------|-----------|-------------------|---------|
| `busca` | string | Busca por título ou descrição | Qualquer texto | - |
| `categoria` | integer | Filtrar por ID da categoria | ID válido | - |
| `localizacao` | integer | Filtrar por ID da localização | ID válido | - |
| `status` | string | Filtrar por status da campanha | `ativa`, `encerrada`, `todas` | `ativa` |
| `ordenar` | string | Ordenar resultados | `recente`, `antiga`, `prazo`, `progresso` | `recente` |

---

## 📋 Exemplos de Uso

### **1. Buscar campanhas por palavra-chave**

Busca "educação" no título ou descrição:

```bash
GET /api/campanhas/listar/?busca=educação
```

```bash
curl "http://srv1037558.hstgr.cloud:8001/api/campanhas/listar/?busca=educação"
```

---

### **2. Filtrar por categoria**

Mostrar apenas campanhas da categoria ID 2:

```bash
GET /api/campanhas/listar/?categoria=2
```

```bash
curl "http://srv1037558.hstgr.cloud:8001/api/campanhas/listar/?categoria=2"
```

---

### **3. Filtrar por localização**

Mostrar campanhas da localização ID 5:

```bash
GET /api/campanhas/listar/?localizacao=5
```

```bash
curl "http://srv1037558.hstgr.cloud:8001/api/campanhas/listar/?localizacao=5"
```

---

### **4. Filtrar por status**

**Apenas campanhas ativas** (padrão):
```bash
GET /api/campanhas/listar/?status=ativa
```

**Apenas campanhas encerradas**:
```bash
GET /api/campanhas/listar/?status=encerrada
```

**Todas as campanhas** (ativas + encerradas):
```bash
GET /api/campanhas/listar/?status=todas
```

---

### **5. Ordenar resultados**

**Mais recentes primeiro** (padrão):
```bash
GET /api/campanhas/listar/?ordenar=recente
```

**Mais antigas primeiro**:
```bash
GET /api/campanhas/listar/?ordenar=antiga
```

**Por prazo de encerramento** (mais próximo ao prazo):
```bash
GET /api/campanhas/listar/?ordenar=prazo
```

**Por progresso** (experimental):
```bash
GET /api/campanhas/listar/?ordenar=progresso
```

---

### **6. Combinar múltiplos filtros**

Buscar "saúde" em campanhas ativas da categoria 3, ordenadas por prazo:

```bash
GET /api/campanhas/listar/?busca=saúde&categoria=3&status=ativa&ordenar=prazo
```

```bash
curl "http://srv1037558.hstgr.cloud:8001/api/campanhas/listar/?busca=sa%C3%BAde&categoria=3&status=ativa&ordenar=prazo"
```

---

## 🧪 Testando no Swagger UI

1. Acesse: `http://srv1037558.hstgr.cloud:8001/api/docs/`
2. Vá para: **`GET /api/campanhas/listar/`**
3. Clique em **"Try it out"**
4. Preencha os parâmetros desejados:
   - `busca`: Digite uma palavra-chave
   - `categoria`: Digite um ID de categoria
   - `localizacao`: Digite um ID de localização
   - `status`: Escolha entre `ativa`, `encerrada` ou `todas`
   - `ordenar`: Escolha entre `recente`, `antiga`, `prazo` ou `progresso`
5. Clique em **"Execute"**

---

## 🧠 Como funciona internamente

### **1. Busca (busca)**
```python
# Busca case-insensitive no título OU descrição
campanhas.filter(
    Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
)
```

### **2. Filtro por Categoria (categoria)**
```python
# Filtra campanhas que possuem a categoria especificada
campanhas.filter(categorias__id=categoria_id)
```

### **3. Filtro por Localização (localizacao)**
```python
# Filtra campanhas da localização especificada
campanhas.filter(localizacao_id=localizacao_id)
```

### **4. Filtro por Status (status)**
```python
if status_filtro == 'ativa':
    campanhas.filter(ativa=True)
elif status_filtro == 'encerrada':
    campanhas.filter(ativa=False)
# 'todas' não aplica filtro
```

### **5. Ordenação (ordenar)**
```python
if ordenar == 'recente':
    campanhas.order_by('-data_inicio')  # Mais recente
elif ordenar == 'antiga':
    campanhas.order_by('data_inicio')   # Mais antiga
elif ordenar == 'prazo':
    campanhas.order_by('prazo')         # Prazo mais próximo
```

---

## 🚀 Cache Inteligente

O sistema usa **cache baseado nos filtros**:

```python
cache_key = f'campanhas_{busca}_{categoria_id}_{localizacao_id}_{status_filtro}_{ordenar}'
```

Isso significa que:
- ✅ Cada combinação de filtros tem seu próprio cache
- ✅ Cache dura 1 hora (`CACHE_TTL`)
- ✅ Reduz carga no banco de dados
- ✅ Respostas mais rápidas

---

## 📊 Exemplos de Resposta

### **Sem filtros (padrão)**

```json
[
  {
    "id": 1,
    "titulo": "Campanha de Educação",
    "descricao": "Doações para material escolar",
    "ativa": true,
    "status_campanha": "Em andamento",
    "percentual_atingido": 45.5,
    "categorias": [1, 3],
    "localizacao": 5,
    ...
  },
  ...
]
```

### **Com busca: `?busca=educação`**

Retorna apenas campanhas com "educação" no título ou descrição.

### **Com categoria: `?categoria=2`**

Retorna apenas campanhas da categoria ID 2.

### **Combinado: `?busca=saúde&status=encerrada&ordenar=prazo`**

Retorna campanhas encerradas sobre "saúde", ordenadas por prazo.

---

## 🎨 Frontend - Exemplos de UI

### **Barra de Busca**
```html
<input type="text" placeholder="Buscar campanhas..." />
```
```javascript
fetch(`/api/campanhas/listar/?busca=${termoDeBusca}`)
```

### **Filtro de Categoria (Dropdown)**
```html
<select>
  <option value="">Todas as categorias</option>
  <option value="1">Educação</option>
  <option value="2">Saúde</option>
  <option value="3">Alimentação</option>
</select>
```
```javascript
fetch(`/api/campanhas/listar/?categoria=${categoriaId}`)
```

### **Filtro de Status (Tabs)**
```html
<div class="tabs">
  <button onclick="filtrarPorStatus('ativa')">Ativas</button>
  <button onclick="filtrarPorStatus('encerrada')">Encerradas</button>
  <button onclick="filtrarPorStatus('todas')">Todas</button>
</div>
```
```javascript
function filtrarPorStatus(status) {
  fetch(`/api/campanhas/listar/?status=${status}`)
}
```

### **Ordenação (Dropdown)**
```html
<select onchange="ordenar(this.value)">
  <option value="recente">Mais recentes</option>
  <option value="antiga">Mais antigas</option>
  <option value="prazo">Prazo mais próximo</option>
  <option value="progresso">Por progresso</option>
</select>
```
```javascript
function ordenar(ordem) {
  fetch(`/api/campanhas/listar/?ordenar=${ordem}`)
}
```

---

## 🔧 Dicas de Performance

1. **Combine filtros quando possível**
   - ✅ `?busca=saude&categoria=2&status=ativa`
   - ❌ Múltiplas requisições separadas

2. **Use cache efetivamente**
   - Consultas idênticas são servidas do cache
   - Cache válido por 1 hora

3. **Evite buscas muito genéricas**
   - ✅ `?busca=educacao infantil`
   - ❌ `?busca=a` (retorna muitas campanhas)

---

## 🎯 Casos de Uso Reais

### **📱 App Mobile - Tela Inicial**
```
Mostra: Campanhas ativas, ordenadas por mais recentes
URL: /api/campanhas/listar/?status=ativa&ordenar=recente
```

### **🔍 Página de Busca**
```
Usuário digita: "alimentação"
URL: /api/campanhas/listar/?busca=alimentação
```

### **🏷️ Página de Categoria**
```
Usuário clica em "Saúde" (ID 2)
URL: /api/campanhas/listar/?categoria=2
```

### **📍 Filtro por Localização**
```
Mostrar campanhas de "Recife" (ID 5)
URL: /api/campanhas/listar/?localizacao=5
```

### **🏁 Campanhas Próximas do Prazo**
```
Mostrar campanhas ativas, ordenadas por prazo
URL: /api/campanhas/listar/?status=ativa&ordenar=prazo
```

---

## ✅ Checklist de Testes

- [ ] Buscar por palavra-chave
- [ ] Filtrar por categoria válida
- [ ] Filtrar por localização válida
- [ ] Filtrar por status (ativa/encerrada/todas)
- [ ] Ordenar por recente
- [ ] Ordenar por antiga
- [ ] Ordenar por prazo
- [ ] Combinar busca + categoria + status
- [ ] Verificar cache (segunda requisição mais rápida)
- [ ] Testar com valores inválidos (deve ignorar)

---

## 🎉 Pronto!

Agora você pode **filtrar, buscar e ordenar** campanhas facilmente! 🔍✨

