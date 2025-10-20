from django.contrib import admin
from .models import TipoServico, Doacao, DoacaoIndependente

@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'icone', 'cor', 'ativo', 'ordem', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'codigo', 'descricao')
    list_editable = ('ativo', 'ordem', 'cor')
    ordering = ['ordem', 'nome']

@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('get_descricao', 'doador', 'campanha', 'get_item_campanha', 'quantidade', 'unidade', 'status', 'data_doacao')
    list_filter = ('status', 'campanha', 'data_doacao', 'data_entrega')
    search_fields = ('doador__nome_completo', 'campanha__titulo', 'item_campanha__nome')
    date_hierarchy = 'data_doacao'
    readonly_fields = ('data_doacao', 'descricao_completa', 'doador')
    
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
        """Customiza o form para filtrar itens baseado na campanha"""
        form = super().get_form(request, obj, **kwargs)
        
        # Se está editando uma doação existente
        if obj and obj.campanha:
            from backend.campanhas.models import ItemCampanha
            form.base_fields['item_campanha'].queryset = ItemCampanha.objects.filter(
                campanha=obj.campanha
            )
        # Se está criando (obj é None), não mostrar nenhum item inicialmente
        # O JavaScript vai popular depois que selecionar a campanha
        elif not obj:
            from backend.campanhas.models import ItemCampanha
            form.base_fields['item_campanha'].queryset = ItemCampanha.objects.none()
            form.base_fields['item_campanha'].required = False
            form.base_fields['item_campanha'].help_text = '⚠️ Primeiro selecione uma campanha acima'
        
        return form
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra itens baseado na campanha - complementa get_form"""
        if db_field.name == "item_campanha":
            # Tentar pegar campanha_id do POST (quando form é submetido)
            campanha_id = request.POST.get('campanha') if request.method == 'POST' else None
            
            if campanha_id:
                from backend.campanhas.models import ItemCampanha
                kwargs["queryset"] = ItemCampanha.objects.filter(campanha_id=campanha_id)
            elif 'queryset' not in kwargs:
                # Se não foi definido no get_form, não mostrar nada
                from backend.campanhas.models import ItemCampanha
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
