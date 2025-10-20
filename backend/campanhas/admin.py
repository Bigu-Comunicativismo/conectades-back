from django.contrib import admin
from django.contrib import messages
from .models import Organizadora, Campanha, Imagem, ItemCampanha, PostAtualizacao

# Organizadora NÃO aparece no admin - é criada automaticamente
# quando uma Doadora cria sua primeira campanha

@admin.register(Imagem)
class ImagemAdmin(admin.ModelAdmin):
    list_display = ('alt', 'src', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('alt',)

@admin.register(ItemCampanha)
class ItemCampanhaAdmin(admin.ModelAdmin):
    list_display = ('get_nome_completo', 'campanha', 'quantidade_solicitada', 'quantidade_contribuida', 'unidade', 'percentual_atingido')
    list_filter = ('campanha', 'data_criacao')
    search_fields = ('nome', 'campanha__titulo')
    ordering = ['campanha', 'nome']
    
    def get_nome_completo(self, obj):
        """Retorna nome com progresso"""
        return f"{obj.nome} ({obj.quantidade_contribuida}/{obj.quantidade_solicitada} {obj.unidade})"
    get_nome_completo.short_description = 'Item'
    get_nome_completo.admin_order_field = 'nome'
    
    def percentual_atingido(self, obj):
        """Exibe o percentual formatado"""
        return f"{obj.percentual_atingido:.1f}%"
    percentual_atingido.short_description = '% Atingido'

@admin.register(PostAtualizacao)
class PostAtualizacaoAdmin(admin.ModelAdmin):
    list_display = ('get_resumo', 'campanha', 'data_criacao')
    list_filter = ('campanha', 'data_criacao')
    search_fields = ('mensagem', 'campanha__titulo')
    date_hierarchy = 'data_criacao'
    
    def get_resumo(self, obj):
        """Retorna resumo da mensagem"""
        return obj.mensagem[:100] + '...' if len(obj.mensagem) > 100 else obj.mensagem
    get_resumo.short_description = 'Mensagem'


# Inline para mostrar itens dentro da campanha
class ItemCampanhaInline(admin.TabularInline):
    model = ItemCampanha
    extra = 1
    fields = ('nome', 'quantidade_solicitada', 'quantidade_contribuida', 'unidade')
    readonly_fields = ('quantidade_contribuida',)
    verbose_name = "Item Solicitado"
    verbose_name_plural = "📦 Itens Solicitados na Campanha"


# Inline para mostrar posts de atualização dentro da campanha
class PostAtualizacaoInline(admin.StackedInline):
    model = PostAtualizacao
    extra = 0
    fields = ('mensagem', 'imagem', 'data_criacao')
    readonly_fields = ('data_criacao',)
    verbose_name = "Post de Atualização"
    verbose_name_plural = "📢 Posts de Atualização da Campanha"


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizadora', 'get_beneficiaria', 'get_progresso_visual', 'get_total_itens', 'get_itens_completos', 'dias_restantes', 'ativa')
    list_filter = ('data_inicio', 'prazo', 'organizadora__ativo', 'ativa')
    search_fields = ('titulo', 'descricao', 'organizadora__pessoa__nome_completo')
    date_hierarchy = 'data_inicio'
    inlines = [ItemCampanhaInline, PostAtualizacaoInline]
    readonly_fields = ('get_percentual_atingido', 'get_status_campanha', 'dias_restantes')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'subtitulo', 'descricao', 'organizadora', 'beneficiaria')
        }),
        ('📊 Progresso da Campanha', {
            'fields': ('get_status_campanha', 'get_percentual_atingido'),
            'description': 'Progresso calculado automaticamente baseado nos itens abaixo'
        }),
        ('Detalhes', {
            'fields': ('imagem', 'categorias', 'whatsapp', 'localizacao')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'prazo', 'dias_restantes')
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
    )
    
    def get_beneficiaria(self, obj):
        """Retorna o nome da beneficiária"""
        return obj.beneficiaria.nome_exibicao if obj.beneficiaria else '-'
    get_beneficiaria.short_description = '👤 Beneficiária'
    get_beneficiaria.admin_order_field = 'beneficiaria__nome_completo'
    
    def get_total_itens(self, obj):
        """Retorna total de itens na campanha"""
        return obj.total_itens
    get_total_itens.short_description = '📦 Itens'
    
    def get_itens_completos(self, obj):
        """Retorna quantos itens estão completos"""
        return f"{obj.itens_completos}/{obj.total_itens}"
    get_itens_completos.short_description = '✅ Completos'
    
    def get_percentual_atingido(self, obj):
        """Retorna o percentual formatado"""
        return f"{obj.percentual_atingido:.1f}%"
    get_percentual_atingido.short_description = 'Percentual Atingido'
    
    def get_status_campanha(self, obj):
        """Retorna o status da campanha"""
        return obj.status_campanha
    get_status_campanha.short_description = 'Status da Campanha'
    
    def get_progresso_visual(self, obj):
        """Retorna uma barra de progresso visual"""
        percentual = obj.percentual_atingido
        status = obj.status_campanha
        return f"{status} {percentual:.0f}%"
    get_progresso_visual.short_description = '📊 Progresso'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra beneficiaria para mostrar apenas usuários do tipo beneficiária"""
        if db_field.name == "beneficiaria":
            from backend.pessoas.models import TipoUsuario, Pessoa
            try:
                tipo_beneficiaria = TipoUsuario.objects.get(codigo='beneficiaria')
                kwargs["queryset"] = Pessoa.objects.filter(tipo_usuario=tipo_beneficiaria)
            except TipoUsuario.DoesNotExist:
                kwargs["queryset"] = Pessoa.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        # Verificar se o usuário é uma Doadora ou Beneficiária
        from backend.pessoas.models import TipoUsuario
        
        try:
            tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
            tipo_beneficiaria = TipoUsuario.objects.get(codigo='beneficiaria')
            
            tipos_permitidos = [tipo_doadora, tipo_beneficiaria]
            
            if request.user.tipo_usuario not in tipos_permitidos:
                messages.error(request, 'Apenas Doadoras e Beneficiárias podem criar campanhas!')
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