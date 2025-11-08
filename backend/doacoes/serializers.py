from rest_framework import serializers
from .models import TipoServico, Doacao, DoacaoIndependente


class AtualizarStatusDoacaoSerializer(serializers.Serializer):
    """Serializer para atualizar status de uma doação"""
    status = serializers.ChoiceField(
        choices=['pendente', 'confirmada', 'entregue', 'cancelada'],
        required=False,
        help_text="Novo status da doação"
    )
    data_entrega = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Data de entrega da doação (apenas beneficiária pode alterar)"
    )
    observacoes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Observações sobre a doação"
    )


class TipoServicoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de serviço"""
    
    class Meta:
        model = TipoServico
        fields = [
            'id', 'nome', 'codigo', 'descricao', 'icone', 'cor', 
            'ativo', 'ordem', 'data_criacao'
        ]
        read_only_fields = ['id', 'codigo', 'data_criacao']


class DoacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para doações.
    Uma doação vincula um doador a uma campanha, contribuindo para um item específico.
    """
    doador_id = serializers.IntegerField(write_only=True, help_text="ID do doador (preenchido automaticamente)")
    campanha_id = serializers.IntegerField(write_only=True, help_text="ID da campanha")
    item_campanha_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID do item da campanha (opcional)")
    
    doador_nome = serializers.CharField(source='doador.nome_exibicao', read_only=True)
    campanha_titulo = serializers.CharField(source='campanha.titulo', read_only=True)
    item_campanha_nome = serializers.CharField(source='item_campanha.nome', read_only=True, allow_null=True)
    item_campanha_unidade = serializers.CharField(source='item_campanha.unidade', read_only=True, allow_null=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    descricao_completa = serializers.SerializerMethodField(read_only=True)
    
    def get_status_display(self, obj):
        return obj.status_display
    
    def get_descricao_completa(self, obj):
        return obj.descricao_completa

    class Meta:
        model = Doacao
        fields = [
            'id', 'campanha', 'campanha_id', 'campanha_titulo',
            'doador', 'doador_id', 'doador_nome',
            'item_campanha', 'item_campanha_id', 'item_campanha_nome', 'item_campanha_unidade',
            'descricao_completa',
            'quantidade', 'unidade',
            'imagem', 'data_doacao', 'data_entrega',
            'status', 'status_display', 'observacoes'
        ]
        read_only_fields = ['id', 'campanha', 'doador', 'item_campanha', 'data_doacao']

    def create(self, validated_data):
        doador_id = validated_data.pop('doador_id')
        campanha_id = validated_data.pop('campanha_id')
        item_campanha_id = validated_data.pop('item_campanha_id', None)

        validated_data['doador_id'] = doador_id
        validated_data['campanha_id'] = campanha_id
        
        if item_campanha_id:
            validated_data['item_campanha_id'] = item_campanha_id

        return Doacao.objects.create(**validated_data)


class DoacaoIndependenteSerializer(serializers.ModelSerializer):
    """Serializer para doações independentes"""
    doadora_id = serializers.IntegerField(write_only=True, help_text="ID da doadora (preenchido automaticamente)")
    categorias = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de categorias de interesse"
    )
    tipo_servico_nome = serializers.CharField(source='tipo_servico.nome', read_only=True)
    tipo_servico_icone = serializers.CharField(source='tipo_servico.icone', read_only=True)
    tipo_servico_cor = serializers.CharField(source='tipo_servico.cor', read_only=True)
    doadora_nome = serializers.CharField(source='doadora.nome_exibicao', read_only=True)
    localizacao_nome = serializers.CharField(source='localizacao.nome', read_only=True)
    dias_semana_display = serializers.SerializerMethodField(read_only=True)
    horario_display = serializers.SerializerMethodField(read_only=True)
    frequencia_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    capacidade_total_semanal = serializers.SerializerMethodField(read_only=True)
    
    def get_dias_semana_display(self, obj):
        return obj.dias_semana_display
    
    def get_horario_display(self, obj):
        return obj.horario_display
    
    def get_frequencia_display(self, obj):
        return obj.frequencia_display
    
    def get_status_display(self, obj):
        return obj.status_display
    
    def get_capacidade_total_semanal(self, obj):
        return obj.capacidade_total_semanal

    class Meta:
        model = DoacaoIndependente
        fields = [
            'id', 'doadora', 'doadora_id', 'doadora_nome',
            'titulo', 'descricao', 'tipo_servico', 'tipo_servico_nome', 
            'tipo_servico_icone', 'tipo_servico_cor',
            'quantidade_pessoas', 'duracao_atendimento', 'frequencia_semanal',
            'frequencia_display', 'data_inicio', 'data_fim',
            'dias_semana', 'dias_semana_display', 'horario_inicio', 'horario_fim',
            'horario_display', 'localizacao', 'localizacao_nome', 'endereco_detalhado',
            'whatsapp', 'email_contato', 'categorias', 'imagem',
            'status', 'status_display', 'ativa', 'requisitos', 'observacoes',
            'agendamentos_confirmados', 'agendamentos_realizados',
            'capacidade_total_semanal', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = [
            'id', 'doadora', 'agendamentos_confirmados', 'agendamentos_realizados',
            'data_criacao', 'data_atualizacao'
        ]

    def create(self, validated_data):
        doadora_id = validated_data.pop('doadora_id')
        categorias = validated_data.pop('categorias', None)
        doacao = DoacaoIndependente.objects.create(
            doadora_id=doadora_id,
            **validated_data
        )
        if categorias is not None:
            doacao.categorias.set(categorias)
        return doacao


class DoacaoIndependenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de doações independentes"""
    tipo_servico_nome = serializers.CharField(source='tipo_servico.nome', read_only=True)
    tipo_servico_icone = serializers.CharField(source='tipo_servico.icone', read_only=True)
    tipo_servico_cor = serializers.CharField(source='tipo_servico.cor', read_only=True)
    doadora_nome = serializers.CharField(source='doadora.nome_exibicao', read_only=True)
    localizacao_nome = serializers.CharField(source='localizacao.nome', read_only=True)
    dias_semana_display = serializers.SerializerMethodField(read_only=True)
    horario_display = serializers.SerializerMethodField(read_only=True)
    frequencia_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    
    def get_dias_semana_display(self, obj):
        return obj.dias_semana_display
    
    def get_horario_display(self, obj):
        return obj.horario_display
    
    def get_frequencia_display(self, obj):
        return obj.frequencia_display
    
    def get_status_display(self, obj):
        return obj.status_display

    class Meta:
        model = DoacaoIndependente
        fields = [
            'id', 'titulo', 'descricao', 'tipo_servico_nome', 'tipo_servico_icone', 'tipo_servico_cor',
            'doadora_nome', 'quantidade_pessoas', 'frequencia_display', 'horario_display',
            'dias_semana_display', 'localizacao_nome', 'status_display', 'ativa',
            'data_inicio', 'data_fim', 'whatsapp'
        ]







