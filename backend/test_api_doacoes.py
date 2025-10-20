#!/usr/bin/env python
"""
Script para testar endpoints de doações via API REST
Teste as funcionalidades sem precisar acessar o Django Admin
"""

import requests
import json
from datetime import datetime, date

# Configurações
BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def login(username, password):
    """Faz login e retorna o token JWT"""
    print_info(f"Fazendo login como: {username}")
    
    response = requests.post(
        f"{API_URL}/token/",
        json={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access')
        print_success(f"Login realizado com sucesso!")
        return token
    else:
        print_error(f"Erro no login: {response.status_code}")
        print(response.json())
        return None


def get_headers(token):
    """Retorna headers com autenticação"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def testar_doadora():
    """Testa funcionalidades da doadora"""
    print_header("🎯 TESTE: DOADORA (Ana Costa)")
    
    # Login
    token = login("ana.costa", "senha123")
    if not token:
        return
    
    headers = get_headers(token)
    
    # 1. Listar minhas doações
    print_info("1. Listando minhas doações...")
    response = requests.get(
        f"{API_URL}/doacoes/minhas/",
        headers=headers
    )
    
    if response.status_code == 200:
        doacoes = response.json()
        print_success(f"Total de doações: {len(doacoes)}")
        
        for doacao in doacoes[:3]:  # Mostrar apenas as 3 primeiras
            print(f"   • ID {doacao['id']}: {doacao['quantidade']} {doacao['unidade']} de {doacao['item_campanha_nome']}")
            print(f"     Campanha: {doacao['campanha_titulo']}")
            print(f"     Status: {doacao['status']}")
            print()
    else:
        print_error(f"Erro ao listar doações: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
        return
    
    # 2. Tentar cancelar uma doação pendente
    doacao_pendente = next((d for d in doacoes if d['status'] == 'pendente'), None)
    
    if doacao_pendente:
        print_info(f"2. Cancelando doação ID {doacao_pendente['id']}...")
        
        response = requests.patch(
            f"{API_URL}/doacoes/{doacao_pendente['id']}/atualizar-status/",
            headers=headers,
            json={
                "status": "cancelada",
                "observacoes": "Não poderei entregar esta doação"
            }
        )
        
        if response.status_code == 200:
            print_success("Doação cancelada com sucesso!")
            result = response.json()
            print(f"   Mensagem: {result.get('mensagem')}")
        else:
            print_error(f"Erro ao cancelar doação: {response.status_code}")
            print(response.json())
    else:
        print_warning("Nenhuma doação pendente encontrada para cancelar")
    
    # 3. Tentar alterar data de entrega (DEVE FALHAR)
    if doacoes:
        print_info(f"3. Tentando alterar data de entrega da doação ID {doacoes[0]['id']} (deve falhar)...")
        
        response = requests.patch(
            f"{API_URL}/doacoes/{doacoes[0]['id']}/atualizar-status/",
            headers=headers,
            json={
                "data_entrega": str(date.today())
            }
        )
        
        if response.status_code == 403:
            print_success("Bloqueio funcionou! Doadora não pode alterar data de entrega")
            print(f"   Mensagem: {response.json().get('erro')}")
        else:
            print_error(f"Atenção! Doadora conseguiu alterar data de entrega (não deveria)")


def testar_beneficiaria():
    """Testa funcionalidades da beneficiária"""
    print_header("🎯 TESTE: BENEFICIÁRIA (Carla Oliveira)")
    
    # Login
    token = login("carla.oliveira", "senha123")
    if not token:
        return
    
    headers = get_headers(token)
    
    # 1. Listar doações das minhas campanhas
    print_info("1. Listando doações das minhas campanhas...")
    response = requests.get(
        f"{API_URL}/doacoes/minhas-campanhas/",
        headers=headers
    )
    
    if response.status_code == 200:
        doacoes = response.json()
        print_success(f"Total de doações recebidas: {len(doacoes)}")
        
        for doacao in doacoes:
            print(f"   • ID {doacao['id']}: {doacao['quantidade']} {doacao['unidade']} de {doacao['item_campanha_nome']}")
            print(f"     Doador: {doacao['doador_nome']}")
            print(f"     Campanha: {doacao['campanha_titulo']}")
            print(f"     Status: {doacao['status']}")
            print()
    else:
        print_error(f"Erro ao listar doações: {response.status_code}")
        print(response.json())
        return
    
    # 2. Atualizar status para "entregue" e definir data de entrega
    doacao_confirmada = next((d for d in doacoes if d['status'] == 'confirmada'), None)
    
    if doacao_confirmada:
        print_info(f"2. Atualizando status da doação ID {doacao_confirmada['id']} para 'entregue'...")
        
        response = requests.patch(
            f"{API_URL}/doacoes/{doacao_confirmada['id']}/atualizar-status/",
            headers=headers,
            json={
                "status": "entregue",
                "data_entrega": str(date.today()),
                "observacoes": "Doação recebida com sucesso! Muito obrigada!"
            }
        )
        
        if response.status_code == 200:
            print_success("Status atualizado com sucesso!")
            result = response.json()
            print(f"   Mensagem: {result.get('mensagem')}")
            print(f"   Novo status: {result['doacao']['status']}")
        else:
            print_error(f"Erro ao atualizar status: {response.status_code}")
            print(response.json())
    else:
        print_warning("Nenhuma doação confirmada encontrada para atualizar")
    
    # 3. Confirmar uma doação pendente
    doacao_pendente = next((d for d in doacoes if d['status'] == 'pendente'), None)
    
    if doacao_pendente:
        print_info(f"3. Confirmando doação ID {doacao_pendente['id']}...")
        
        response = requests.patch(
            f"{API_URL}/doacoes/{doacao_pendente['id']}/atualizar-status/",
            headers=headers,
            json={
                "status": "confirmada",
                "observacoes": "Doação confirmada, aguardando entrega"
            }
        )
        
        if response.status_code == 200:
            print_success("Doação confirmada com sucesso!")
        else:
            print_error(f"Erro ao confirmar doação: {response.status_code}")
            print(response.json())


def testar_beneficiaria_fernanda():
    """Testa funcionalidades da beneficiária Fernanda Lima"""
    print_header("🎯 TESTE: BENEFICIÁRIA (Fernanda Lima)")
    
    # Login
    token = login("fernanda.lima", "senha123")
    if not token:
        return
    
    headers = get_headers(token)
    
    # Listar doações das minhas campanhas
    print_info("Listando doações das minhas campanhas...")
    response = requests.get(
        f"{API_URL}/doacoes/minhas-campanhas/",
        headers=headers
    )
    
    if response.status_code == 200:
        doacoes = response.json()
        print_success(f"Total de doações recebidas: {len(doacoes)}")
        
        # Mostrar estatísticas
        status_count = {}
        for doacao in doacoes:
            status = doacao['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        print("\n   📊 Estatísticas:")
        for status, count in status_count.items():
            emoji = {'pendente': '⏳', 'confirmada': '✅', 'entregue': '📦', 'cancelada': '❌'}.get(status, '❓')
            print(f"      {emoji} {status.title()}: {count}")


def main():
    """Executa todos os testes"""
    print_header("🧪 TESTES DE API DE DOAÇÕES")
    print_info("Este script testa os endpoints da API de doações")
    print_info("Servidor deve estar rodando em: http://localhost:8001")
    print()
    
    try:
        # Testar doadora
        testar_doadora()
        
        # Testar beneficiárias
        testar_beneficiaria()
        testar_beneficiaria_fernanda()
        
        print_header("✅ TESTES CONCLUÍDOS")
        print_success("Todos os testes foram executados!")
        print()
        print_info("Para testar manualmente, use os endpoints:")
        print(f"   • GET  {API_URL}/doacoes/minhas/ - Listar minhas doações (doadora)")
        print(f"   • GET  {API_URL}/doacoes/minhas-campanhas/ - Listar doações recebidas (beneficiária)")
        print(f"   • GET  {API_URL}/doacoes/<id>/ - Detalhar doação")
        print(f"   • PATCH {API_URL}/doacoes/<id>/atualizar-status/ - Atualizar status")
        print()
        
    except requests.exceptions.ConnectionError:
        print_error("Não foi possível conectar ao servidor!")
        print_warning("Certifique-se de que o servidor está rodando em http://localhost:8001")
        print_info("Execute: python manage.py runserver 8001")
    except Exception as e:
        print_error(f"Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

