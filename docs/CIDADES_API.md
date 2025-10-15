# 🌍 Integração com API do IBGE para Cidades e Bairros

Este documento explica como carregar cidades e bairros usando a API do IBGE e comandos Django personalizados.

---

## 📍 **Comandos Disponíveis**

### **1. Carregar Cidades da Região Metropolitana do Recife**

Carrega automaticamente as 14 cidades da RMR via **API do IBGE**:

```bash
# Carregar cidades da RMR
docker-compose exec web python backend/manage.py carregar_cidades_rmr

# Limpar cidades existentes e recarregar
docker-compose exec web python backend/manage.py carregar_cidades_rmr --limpar
```

**Cidades incluídas:**
- Abreu e Lima
- Araçoiaba
- Cabo de Santo Agostinho
- Camaragibe
- Goiana
- Igarassu
- Ipojuca
- Itamaracá
- Itapissuma
- Jaboatão dos Guararapes
- Moreno
- Olinda
- Paulista
- Recife
- São Lourenço da Mata

---

### **2. Carregar Bairros de Recife**

Carrega os 89 bairros oficiais de Recife:

```bash
# Carregar bairros de Recife
docker-compose exec web python backend/manage.py carregar_bairros_recife

# Limpar bairros existentes e recarregar
docker-compose exec web python backend/manage.py carregar_bairros_recife --limpar
```

**Exemplos de bairros:**
- Boa Viagem
- Casa Forte
- Graças
- Pina
- Santo Amaro
- (+ 84 outros bairros)

---

## 🔧 **Como Funciona**

### **API do IBGE (Cidades)**

A API do IBGE fornece dados oficiais e atualizados de todos os municípios brasileiros:

**Endpoint usado:**
```
https://servicodados.ibge.gov.br/api/v1/localidades/municipios
```

**Vantagens:**
- ✅ Dados oficiais do governo
- ✅ Sempre atualizados
- ✅ Gratuito e sem necessidade de API key
- ✅ Inclui código IBGE de cada município

**Funcionamento:**
1. Comando faz requisição para a API do IBGE
2. Filtra apenas municípios da RMR (por código IBGE)
3. Cria registros na tabela `LocalizacaoInteresse`
4. Gera código automático (slug) para cada cidade

---

### **Dados Estáticos (Bairros)**

Os bairros são carregados de uma lista estática baseada em dados oficiais:

**Fonte:** [Lista de bairros do Recife - Wikipedia](https://pt.wikipedia.org/wiki/Lista_de_bairros_do_Recife)

**Funcionamento:**
1. Lista de bairros está no código do comando
2. Cria registros na tabela `LocalizacaoInteresse`
3. Gera código automático (slug) para cada bairro

---

## 📊 **Estrutura dos Dados**

### **Exemplo de Cidade:**
```json
{
  "id": 15,
  "tipo": "cidade",
  "nome": "Recife",
  "codigo": "recife_cidade_recife",
  "cidade": "Recife",
  "estado": "PE",
  "ativo": true,
  "ordem": 0
}
```

### **Exemplo de Bairro:**
```json
{
  "id": 42,
  "tipo": "bairro",
  "nome": "Boa Viagem",
  "codigo": "boa-viagem_bairro_recife",
  "cidade": "Recife",
  "estado": "PE",
  "ativo": true,
  "ordem": 15
}
```

---

## 🚀 **Expandindo para Outras Regiões**

### **Adicionar Mais Cidades**

Para adicionar cidades de outra região, edite o arquivo:
`backend/pessoas/management/commands/carregar_cidades_rmr.py`

Modifique a lista `MUNICIPIOS_RMR` com os códigos IBGE desejados:

```python
MUNICIPIOS_RMR = [
    2600054,  # Abreu e Lima
    2604007,  # Araçoiaba
    # Adicione mais códigos aqui...
]
```

**Como encontrar códigos IBGE:**
1. Acesse: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
2. Busque pelo nome da cidade
3. Copie o `id` (código IBGE)

---

### **Adicionar Bairros de Outras Cidades**

Crie um novo comando baseado em `carregar_bairros_recife.py`:

```bash
cp backend/pessoas/management/commands/carregar_bairros_recife.py \
   backend/pessoas/management/commands/carregar_bairros_olinda.py
```

Edite o novo arquivo e modifique:
1. A lista `BAIRROS_RECIFE` para os bairros da nova cidade
2. O filtro `cidade='Recife'` para a nova cidade

---

## 🌐 **Usando API Externa para Bairros**

Atualmente não existe uma API oficial do IBGE para bairros, mas você pode usar:

### **Opção 1: ViaCEP (Gratuito)**
- API: https://viacep.com.br/
- Retorna endereço completo a partir de CEP (inclui bairro)
- Limitação: Precisa ter CEPs conhecidos

### **Opção 2: Google Places API**
- API: https://developers.google.com/maps/documentation/places/web-service
- Retorna bairros e localizações detalhadas
- Limitação: Requer API key e tem custos

### **Opção 3: OpenStreetMap (Nominatim)**
- API: https://nominatim.org/release-docs/develop/api/Search/
- Gratuito e open source
- Limitação: Rate limit de 1 requisição/segundo

---

## 📝 **Exemplos de Uso via API**

### **Listar Cidades Disponíveis:**
```bash
curl http://localhost/api/cadastro/localizacoes-interesse/?tipo=cidade
```

### **Listar Bairros de Recife:**
```bash
curl http://localhost/api/cadastro/localizacoes-interesse/?tipo=bairro&cidade=Recife
```

### **Buscar por Nome:**
```bash
curl http://localhost/api/cadastro/localizacoes-interesse/?search=Boa%20Viagem
```

---

## 🔄 **Atualização dos Dados**

### **Quando Atualizar:**
- **Cidades:** Raramente mudam (apenas em casos de emancipação de municípios)
- **Bairros:** Podem ser atualizados conforme legislação municipal

### **Como Atualizar:**

```bash
# Recarregar cidades (sobrescreve)
docker-compose exec web python backend/manage.py carregar_cidades_rmr --limpar

# Recarregar bairros (sobrescreve)
docker-compose exec web python backend/manage.py carregar_bairros_recife --limpar
```

---

## 🎯 **Resumo**

| Tipo | Fonte | Quantidade | Comando |
|------|-------|------------|---------|
| **Cidades RMR** | API IBGE | 14 | `carregar_cidades_rmr` |
| **Bairros Recife** | Lista estática | 89 | `carregar_bairros_recife` |

**Total de localizações:** 103+ (cidades + bairros)

---

## 🛠️ **Troubleshooting**

### **Erro: "Unable to connect to IBGE API"**
```bash
# Verifique a conexão com a internet
docker-compose exec web curl https://servicodados.ibge.gov.br/api/v1/localidades/municipios/2613701

# Se funcionar, tente o comando novamente
```

### **Erro: "LocalizacaoInteresse already exists"**
```bash
# Use a flag --limpar para sobrescrever
docker-compose exec web python backend/manage.py carregar_cidades_rmr --limpar
```

### **Erro: "Module 'requests' not found"**
```bash
# Instale a dependência
docker-compose exec web pip install requests

# Ou reconstrua o container
docker-compose build web
```

---

**Desenvolvido por Bigu Comunicativismo | Integração com dados oficiais do IBGE**

