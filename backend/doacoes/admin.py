from django.contrib import admin
from django import forms
from .models import TipoServico, Doacao, DoacaoIndependente


class DoacaoForm(forms.ModelForm):
    """Formulário customizado para Doacao que permite item_campanha vazio durante criação"""
    
    class Meta:
        model = Doacao
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se é uma nova doação, tornar item_campanha opcional
        if not self.instance.pk:
            self.fields['item_campanha'].required = False
            self.fields['item_campanha'].queryset = self.fields['item_campanha'].queryset.none()
        else:
            # Se é edição, tornar todos os campos read-only
            for field_name, field in self.fields.items():
                if field_name not in ['status', 'data_entrega', 'observacoes']:
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['disabled'] = True
                    field.help_text = '⚠️ Este campo não pode ser editado após a criação da doação'
    
    def clean(self):
        cleaned_data = super().clean()
        campanha = cleaned_data.get('campanha')
        item_campanha = cleaned_data.get('item_campanha')
        
        # Se item_campanha foi selecionado, verificar se pertence à campanha
        if item_campanha and campanha:
            if item_campanha.campanha != campanha:
                raise forms.ValidationError({
                    'item_campanha': 'O item selecionado não pertence à campanha escolhida.'
                })
        
        return cleaned_data


@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'icone', 'cor', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'descricao')
    list_editable = ('ativo', 'ordem', 'cor')
    ordering = ['ordem', 'nome']

