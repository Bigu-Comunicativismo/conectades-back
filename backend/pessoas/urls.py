from django.urls import path
from . import views

urlpatterns = [
    # ========== ENDPOINTS PÚBLICOS (sem autenticação) ==========
    
    # Opções de cadastro
    path('opcoes/', views.listar_opcoes_cadastro, name='listar_opcoes_cadastro'),
    path('bairros/<str:cidade>/', views.listar_bairros_cidade, name='listar_bairros_cidade'),
    
    # Registro
    path('registro/iniciar/', views.iniciar_registro, name='iniciar_registro'),
    path('registro/confirmar/', views.confirmar_registro, name='confirmar_registro'),  # Mantido para compatibilidade
    path('registro/ativar/<uuid:token>/', views.ativar_conta, name='ativar_conta'),
    
    # Autenticação
    path('login/', views.login, name='login'),
    
    # Códigos de verificação
    path('codigo/solicitar/', views.solicitar_codigo, name='solicitar_codigo'),
    path('codigo/verificar/', views.verificar_codigo_view, name='verificar_codigo'),
    
    # Recuperação de senha em 2 etapas
    path('senha/recuperar/', views.solicitar_recuperacao_senha, name='solicitar_recuperacao_senha'),
    path('senha/redefinir/', views.redefinir_senha, name='redefinir_senha'),
    
    # ========== ENDPOINTS PROTEGIDOS (requerem JWT) ==========
    path('perfil/', views.meu_perfil, name='meu_perfil'),
    path('perfil/atualizar/', views.atualizar_perfil, name='atualizar_perfil'),
]
