from django.urls import path

from .views_confirmation import confirmar_doacao_via_link


urlpatterns = [
    path('confirmar/<str:token>/', confirmar_doacao_via_link, name='confirmar_doacao_link'),
]

