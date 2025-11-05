"""
Views para ativação de conta via link do email
"""
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CodigoVerificacao
from django.core.cache import cache
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def ativar_conta_via_link(request, token):
    """
    Ativa a conta do usuário através do link recebido por email.
    
    Esta é uma view HTML simples que:
    1. Recebe o token da URL
    2. Valida o token
    3. Ativa a conta
    4. Mostra mensagem de sucesso ou erro
    
    URL: /auth/ativar/<token>/
    """
    try:
        logger.info(f"🔍 Tentando ativar conta com token: {token}")
        # Buscar o código de verificação pelo token
        codigo_verificacao = CodigoVerificacao.objects.filter(
            token=token,
            tipo='cadastro',
            usado=False
        ).first()
        
        if not codigo_verificacao:
            return HttpResponse("""
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Link Inválido - Conectades</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                            max-width: 500px;
                        }
                        h1 { color: #e74c3c; margin-bottom: 20px; }
                        p { color: #555; line-height: 1.6; margin: 15px 0; }
                        .icon { font-size: 64px; margin-bottom: 20px; }
                        a {
                            display: inline-block;
                            margin-top: 20px;
                            padding: 12px 30px;
                            background: #667eea;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            transition: background 0.3s;
                        }
                        a:hover { background: #5568d3; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">❌</div>
                        <h1>Link Inválido ou Expirado</h1>
                        <p>Este link de ativação é inválido ou já foi utilizado.</p>
                        <p><strong>Possíveis motivos:</strong></p>
                        <ul style="text-align: left; color: #666;">
                            <li>O link já foi usado anteriormente</li>
                            <li>O link expirou (válido por 24 horas)</li>
                            <li>O token está incorreto</li>
                        </ul>
                        <p>Se você precisa ativar sua conta, solicite um novo código de ativação.</p>
                        <a href="/api/docs/">Ir para API Docs</a>
                    </div>
                </body>
                </html>
            """, content_type="text/html")
        
        # Verificar se o código está válido (não expirado)
        valido, mensagem = codigo_verificacao.esta_valido()
        
        if not valido:
            return HttpResponse(f"""
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Link Expirado - Conectades</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                            max-width: 500px;
                        }}
                        h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                        p {{ color: #555; line-height: 1.6; margin: 15px 0; }}
                        .icon {{ font-size: 64px; margin-bottom: 20px; }}
                        a {{
                            display: inline-block;
                            margin-top: 20px;
                            padding: 12px 30px;
                            background: #667eea;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            transition: background 0.3s;
                        }}
                        a:hover {{ background: #5568d3; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">⏰</div>
                        <h1>Link Expirado</h1>
                        <p>{mensagem}</p>
                        <p>Os links de ativação são válidos por <strong>24 horas</strong>.</p>
                        <p>Solicite um novo código de ativação através da API.</p>
                        <a href="/api/docs/">Ir para API Docs</a>
                    </div>
                </body>
                </html>
            """, content_type="text/html")
        
        # Recuperar dados do registro do cache
        email = codigo_verificacao.email
        cache_key = f'registro_pendente_{email}'
        dados_registro = cache.get(cache_key)
        
        if not dados_registro:
            return HttpResponse("""
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Dados Expirados - Conectades</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            text-align: center;
                            max-width: 500px;
                        }
                        h1 { color: #e74c3c; margin-bottom: 20px; }
                        p { color: #555; line-height: 1.6; margin: 15px 0; }
                        .icon { font-size: 64px; margin-bottom: 20px; }
                        a {
                            display: inline-block;
                            margin-top: 20px;
                            padding: 12px 30px;
                            background: #667eea;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            transition: background 0.3s;
                        }
                        a:hover { background: #5568d3; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">🕐</div>
                        <h1>Dados de Registro Expirados</h1>
                        <p>Os dados do seu registro expiraram.</p>
                        <p>Por favor, faça o registro novamente através da API.</p>
                        <a href="/api/docs/">Ir para API Docs</a>
                    </div>
                </body>
                </html>
            """, content_type="text/html")
        
        # Criar a conta do usuário
        with transaction.atomic():
            from .models import Pessoa, TipoUsuario, Genero
            from rest_framework_simplejwt.tokens import RefreshToken
            
            # Criar usuário básico primeiro
            user = Pessoa.objects.create_user(
                username=dados_registro['email'],
                email=dados_registro['email'],
                password=dados_registro['password'],
                is_active=True  # Ativar a conta
            )
            
            # Configurar campos adicionais
            user.nome_completo = dados_registro['nome_completo']
            user.cpf = dados_registro.get('cpf', '')
            user.telefone = dados_registro.get('telefone', '')
            user.nome_social = dados_registro.get('nome_social', dados_registro['nome_completo'])
            user.mini_bio = dados_registro.get('mini_bio', '')
            user.cidade = dados_registro.get('cidade', '')
            user.bairro = dados_registro.get('bairro', '')
            
            # Data de nascimento (se existir)
            if dados_registro.get('data_nascimento'):
                user.data_nascimento = dados_registro['data_nascimento']
            
            # Tipo de usuário
            if dados_registro.get('tipo_usuario'):
                user.tipo_usuario = TipoUsuario.objects.get(id=dados_registro['tipo_usuario'])
            
            # Gênero
            if dados_registro.get('genero'):
                user.genero = Genero.objects.get(id=dados_registro['genero'])
            
            # Salvar usuário com todos os campos
            user.save()
            
            # Adicionar categorias e localizações de interesse
            if 'categorias_interesse' in dados_registro:
                user.categorias_interesse.set(dados_registro['categorias_interesse'])
            
            if 'localizacoes_interesse' in dados_registro:
                user.localizacoes_interesse.set(dados_registro['localizacoes_interesse'])
            
            # Marcar código como usado
            codigo_verificacao.marcar_como_usado()
            
            # Limpar cache
            cache.delete(cache_key)
            
            logger.info(f"✅ Conta ativada com sucesso via link: {email}")
        
        # Retornar página de sucesso
        return HttpResponse(f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Conta Ativada - Conectades</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{ color: #27ae60; margin-bottom: 20px; }}
                    p {{ color: #555; line-height: 1.6; margin: 15px 0; }}
                    .icon {{ font-size: 64px; margin-bottom: 20px; }}
                    .info-box {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border-left: 4px solid #27ae60;
                    }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 30px;
                        background: #27ae60;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        transition: background 0.3s;
                    }}
                    a:hover {{ background: #219653; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>Conta Ativada com Sucesso!</h1>
                    <p>Bem-vinda à plataforma Conectades!</p>
                    
                    <div class="info-box">
                        <strong>Email:</strong> {email}<br>
                        <strong>Status:</strong> Conta Ativa
                    </div>
                    
                    <p>Sua conta foi ativada e você já pode fazer login!</p>
                    <p>Use o email e senha cadastrados para acessar a plataforma.</p>
                    
                    <a href="/api/docs/">Fazer Login na API</a>
                </div>
            </body>
            </html>
        """, content_type="text/html")
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Erro ao ativar conta via link: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return HttpResponse(f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Erro - Conectades</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }}
                    h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                    p {{ color: #555; line-height: 1.6; margin: 15px 0; }}
                    .icon {{ font-size: 64px; margin-bottom: 20px; }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 30px;
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        transition: background 0.3s;
                    }}
                    a:hover {{ background: #5568d3; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⚠️</div>
                    <h1>Erro ao Ativar Conta</h1>
                    <p>Ocorreu um erro ao processar a ativação da sua conta.</p>
                    <p>Por favor, entre em contato com o suporte ou tente novamente mais tarde.</p>
                    <a href="/api/docs/">Ir para API Docs</a>
                </div>
            </body>
            </html>
        """, content_type="text/html")

