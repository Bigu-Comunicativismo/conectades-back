#!/usr/bin/env python3
"""
Script de Teste de SMTP para VPS
Execute no servidor VPS com Docker:

cd /var/www/conectades-dev
docker compose exec web python test_smtp_vps.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("\n" + "="*60)
print("🔍 TESTE DE CONFIGURAÇÃO SMTP")
print("="*60 + "\n")

# 1. Verificar configurações
print("📋 CONFIGURAÇÕES ATUAIS:")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(vazio)'}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# 2. Verificar se está usando console backend
if 'console' in settings.EMAIL_BACKEND.lower():
    print("❌ ERRO: EMAIL_BACKEND está configurado como 'console'")
    print("   Emails não serão enviados, apenas exibidos no console!")
    print()
    print("✅ SOLUÇÃO:")
    print("   Verifique o arquivo .env no servidor e certifique-se que:")
    print("   EMAIL_BACKEND=smtp")
    print()
    sys.exit(1)

# 3. Verificar se credenciais estão definidas
if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("❌ ERRO: Credenciais SMTP não configuradas!")
    print(f"   EMAIL_HOST_USER: {'✅ OK' if settings.EMAIL_HOST_USER else '❌ VAZIO'}")
    print(f"   EMAIL_HOST_PASSWORD: {'✅ OK' if settings.EMAIL_HOST_PASSWORD else '❌ VAZIO'}")
    print()
    print("✅ SOLUÇÃO:")
    print("   Configure no arquivo .env do servidor:")
    print("   EMAIL_HOST_USER=contato@bigu.org.br")
    print("   EMAIL_HOST_PASSWORD=sua_senha_app_gmail")
    print()
    sys.exit(1)

# 4. Testar envio de email
print("📧 TESTANDO ENVIO DE EMAIL...")
print()

email_teste = input("Digite o email para teste (ou Enter para usar contato@bigu.org.br): ").strip()
if not email_teste:
    email_teste = "contato@bigu.org.br"

try:
    print(f"   Enviando email de teste para: {email_teste}")
    print("   Aguarde...")
    
    send_mail(
        subject='🧪 Teste SMTP - Conectades',
        message='''
Olá! 👋

Este é um email de TESTE do sistema Conectades.

Se você recebeu este email, significa que o SMTP está configurado corretamente! ✅

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_teste],
        fail_silently=False,
    )
    
    print()
    print("✅ EMAIL ENVIADO COM SUCESSO!")
    print()
    print("🔍 PRÓXIMOS PASSOS:")
    print("   1. Verifique a caixa de entrada de:", email_teste)
    print("   2. Se não encontrar, verifique a pasta de SPAM")
    print("   3. Aguarde até 2 minutos (atraso normal de SMTP)")
    print()
    print("📊 LOGS:")
    print("   - Se o email não chegou, verifique os logs do container:")
    print("     docker compose logs web | grep -i mail")
    print()
    
except Exception as e:
    print()
    print("❌ ERRO AO ENVIAR EMAIL!")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensagem: {str(e)}")
    print()
    print("🔍 POSSÍVEIS CAUSAS:")
    print("   1. Senha do Gmail incorreta")
    print("   2. Verificação em 2 etapas não ativada")
    print("   3. Senha de App não gerada")
    print("   4. Firewall bloqueando porta 587")
    print("   5. Gmail bloqueou o acesso (menos provável com senha de app)")
    print()
    print("✅ SOLUÇÕES:")
    print("   1. Verifique a senha de app no Gmail")
    print("   2. Gere uma nova senha de app")
    print("   3. Teste telnet smtp.gmail.com 587")
    print("   4. Verifique logs: docker compose logs web")
    print()
    sys.exit(1)

print("="*60)
print("✅ TESTE CONCLUÍDO COM SUCESSO")
print("="*60)

