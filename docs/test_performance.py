#!/usr/bin/env python3
"""
Script para testar performance da API com Redis + Uvicorn + Nginx
Otimizado para 1000+ usuários simultâneos
"""
import requests
import time
import concurrent.futures
import json
import statistics
from datetime import datetime

BASE_URL = "http://localhost"  # Nginx
API_BASE = "http://localhost/api"
TOKEN = None

def get_auth_token():
    """Obter token JWT para autenticação"""
    global TOKEN
    if TOKEN:
        return TOKEN
    
    # Assumindo que existe um usuário de teste
    login_data = {
        "username": "admin",  # ou seu usuário de teste
        "password": "admin123"  # ou sua senha de teste
    }
    
    try:
        response = requests.post(f"{API_BASE}/token/", json=login_data, timeout=10)
        if response.status_code == 200:
            TOKEN = response.json()["access"]
            return TOKEN
        else:
            print(f"Erro ao obter token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erro na requisição de login: {e}")
        return None

def make_request(endpoint, headers, timeout=30):
    """Fazer uma requisição para um endpoint"""
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=timeout)
        end_time = time.time()
        
        return {
            'endpoint': endpoint,
            'status_code': response.status_code,
            'response_time': end_time - start_time,
            'success': response.status_code == 200,
            'content_length': len(response.content) if response.content else 0
        }
    except requests.exceptions.Timeout:
        return {
            'endpoint': endpoint,
            'status_code': 0,
            'response_time': timeout,
            'success': False,
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'status_code': 0,
            'response_time': 0,
            'success': False,
            'error': str(e)
        }

def test_performance(concurrent_users=100, requests_per_user=10, test_name="Teste"):
    """Testar performance com múltiplos usuários simultâneos"""
    token = get_auth_token()
    if not token:
        print("❌ Não foi possível obter token de autenticação")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/campanhas/listar/",
        "/campanhas/minhas/",
        "/campanhas/beneficiaria/",
    ]
    
    print(f"\n🚀 {test_name}")
    print(f"👥 Usuários simultâneos: {concurrent_users}")
    print(f"📊 Requests por usuário: {requests_per_user}")
    print(f"🔗 Endpoints: {len(endpoints)}")
    print(f"📈 Total de requests: {concurrent_users * requests_per_user * len(endpoints)}")
    
    all_requests = []
    for _ in range(concurrent_users):
        for _ in range(requests_per_user):
            for endpoint in endpoints:
                all_requests.append((endpoint, headers))
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(make_request, endpoint, headers) for endpoint, headers in all_requests]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Análise dos resultados
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    if successful_requests:
        response_times = [r['response_time'] for r in successful_requests]
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max_response_time
    else:
        avg_response_time = median_response_time = max_response_time = min_response_time = p95_response_time = 0
    
    # Calcular throughput
    throughput = len(all_requests) / total_time if total_time > 0 else 0
    
    print(f"\n📊 RESULTADOS:")
    print(f"⏱️  Tempo total: {total_time:.2f}s")
    print(f"🚀 Throughput: {throughput:.2f} requests/segundo")
    print(f"✅ Requests bem-sucedidos: {len(successful_requests)}")
    print(f"❌ Requests falharam: {len(failed_requests)}")
    print(f"📈 Taxa de sucesso: {len(successful_requests) / len(all_requests) * 100:.1f}%")
    print(f"⚡ Tempo de resposta médio: {avg_response_time:.3f}s")
    print(f"📊 Tempo de resposta mediano: {median_response_time:.3f}s")
    print(f"📈 P95 tempo de resposta: {p95_response_time:.3f}s")
    print(f"🔝 Tempo de resposta máximo: {max_response_time:.3f}s")
    print(f"🔻 Tempo de resposta mínimo: {min_response_time:.3f}s")
    
    # Verificar se está dentro dos parâmetros esperados
    if throughput >= 500 and avg_response_time <= 0.1 and len(successful_requests) / len(all_requests) >= 0.95:
        print("🎉 ✅ PERFORMANCE EXCELENTE - Suporta 1000+ usuários!")
    elif throughput >= 200 and avg_response_time <= 0.2 and len(successful_requests) / len(all_requests) >= 0.90:
        print("👍 ✅ PERFORMANCE BOA - Suporta 500+ usuários")
    elif throughput >= 100 and avg_response_time <= 0.5 and len(successful_requests) / len(all_requests) >= 0.80:
        print("⚠️  ⚠️  PERFORMANCE REGULAR - Suporta 200+ usuários")
    else:
        print("❌ ❌ PERFORMANCE RUIM - Precisa de otimizações")
    
    return {
        'test_name': test_name,
        'concurrent_users': concurrent_users,
        'total_requests': len(all_requests),
        'successful_requests': len(successful_requests),
        'failed_requests': len(failed_requests),
        'success_rate': len(successful_requests) / len(all_requests) * 100,
        'total_time': total_time,
        'throughput': throughput,
        'avg_response_time': avg_response_time,
        'median_response_time': median_response_time,
        'p95_response_time': p95_response_time,
        'max_response_time': max_response_time,
        'min_response_time': min_response_time
    }

