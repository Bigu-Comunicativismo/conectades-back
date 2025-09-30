from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Pessoa

@admin.register(Pessoa)
class PessoaAdmin(UserAdmin):
    list_display = ('username', 'nome', 'nome_alias', 'email', 'tipo', 'cidade', 'is_active')
    list_filter = ('tipo', 'is_active', 'is_staff', 'cidade')
    search_fields = ('username', 'nome', 'nome_alias', 'email', 'cpf')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Pessoais', {
            'fields': ('tipo', 'nome', 'cpf', 'telefone', 'cidade', 'bairro', 'endereco')
        }),
        ('Perfil Público', {
            'fields': ('nome_alias', 'mini_bio', 'foto')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais', {
            'fields': ('tipo', 'nome', 'cpf', 'telefone', 'cidade', 'bairro', 'endereco')
        }),
        ('Perfil Público', {
            'fields': ('nome_alias', 'mini_bio', 'foto')
        }),
    )