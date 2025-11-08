from rest_framework import serializers
from .models import TipoServico, Doacao, DoacaoIndependente
from backend.campanhas.models import Imagem
from backend.pessoas.models import LocalizacaoInteresse, Pessoa


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
            'id', 'nome', 'descricao', 'icone', 'cor', 
            'ativo', 'ordem', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao']


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
    """Serializer para doações independentes (leitura/atualização)"""
    doadora_id = serializers.IntegerField(write_only=True, required=False, help_text="ID da doadora (preenchido automaticamente)")
    categorias = serializers.PrimaryKeyRelatedField(queryset=TipoServico.objects.all(), many=True, required=False)
    doadora_nome = serializers.CharField(source='doadora.nome_exibicao', read_only=True)
    localizacao_nome = serializers.CharField(source='localizacao.nome', read_only=True)
    imagem_url = serializers.SerializerMethodField(read_only=True)
    imagem_alt = serializers.CharField(source='imagem.alt', read_only=True, allow_null=True)
    categorias_detalhes = TipoServicoSerializer(source='categorias', many=True, read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    
    def get_imagem_url(self, obj):
        if obj.imagem and obj.imagem.src:
            return obj.imagem.src.url
        return None
    
    def get_status_display(self, obj):
        return obj.status_display

    class Meta:
        model = DoacaoIndependente
        fields = [
            'id', 'doadora', 'doadora_id', 'doadora_nome',
            'titulo', 'subtitulo', 'descricao',
            'data_inicio', 'data_fim',
            'localizacao', 'localizacao_nome',
            'categorias', 'categorias_detalhes', 'imagem', 'imagem_url', 'imagem_alt',
            'whatsapp',
            'status', 'status_display', 'ativa',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = [
            'id', 'doadora',
            'status_display', 'imagem_url',
            'data_criacao', 'data_atualizacao'
        ]
        extra_kwargs = {
            'categorias': {'required': False},
            'subtitulo': {'required': False, 'allow_null': True, 'allow_blank': True},
            'localizacao': {'required': False, 'allow_null': True},
            'imagem': {'required': False, 'allow_null': True},
            'data_fim': {'required': False, 'allow_null': True},
            'whatsapp': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def create(self, validated_data):
        doadora_id = validated_data.pop('doadora_id', None)
        categorias = validated_data.pop('categorias', None)
        ativa = validated_data.pop('ativa', None)
        status = validated_data.pop('status', None)

        if doadora_id is None:
            doadora = self.context.get('doadora')
            if not doadora:
                raise serializers.ValidationError({'doadora_id': 'Informe a doadora responsável.'})
            doadora_id = doadora.id

        if ativa is None:
            ativa = True
        if not status:
            status = 'ativa'
        elif status not in dict(DoacaoIndependente.STATUS_CHOICES):
            raise serializers.ValidationError({'status': 'Valor inválido.'})

        doacao = DoacaoIndependente.objects.create(
            doadora_id=doadora_id,
            ativa=ativa,
            status=status,
            **validated_data
        )
        if categorias is not None:
            doacao.categorias.set(categorias)
        return doacao


class DoacaoIndependenteCreateSerializer(serializers.Serializer):
    """Serializer simplificado para criação de doações independentes"""
    titulo = serializers.CharField()
    subtitulo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    descricao = serializers.CharField()
    imagem = serializers.ImageField(required=False, allow_null=True)
    imagem_alt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    whatsapp = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    data_inicio = serializers.DateTimeField()
    data_fim = serializers.DateTimeField(required=False, allow_null=True)
    localizacao = serializers.PrimaryKeyRelatedField(
        queryset=LocalizacaoInteresse.objects.all(),
        required=False,
        allow_null=True
    )
    categorias = serializers.PrimaryKeyRelatedField(
        queryset=TipoServico.objects.all(),
        many=True,
        required=False,
        allow_empty=True
    )
    doadora_id = serializers.IntegerField(required=False)

    def create(self, validated_data):
        doadora = self.context['doadora']
        imagem_arquivo = validated_data.pop('imagem', None)
        imagem_alt = validated_data.pop('imagem_alt', None)
        localizacao = validated_data.pop('localizacao', None)
        categorias = validated_data.pop('categorias', [])
        doadora_id = validated_data.pop('doadora_id', None)

        selected_doadora = doadora
        if doadora_id is not None and doadora_id != doadora.id:
            if not doadora.is_staff:
                raise serializers.ValidationError({'doadora_id': 'Você não pode criar doações para outra pessoa.'})
            try:
                selected_doadora = Pessoa.objects.get(id=doadora_id)
            except Pessoa.DoesNotExist:
                raise serializers.ValidationError({'doadora_id': 'Pessoa informada não encontrada.'})

        imagem_obj = None
        if imagem_arquivo:
            imagem_obj = Imagem.objects.create(
                src=imagem_arquivo,
                alt=imagem_alt or f"Imagem da doação independente {validated_data['titulo']}"
            )

        doacao = DoacaoIndependente.objects.create(
            doadora=selected_doadora,
            titulo=validated_data['titulo'],
            subtitulo=validated_data.get('subtitulo'),
            descricao=validated_data['descricao'],
            imagem=imagem_obj,
            data_inicio=validated_data['data_inicio'],
            data_fim=validated_data.get('data_fim'),
            localizacao=localizacao,
            whatsapp=validated_data.get('whatsapp'),
            status='ativa',
            ativa=True
        )

        if categorias:
            doacao.categorias.set(categorias)

        return doacao


class DoacaoIndependenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de doações independentes"""
    categorias = serializers.PrimaryKeyRelatedField(source='categorias', many=True, read_only=True)
    doadora_nome = serializers.CharField(source='doadora.nome_exibicao', read_only=True)
    localizacao_nome = serializers.CharField(source='localizacao.nome', read_only=True)
    imagem_url = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    categorias_detalhes = TipoServicoSerializer(source='categorias', many=True, read_only=True)

    def get_status_display(self, obj):
        return obj.status_display

    def get_imagem_url(self, obj):
        if obj.imagem and obj.imagem.src:
            return obj.imagem.src.url
        return None

    class Meta:
        model = DoacaoIndependente
        fields = [
            'id', 'titulo', 'subtitulo', 'descricao',
            'categorias', 'categorias_detalhes',
            'doadora_nome', 'localizacao_nome',
            'status_display', 'ativa',
            'data_inicio', 'data_fim',
            'imagem_url', 'whatsapp'
        ]







