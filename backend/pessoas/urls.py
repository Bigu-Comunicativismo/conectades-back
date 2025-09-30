from django.urls import path
from . import views

urlpatterns = [
    path('beneficiaria/', views.cadastro_beneficiaria, name='cadastro_beneficiaria'),
    path('doadora/', views.cadastro_doadora, name='cadastro_doadora'),
    path('organizadora/', views.cadastro_organizadora, name='cadastro_organizadora'),
]

