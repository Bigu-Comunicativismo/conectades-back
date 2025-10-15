# 🌟 Conectades - Plataforma de Conexão Social

Plataforma para conectar pessoas e campanhas sociais, facilitando doações e voluntariado na Região Metropolitana do Recife.

---

## 🚀 Início Rápido

```bash
# Clonar repositório
git clone https://github.com/Bigu-Comunicativismo/conectades-back.git
cd conectades-back

# Iniciar aplicação (build + migração + população de dados)
chmod +x start.sh
./start.sh
```

**Pronto!** Acesse:
- 🌐 **Admin**: http://localhost/admin/ (admin/admin123)
- 📚 **API Docs**: http://localhost/api/docs/
- 🔗 **API**: http://localhost/api/

---

## ✨ Principais Funcionalidades

### **Sistema Dinâmico de Cadastro**
- ✅ **Tabelas configuráveis** (Tipos, Gêneros, Categorias)
- ✅ **Códigos auto-gerados** (sem necessidade de inserir manualmente)
- ✅ **106 localizações** da RMR pré-carregadas

### **Gestão de Campanhas**
- ✅ **Doadoras** podem criar campanhas
- ✅ **Organizadora** criada automaticamente
- ✅ **Beneficiárias** recebem ajuda

### **Alta Performance**
- ✅ **1000+ usuários simultâneos**
- ✅ **Redis** para cache
- ✅ **Nginx** como load balancer
- ✅ **Uvicorn** ASGI server

---

## 📊 Dados Pré-populados

| Tipo | Quantidade | Exemplos |
|------|-----------|----------|
| **Tipos de Usuário** | 2 | Beneficiária, Doadora |
| **Gêneros** | 10 | Mulher Cis, Não-binário, Travesti, ... |
| **Categorias** | 11 | Alimentação, Educação, Saúde, ... |
| **Cidades RMR** | 15 | Recife, Olinda, Jaboatão, ... |
| **Bairros** | 91 | Boa Viagem, Casa Forte, Graças, ... |

---

## 🛠️ Tecnologias

- **Backend**: Django 5.2 + Django REST Framework
- **Banco de Dados**: PostgreSQL 15
- **Cache**: Redis 7
- **Servidor**: Uvicorn (ASGI)
- **Proxy**: Nginx
- **Containerização**: Docker + Docker Compose

---

## 📖 Documentação Completa

- 📘 [Guia de Instalação Completo](docs/README.md)
- 🧪 [Testes com Insomnia/Postman](docs/TESTES_INSOMNIA_POSTMAN.md)
- 🏗️ [Arquitetura do Sistema](docs/arquitetura.md)
- 👩‍💼 [Lógica da Organizadora](docs/LOGICA_ORGANIZADORA.md)
- 🌍 [Integração com Localizações](docs/CIDADES_API.md)
- ⚡ [Performance e Otimizações](docs/README_PERFORMANCE.md)

---

## 🎯 Comandos Úteis

```bash
# Iniciar aplicação
./start.sh

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f web

# Carregar localizações da RMR
docker-compose exec web python backend/manage.py carregar_localizacoes_rmr

# Acessar shell Django
docker-compose exec web python backend/manage.py shell
```

---

## 👥 Tipos de Usuário

### **Beneficiária**
- Recebe doações e ajuda
- NÃO pode criar campanhas

### **Doadora**
- Faz doações
- PODE criar campanhas
- Vira Organizadora automaticamente ao criar primeira campanha

### **Organizadora**
- É uma Doadora que já criou campanhas
- Gerencia suas próprias campanhas
- Perfil criado automaticamente (não precisa cadastro)

---

## 🌐 URLs de Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Admin Django** | http://localhost/admin/ | admin/admin123 |
| **API Docs (Swagger)** | http://localhost/api/docs/ | - |
| **API** | http://localhost/api/ | Token JWT |
| **Health Check** | http://localhost/health | - |

---

## 🔒 Segurança

- ✅ Autenticação JWT
- ✅ Rate limiting (100 req/min anônimo, 200 req/min autenticado)
- ✅ CORS configurado
- ✅ Proteção contra força bruta
- ✅ Validações de CPF e telefone

---

## 📈 Escalabilidade

### **Suporta 1000+ usuários simultâneos:**
- 4 workers Uvicorn
- Connection pooling PostgreSQL (200 conexões)
- Redis com 2GB memória
- Nginx com rate limiting

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

## 👏 Créditos

**Desenvolvido por:** Bigu Comunicativismo  
**Apoio:** Nic.br e Ponte a Ponte  
**Região:** Metropolitana do Recife - PE

---

## 📞 Suporte

- 📧 Email: contato@bigucomunicativismo.com.br
- 🌐 Site: [bigucomunicativismo.com.br](https://bigucomunicativismo.com.br)
- 💬 Issues: [GitHub Issues](https://github.com/Bigu-Comunicativismo/conectades-back/issues)

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