@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    form = DoacaoForm
    list_display = ('get_descricao', 'doador', 'campanha', 'get_item_campanha', 'quantidade', 'unidade', 'status', 'data_doacao')
    list_filter = ('status', 'campanha', 'data_doacao', 'data_entrega')
    search_fields = ('doador__nome_completo', 'campanha__titulo', 'item_campanha__nome')
    date_hierarchy = 'data_doacao'
    readonly_fields = ('data_doacao', 'descricao_completa', 'doador')
    
    def has_change_permission(self, request, obj=None):
        """Permite apenas visualização de doações existentes"""
        if obj:  # Se está editando uma doação existente
            return False  # Não permite edição
        return True  # Permite criação de novas doações
    
    def has_delete_permission(self, request, obj=None):
        """Permite apenas visualização de doações existentes"""
        if obj:  # Se está tentando deletar uma doação existente
            return False  # Não permite exclusão
        return True  # Permite criação de novas doações
    
    def changelist_view(self, request, extra_context=None):
        """Adiciona mensagem informativa sobre edição de doações"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Doações (Somente Visualização)'
        extra_context['subtitle'] = '⚠️ As doações não podem ser editadas após serem criadas para manter a integridade dos dados da campanha'
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('campanha', 'doador')
        }),
        ('Vínculo com Item da Campanha', {
            'fields': ('item_campanha',),
            'description': 'Selecione o item da campanha que está sendo contribuído. Ao confirmar/entregar a doação, o item será atualizado automaticamente.'
        }),
        ('Detalhes da Doação', {
            'fields': ('quantidade', 'unidade', 'imagem', 'descricao_completa')
        }),
        ('Status e Datas', {
            'fields': ('status', 'data_doacao', 'data_entrega')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_descricao(self, obj):
        """Retorna descrição curta da doação"""
        item_nome = obj.item_campanha.nome if obj.item_campanha else "Doação genérica"
        return f"{obj.quantidade} {obj.unidade} de {item_nome}"
    get_descricao.short_description = 'Doação'
    
    def get_item_campanha(self, obj):
        """Retorna o item da campanha"""
        return obj.item_campanha.nome if obj.item_campanha else '-'
    get_item_campanha.short_description = 'Item Contribuído'
    
    def get_form(self, request, obj=None, **kwargs):
        """Retorna o formulário customizado"""
        return super().get_form(request, obj, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra itens baseado na campanha"""
        if db_field.name == "item_campanha":
            from backend.campanhas.models import ItemCampanha
            
            # Tentar pegar campanha_id do POST (quando form é submetido)
            campanha_id = request.POST.get('campanha') if request.method == 'POST' else None
            
            # Se não tem campanha_id no POST, tentar pegar da URL (edição)
            if not campanha_id and request.resolver_match:
                try:
                    object_id = request.resolver_match.kwargs.get('object_id')
                    if object_id:
                        from backend.doacoes.models import Doacao
                        doacao = Doacao.objects.get(id=object_id)
                        if doacao.campanha:
                            campanha_id = doacao.campanha.id
                except (Doacao.DoesNotExist, ValueError):
                    pass
            
            if campanha_id:
                kwargs["queryset"] = ItemCampanha.objects.filter(campanha_id=campanha_id)
            else:
                # Se não tem campanha selecionada, não mostrar nada
                kwargs["queryset"] = ItemCampanha.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Define o doador automaticamente como usuário logado ao criar"""
        if not change:  # Apenas na criação
            obj.doador = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doador', 'campanha', 'item_campanha')
    
    def render_change_form(self, request, context, *args, **kwargs):
        """Adiciona JavaScript inline para filtrar itens por campanha"""
        # Verificar se o campo item_campanha existe no formulário
        if 'item_campanha' in context['adminform'].form.fields:
            context['adminform'].form.fields['item_campanha'].help_text = '''
            <script type="text/javascript">
            (function() {
                function initItemFilter() {
                    const campanhaField = document.getElementById('id_campanha');
                    const itemField = document.getElementById('id_item_campanha');
                    
                    if (!campanhaField || !itemField) {
                        console.log('⚠️ Campos não encontrados, tentando novamente...');
                        setTimeout(initItemFilter, 100);
                        return;
                    }
                    
                    console.log('🔧 Filtro de itens carregado');
                    
                    function updateItems() {
                        const campanhaId = campanhaField.value;
                        console.log('📋 Campanha selecionada:', campanhaId);
                        
                        if (!campanhaId) {
                            itemField.innerHTML = '<option value="">⚠️ Selecione uma campanha primeiro</option>';
                            itemField.disabled = true;
                            return;
                        }
                        
                        itemField.innerHTML = '<option value="">Carregando...</option>';
                        itemField.disabled = true;
                        
                        fetch('/api/campanhas/' + campanhaId + '/itens/')
                            .then(response => response.json())
                            .then(itens => {
                                console.log('✅ Itens recebidos:', itens.length);
                                itemField.innerHTML = '<option value="">---------</option>';
                                
                                if (itens.length > 0) {
                                    itens.forEach(item => {
                                        const percentual = item.percentual_atingido.toFixed(0);
                                        const texto = item.nome + ' (' + item.quantidade_contribuida + '/' + item.quantidade_solicitada + ' ' + item.unidade + ') [' + percentual + '%]';
                                        const option = new Option(texto, item.id);
                                        itemField.add(option);
                                    });
                                    itemField.disabled = false;
                                } else {
                                    itemField.innerHTML = '<option value="">⚠️ Esta campanha não tem itens</option>';
                                }
                            })
                            .catch(error => {
                                console.error('❌ Erro:', error);
                                itemField.innerHTML = '<option value="">Erro ao carregar itens</option>';
                            });
                    }
                    
                    campanhaField.addEventListener('change', function() {
                        console.log('🔄 Campanha alterada');
                        updateItems();
                    });
                    
                    // Carregar itens se já há uma campanha selecionada
                    if (campanhaField.value) {
                        console.log('🔄 Carregando itens da campanha inicial');
                        updateItems();
                    } else {
                        itemField.innerHTML = '<option value="">⚠️ Selecione uma campanha primeiro</option>';
                        itemField.disabled = true;
                    }
                }
                
                // Tentar inicializar imediatamente e também no DOMContentLoaded
                initItemFilter();
                document.addEventListener('DOMContentLoaded', initItemFilter);
            })();
            </script>
            Selecione o item da campanha que você está doando. Ao confirmar a doação, a quantidade do item será atualizada automaticamente.
        '''
        
        return super().render_change_form(request, context, *args, **kwargs)


@admin.register(DoacaoIndependente)
class DoacaoIndependenteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'doadora', 'tipo_servico', 'quantidade_pessoas', 'frequencia_display', 'status', 'data_inicio')
    list_filter = ('tipo_servico', 'status', 'ativa', 'data_inicio', 'data_fim')
    search_fields = ('titulo', 'descricao', 'doadora__nome_completo', 'endereco_detalhado')
    date_hierarchy = 'data_inicio'
    readonly_fields = ('data_criacao', 'data_atualizacao', 'agendamentos_confirmados', 'agendamentos_realizados', 'doadora')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('doadora', 'titulo', 'descricao', 'tipo_servico', 'categorias')
        }),
        ('Detalhes do Serviço', {
            'fields': ('quantidade_pessoas', 'duracao_atendimento', 'frequencia_semanal', 'imagem')
        }),
        ('Período e Horários', {
            'fields': ('data_inicio', 'data_fim', 'dias_semana', 'horario_inicio', 'horario_fim')
        }),
        ('Localização', {
            'fields': ('localizacao', 'endereco_detalhado')
        }),
        ('Contato', {
            'fields': ('whatsapp', 'email_contato')
        }),
        ('Status e Controle', {
            'fields': ('status', 'ativa', 'agendamentos_confirmados', 'agendamentos_realizados')
        }),
        ('Requisitos e Observações', {
            'fields': ('requisitos', 'observacoes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Define a doadora automaticamente como usuário logado ao criar"""
        if not change:  # Apenas na criação
            obj.doadora = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doadora', 'localizacao')
    
    def frequencia_display(self, obj):
        return obj.frequencia_display
    frequencia_display.short_description = 'Frequência'