def test_cache_performance():
    """Testar performance do cache Redis"""
    print("\n🧪 TESTE DE CACHE REDIS")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Não foi possível obter token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "/campanhas/listar/"
    
    # Primeira execução (cache miss)
    print("🔄 Primeira execução (cache miss)...")
    start_time = time.time()
    response1 = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=30)
    time1 = time.time() - start_time
    
    # Segunda execução (cache hit)
    print("⚡ Segunda execução (cache hit)...")
    start_time = time.time()
    response2 = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=30)
    time2 = time.time() - start_time
    
    print(f"\n📊 RESULTADOS DO CACHE:")
    print(f"🔄 Cache miss: {time1:.3f}s")
    print(f"⚡ Cache hit: {time2:.3f}s")
    print(f"🚀 Melhoria: {time1/time2:.1f}x mais rápido")
    
    if time2 < time1 * 0.5:
        print("✅ Cache funcionando perfeitamente!")
    else:
        print("⚠️  Cache pode não estar funcionando corretamente")

def main():
    """Executar todos os testes de performance"""
    print("🎯 TESTE DE PERFORMANCE - CONECTADES API")
    print("=" * 60)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Arquitetura: Nginx + Redis + Uvicorn + Django")
    print("🎯 Objetivo: Suportar 1000+ usuários simultâneos")
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print("⚠️  Servidor pode não estar funcionando corretamente")
    except:
        print("❌ Servidor não está acessível. Execute: docker-compose up")
        return
    
    results = []
    
    # Teste de cache
    test_cache_performance()
    
    # Testes de carga progressivos
    test_configs = [
        (50, 5, "Teste Leve (50 usuários)"),
        (100, 10, "Teste Médio (100 usuários)"),
        (200, 10, "Teste Pesado (200 usuários)"),
        (500, 5, "Teste Extremo (500 usuários)"),
    ]
    
    for concurrent_users, requests_per_user, test_name in test_configs:
        try:
            result = test_performance(concurrent_users, requests_per_user, test_name)
            if result:
                results.append(result)
        except KeyboardInterrupt:
            print("\n⏹️  Teste interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
    
    # Resumo final
    if results:
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL DOS TESTES")
        print("=" * 60)
        
        for result in results:
            print(f"\n🧪 {result['test_name']}:")
            print(f"   👥 Usuários: {result['concurrent_users']}")
            print(f"   🚀 Throughput: {result['throughput']:.1f} RPS")
            print(f"   ⚡ Latência média: {result['avg_response_time']:.3f}s")
            print(f"   📈 Taxa de sucesso: {result['success_rate']:.1f}%")
    
    print(f"\n🕐 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

