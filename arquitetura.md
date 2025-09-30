┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (1000+ usuários simultâneos)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Usuário 1 │  │   Usuário 2 │  │   Usuário 3 │  │   Usuário N │  ...     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    │ (API Calls)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              NGINX (Load Balancer)                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • Distribui requests entre instâncias                                 │    │
│  │  • SSL Termination                                                     │    │
│  │  • Rate Limiting                                                       │    │
│  │  • Static Files                                                        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Load Balance
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        UVICORN WORKERS (4 instâncias)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Worker 1  │  │   Worker 2  │  │   Worker 3  │  │   Worker 4  │          │
│  │             │  │             │  │             │  │             │          │
│  │ Django App  │  │ Django App  │  │ Django App  │  │ Django App  │          │
│  │             │  │             │  │             │  │             │          │
│  │ • Views     │  │ • Views     │  │ • Views     │  │ • Views     │          │
│  │ • Serializers│  │ • Serializers│  │ • Serializers│  │ • Serializers│          │
│  │ • Auth      │  │ • Auth      │  │ • Auth      │  │ • Auth      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Cache Check
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              REDIS CACHE                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • Cache de Campanhas (TTL: 1 hora)                                   │    │
│  │  • Cache de Doações (TTL: 15 min)                                     │    │
│  │  • Cache de Usuários (TTL: 30 min)                                    │    │
│  │  • Session Storage                                                     │    │
│  │  • Rate Limiting                                                       │    │
│  │                                                                       │    │
│  │  Memória: ~1GB RAM                                                    │    │
│  │  Performance: 1-5ms por request                                       │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Cache Miss
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            POSTGRESQL DATABASE                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  • Tabela: pessoas                                                     │    │
│  │  • Tabela: campanhas                                                   │    │
│  │  • Tabela: doacoes                                                     │    │
│  │  • Tabela: organizadoras                                               │    │
│  │                                                                       │    │
│  │  • Connection Pool: 50 conexões                                       │    │
│  │  • Query Optimization: select_related/prefetch_related                │    │
│  │  • Indexes otimizados                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘

Fluxo de Request Detalhado:

1. Usuário faz request → Frontend
2. Frontend → NGINX (Load Balancer)
3. NGINX → Uvicorn Worker (1 de 4)
4. Uvicorn → Django App
5. Django → Redis Cache
   ├─ Cache HIT → Retorna dados (1-5ms) ⚡
   └─ Cache MISS → PostgreSQL → Salva no Redis → Retorna (50-200ms)
6. Resposta → Usuário

Impacto com 1000 usuários:
Com runserver:
1000 usuários simultâneos:
- 999 usuários ficam AGUARDANDO
- 1 usuário sendo atendido
- Tempo de espera: 10-30 segundos
- Timeout: 90% dos usuários

Com Redis + Uvicorn:
1000 usuários simultâneos:
├─ 4 workers processando
├─ 80% cache hit (Redis): 5ms
├─ 20% cache miss (DB): 200ms
├─ Tempo médio: 5ms × 0.8 + 200ms × 0.2 = 44ms
├─ Throughput: 4 workers × 1000ms ÷ 44ms = ~90 requests/segundo
└─ Timeout: 0% dos usuários


Comparação de cenários:
Arquitetura	    Timeout	Throughput	Latência
Atual	        95%	    5 RPS	    500ms
Só Uvicorn	    90%	    40 RPS	    200ms
Só Redis	    95%	    5 RPS	    500ms
Redis + Uvicorn	<1%	    1000 RPS	16ms