#!/usr/bin/env python3
"""
Script para testar envio de emails
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao PYTHONPATH
sys.path.insert(0, '/home/lelo/conectades')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')

# Configurar Django
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Testa envio de email"""
    print("\n" + "="*70)
    print("🧪 TESTE DE ENVIO DE EMAIL")
    print("="*70 + "\n")
    
    # Mostrar configurações atuais
    print("📋 Configurações de Email:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    if 'smtp' in settings.EMAIL_BACKEND.lower():
        print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"  EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(não configurado)'}")
    
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Solicitar email de destino
    email_destino = input("📧 Digite o email de destino para teste: ").strip()
    
    if not email_destino:
        print("❌ Email não fornecido. Teste cancelado.")
        return
    
    print(f"\n📤 Enviando email de teste para: {email_destino}")
    print("⏳ Aguarde...")
    
    try:
        send_mail(
            subject='🧪 Teste de Envio - Conectades',
            message='''
Olá! 👋

Este é um email de teste da plataforma Conectades.

Se você recebeu este email, significa que o sistema de envio está funcionando corretamente! ✅

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            fail_silently=False,
        )
        
        print("\n✅ Email enviado com sucesso!")
        print(f"📬 Verifique a caixa de entrada de: {email_destino}")
        print("⚠️  Não se esqueça de verificar a pasta de SPAM/Lixo Eletrônico")
        
    except Exception as e:
        print(f"\n❌ Erro ao enviar email:")
        print(f"   {type(e).__name__}: {str(e)}")
        print()
        
        # Dicas de solução
        print("💡 Possíveis soluções:")
        print("   1. Verifique se EMAIL_HOST_USER e EMAIL_HOST_PASSWORD estão corretos no .env")
        print("   2. Para Gmail, use uma 'Senha de App', não sua senha normal")
        print("      Gere em: https://myaccount.google.com/apppasswords")
        print("   3. Verifique se a verificação em duas etapas está ativada (obrigatório para Gmail)")
        print("   4. Verifique se não há espaços extras na senha no arquivo .env")
        print()
    
    print("="*70 + "\n")

if __name__ == '__main__':
    test_email()

