from django.urls import path
from . import views

urlpatterns = [
    # Doações tradicionais
    path('criar/', views.criar_doacao, name='criar_doacao'),
    path('campanha/<int:campanha_id>/', views.listar_doacoes_por_campanha, name='listar_doacoes_por_campanha'),
    path('minhas/', views.minhas_doacoes, name='minhas_doacoes'),  # Doações da doadora
    path('minhas-campanhas/', views.doacoes_minhas_campanhas, name='doacoes_minhas_campanhas'),  # Doações recebidas pela beneficiária
    path('<int:doacao_id>/', views.detalhar_doacao, name='detalhar_doacao'),
    path('<int:doacao_id>/atualizar-status/', views.atualizar_status_doacao, name='atualizar_status_doacao'),
    
    # Tipos de Serviço (para Doações Independentes)
    path('tipos-servico/', views.listar_tipos_servico, name='listar_tipos_servico'),
    path('tipos-servico/criar/', views.criar_tipo_servico, name='criar_tipo_servico'),
    
    # Doações Independentes
    path('independentes/', views.listar_doacoes_independentes, name='listar_doacoes_independentes'),
    path('independentes/criar/', views.criar_doacao_independente, name='criar_doacao_independente'),
    path('independentes/minhas/', views.minhas_doacoes_independentes, name='minhas_doacoes_independentes'),
    path('independentes/<int:doacao_id>/', views.detalhar_doacao_independente, name='detalhar_doacao_independente'),
    path('independentes/<int:doacao_id>/atualizar/', views.atualizar_doacao_independente, name='atualizar_doacao_independente'),
    path('independentes/<int:doacao_id>/pausar/', views.pausar_doacao_independente, name='pausar_doacao_independente'),
    path('independentes/<int:doacao_id>/reativar/', views.reativar_doacao_independente, name='reativar_doacao_independente'),

]







