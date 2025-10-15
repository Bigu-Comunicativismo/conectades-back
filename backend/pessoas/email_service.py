"""
Serviço para envio de emails de verificação
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import CodigoVerificacao


def enviar_codigo_verificacao(email, tipo='cadastro'):
    """
    Envia código de verificação por email
    
    Args:
        email (str): Email do destinatário
        tipo (str): Tipo do código ('cadastro', 'login', 'recuperacao')
    
    Returns:
        tuple: (sucesso: bool, mensagem: str, codigo_obj: CodigoVerificacao ou None)
    """
    try:
        # Gerar código
        codigo_obj = CodigoVerificacao.gerar_codigo(email, tipo)
        
        # Definir assunto e mensagem baseado no tipo
        assuntos = {
            'cadastro': '🌟 Conectades - Código de Verificação de Cadastro',
            'login': '🔐 Conectades - Código de Verificação de Login',
            'recuperacao': '🔑 Conectades - Código de Recuperação de Senha'
        }
        
        mensagens = {
            'cadastro': f'''
Olá! 👋

Bem-vinda à plataforma Conectades!

Seu código de verificação é:

    {codigo_obj.codigo}

Este código é válido por 10 minutos e pode ser usado até 3 vezes.

Se você não solicitou este código, ignore este email.

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
            ''',
            'login': f'''
Olá! 👋

Seu código de verificação para login é:

    {codigo_obj.codigo}

Este código é válido por 10 minutos e pode ser usado até 3 vezes.

Se você não tentou fazer login, entre em contato conosco imediatamente.

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
            ''',
            'recuperacao': f'''
Olá! 👋

Você solicitou a recuperação de senha.

Seu código de verificação é:

    {codigo_obj.codigo}

Este código é válido por 10 minutos e pode ser usado até 3 vezes.

Após verificar o código, você poderá criar uma nova senha.

Se você não solicitou a recuperação de senha, ignore este email.

---
Conectades - Conectando pessoas e oportunidades
Região Metropolitana do Recife - PE
            '''
        }
        
        assunto = assuntos.get(tipo, assuntos['cadastro'])
        mensagem = mensagens.get(tipo, mensagens['cadastro'])
        
        # Enviar email
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return True, f"Código enviado para {email}", codigo_obj
    
    except Exception as e:
        return False, f"Erro ao enviar email: {str(e)}", None


def verificar_codigo(email, codigo, tipo='cadastro'):
    """
    Verifica se o código é válido
    
    Args:
        email (str): Email do usuário
        codigo (str): Código de 6 dígitos
        tipo (str): Tipo do código
    
    Returns:
        tuple: (valido: bool, mensagem: str, codigo_obj: CodigoVerificacao ou None)
    """
    try:
        # Buscar código mais recente
        codigo_obj = CodigoVerificacao.objects.filter(
            email=email,
            codigo=codigo,
            tipo=tipo,
            usado=False
        ).order_by('-data_criacao').first()
        
        if not codigo_obj:
            return False, "Código inválido ou já utilizado", None
        
        # Verificar validade
        valido, mensagem = codigo_obj.esta_valido()
        
        if not valido:
            codigo_obj.incrementar_tentativa()
            return False, mensagem, codigo_obj
        
        # Código válido
        return True, "Código verificado com sucesso", codigo_obj
    
    except Exception as e:
        return False, f"Erro ao verificar código: {str(e)}", None

