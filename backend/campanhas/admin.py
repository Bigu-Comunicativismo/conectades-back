from django.contrib import admin
from django.contrib import messages
from .models import Organizadora, Campanha

# Organizadora NÃO aparece no admin - é criada automaticamente
# quando uma Doadora cria sua primeira campanha

@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizadora', 'beneficiaria', 'data_inicio', 'data_fim')
    list_filter = ('data_inicio', 'data_fim', 'organizadora__ativo')
    search_fields = ('titulo', 'descricao', 'organizadora__pessoa__nome_completo', 'beneficiaria__nome_completo')
    date_hierarchy = 'data_inicio'
    
    def save_model(self, request, obj, form, change):
        # Verificar se o usuário é uma Doadora
        from backend.pessoas.models import TipoUsuario
        
        try:
            tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
            
            if request.user.tipo_usuario != tipo_doadora:
                messages.error(request, 'Apenas Doadoras podem criar campanhas!')
                return
        except Exception as e:
            messages.error(request, f'Erro ao verificar tipo de usuário: {str(e)}')
            return
        
        # Se não há organizadora definida, usar o usuário atual
        if not obj.organizadora_id:
            # Verificar se o usuário atual já tem perfil de organizadora
            organizadora, created = Organizadora.objects.get_or_create(
                pessoa=request.user,
                defaults={'ativo': True}
            )
            
            if created:
                messages.success(
                    request, 
                    f'🎉 Parabéns! Você agora é uma Organizadora e pode criar campanhas!'
                )
            
            obj.organizadora = organizadora
        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Ocultar campo organizadora - será preenchido automaticamente
        if 'organizadora' in form.base_fields:
            form.base_fields['organizadora'].required = False
            form.base_fields['organizadora'].widget = admin.widgets.AdminTextInputWidget(attrs={'style': 'display:none;'})
            
            # Se já existe organizadora para este usuário, preencher
            try:
                organizadora = Organizadora.objects.get(pessoa=request.user)
                form.base_fields['organizadora'].initial = organizadora
            except Organizadora.DoesNotExist:
                pass
        
        return form
    
    def get_readonly_fields(self, request, obj=None):
        """Organizadora é sempre readonly - preenchida automaticamente"""
        if obj:  # Editando campanha existente
            return self.readonly_fields + ('organizadora',)
        return self.readonly_fields