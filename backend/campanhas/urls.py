from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_campanha, name='criar_campanha'),
    path('listar/', views.listar_campanhas, name='listar_campanhas'),
    path('minhas/', views.minhas_campanhas, name='minhas_campanhas'),
    path('beneficiaria/', views.campanhas_beneficiaria, name='campanhas_beneficiaria'),
]

