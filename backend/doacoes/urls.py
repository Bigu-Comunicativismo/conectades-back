from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_doacao, name='criar_doacao'),
    path('campanha/<int:campanha_id>/', views.listar_doacoes_por_campanha, name='listar_doacoes_por_campanha'),
]







