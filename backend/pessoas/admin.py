from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Pessoa, TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse, CodigoVerificacao


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'descricao')
    list_editable = ('ativo', 'ordem')
    ordering = ('ordem', 'nome')


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'descricao')
    list_editable = ('ativo', 'ordem')
    ordering = ('ordem', 'nome')


@admin.register(CategoriaInteresse)
class CategoriaInteresseAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'descricao')
    list_editable = ('ativo', 'ordem')
    ordering = ('ordem', 'nome')


@admin.register(LocalizacaoInteresse)
class LocalizacaoInteresseAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'cidade', 'estado', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('tipo', 'estado', 'ativo', 'data_criacao')
    search_fields = ('nome', 'cidade', 'codigo')
    list_editable = ('ativo', 'ordem')
    ordering = ('estado', 'cidade', 'ordem', 'nome')

@admin.register(Pessoa)
class PessoaAdmin(UserAdmin):
    list_display = ('username', 'nome_completo', 'nome_social', 'email', 'get_tipo_usuario', 'get_genero', 'cidade', 'is_active')
    list_filter = ('tipo_usuario', 'genero', 'is_active', 'is_staff', 'cidade', 'date_joined')
    search_fields = ('username', 'nome_completo', 'nome_social', 'email', 'cpf', 'telefone')
    list_per_page = 25
    
    # Campos de exibição personalizados
    readonly_fields = ('date_joined', 'last_login', 'categorias_interesse_display')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais Básicas', {
            'fields': ('nome_completo', 'nome_social', 'cpf', 'telefone', 'email', 'genero')
        }),
        ('Tipo de Usuário e Localização', {
            'fields': ('tipo_usuario', 'cidade', 'bairro')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Datas importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Perfil Público', {
            'fields': ('mini_bio', 'avatar', 'categorias_interesse_display')
        }),
        ('Interesses', {
            'fields': ('categorias_interesse', 'localizacoes_interesse'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Pessoais Básicas', {
            'fields': ('nome_completo', 'nome_social', 'cpf', 'telefone', 'email', 'genero')
        }),
        ('Tipo de Usuário e Localização', {
            'fields': ('tipo_usuario', 'cidade', 'bairro')
        }),
        ('Perfil Público', {
            'fields': ('mini_bio', 'avatar')
        }),
        ('Interesses', {
            'fields': ('categorias_interesse', 'localizacoes_interesse'),
            'classes': ('collapse',)
        }),
    )
    
    def get_tipo_usuario(self, obj):
        """Exibe o tipo de usuário"""
        return obj.tipo_usuario.nome if obj.tipo_usuario else "-"
    get_tipo_usuario.short_description = "Tipo de Usuário"
    get_tipo_usuario.admin_order_field = 'tipo_usuario__nome'
    
    def get_genero(self, obj):
        """Exibe o gênero"""
        return obj.genero.nome if obj.genero else "-"
    get_genero.short_description = "Gênero"
    get_genero.admin_order_field = 'genero__nome'
    
    def categorias_interesse_display(self, obj):
        """Exibe as categorias de interesse de forma legível"""
        if obj.categorias_interesse.exists():
            categorias = obj.get_categorias_interesse_display()
            if isinstance(categorias, list):
                return ', '.join(categorias)
            return categorias
        return "Nenhuma categoria selecionada"
    categorias_interesse_display.short_description = "Categorias de Interesse"
    
    def get_queryset(self, request):
        """Otimiza a consulta para evitar N+1 queries"""
        return super().get_queryset(request).select_related('tipo_usuario', 'genero').prefetch_related('categorias_interesse', 'localizacoes_interesse')


@admin.register(CodigoVerificacao)
class CodigoVerificacaoAdmin(admin.ModelAdmin):
    list_display = ('email', 'codigo', 'tipo', 'usado', 'tentativas', 'data_criacao', 'data_expiracao', 'status_validade')
    list_filter = ('tipo', 'usado', 'data_criacao')
    search_fields = ('email', 'codigo')
    readonly_fields = ('codigo', 'data_criacao', 'data_expiracao', 'status_validade')
    date_hierarchy = 'data_criacao'
    ordering = ('-data_criacao',)
    
    def status_validade(self, obj):
        """Mostra status visual do código"""
        valido, mensagem = obj.esta_valido()
        if valido:
            return format_html('<span style="color: green;">✓ Válido</span>')
        return format_html(f'<span style="color: red;">✗ {mensagem}</span>')
    status_validade.short_description = "Status"
    
    def has_add_permission(self, request):
        """Códigos são gerados automaticamente, não manualmente"""
        return False
    
    actions = ['marcar_como_usado', 'limpar_expirados']
    
    def marcar_como_usado(self, request, queryset):
        """Marca códigos selecionados como usados"""
        count = queryset.update(usado=True)
        self.message_user(request, f'{count} código(s) marcado(s) como usado(s)')
    marcar_como_usado.short_description = "Marcar como usado"
    
    def limpar_expirados(self, request, queryset):
        """Remove códigos expirados"""
        from django.utils import timezone
        from datetime import timedelta
        
        limite = timezone.now() - timedelta(hours=24)
        count = CodigoVerificacao.objects.filter(data_criacao__lt=limite).count()
        CodigoVerificacao.objects.filter(data_criacao__lt=limite).delete()
        
        self.message_user(request, f'{count} código(s) expirado(s) removido(s)')
    limpar_expirados.short_description = "Limpar códigos expirados (>24h)"