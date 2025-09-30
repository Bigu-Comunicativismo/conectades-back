from django.contrib import admin
from django.contrib import messages
from .models import Organizadora, Campanha

@admin.register(Organizadora)
class OrganizadoraAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'data_cadastro', 'ativo')
    list_filter = ('ativo', 'data_cadastro')
    search_fields = ('pessoa__username', 'pessoa__nome', 'pessoa__nome_alias')
    readonly_fields = ('data_cadastro',)

@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizadora', 'beneficiaria', 'data_inicio', 'data_fim')
    list_filter = ('data_inicio', 'data_fim', 'organizadora__ativo')
    search_fields = ('titulo', 'descricao', 'organizadora__pessoa__nome', 'beneficiaria__nome')
    date_hierarchy = 'data_inicio'
    
    def save_model(self, request, obj, form, change):
        # Se não há organizadora definida, usar o usuário atual
        if not obj.organizadora_id:
            # Verificar se o usuário atual já tem perfil de organizadora
            try:
                organizadora = Organizadora.objects.get(pessoa=request.user)
            except Organizadora.DoesNotExist:
                # Criar perfil de organizadora para o usuário atual
                organizadora = Organizadora.objects.create(pessoa=request.user)
                messages.info(request, f'Perfil de organizadora criado automaticamente para {request.user.username}')
            
            obj.organizadora = organizadora
        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Se é uma nova campanha, configurar o campo organizadora
        if not obj:
            # Tentar obter o perfil de organizadora do usuário atual
            try:
                organizadora = Organizadora.objects.get(pessoa=request.user)
                form.base_fields['organizadora'].initial = organizadora
                form.base_fields['organizadora'].help_text = f'Será preenchido automaticamente com: {organizadora}'
            except Organizadora.DoesNotExist:
                form.base_fields['organizadora'].help_text = 'Será criado automaticamente um perfil de organizadora para você'
            
            form.base_fields['organizadora'].widget.attrs['readonly'] = True
        
        return form