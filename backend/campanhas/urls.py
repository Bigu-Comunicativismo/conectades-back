from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_campanha, name='criar_campanha'),
    path('listar/', views.listar_campanhas, name='listar_campanhas'),
    path('minhas/', views.minhas_campanhas, name='minhas_campanhas'),
    path('<int:campanha_id>/', views.detalhar_campanha, name='detalhar_campanha'),
    path('<int:campanha_id>/itens/', views.listar_itens_campanha, name='listar_itens_campanha'),
    
    # Solicitações de Beneficiária
    path('solicitacoes/minhas/', views.minhas_solicitacoes_beneficiaria, name='minhas_solicitacoes_beneficiaria'),
    path('solicitacoes/<int:solicitacao_id>/aceitar/', views.aceitar_solicitacao_beneficiaria, name='aceitar_solicitacao_beneficiaria'),
    path('solicitacoes/<int:solicitacao_id>/recusar/', views.recusar_solicitacao_beneficiaria, name='recusar_solicitacao_beneficiaria'),
]

