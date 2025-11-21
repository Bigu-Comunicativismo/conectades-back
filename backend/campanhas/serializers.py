from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from .models import Organizadora, Campanha, ItemCampanha
from backend.doacoes.models import Doacao
from backend.pessoas.serializers import PessoaSerializer


class DoacaoSerializer(serializers.ModelSerializer):
    """Serializer para doações"""
    doador = PessoaSerializer(read_only=True)
    item_nome = serializers.CharField(source='item_campanha.nome', read_only=True)
    item_unidade = serializers.CharField(source='item_campanha.unidade', read_only=True)
    
    class Meta:
        model = Doacao
        fields = [
            'id', 'doador', 'item_campanha', 'item_nome', 'item_unidade',
            'quantidade', 'unidade', 'observacoes', 'status', 
            'data_doacao', 'data_entrega'
        ]
        read_only_fields = ['id', 'data_doacao', 'data_entrega']
        ref_name = 'CampanhaDoacao'


class ItemCampanhaSerializer(serializers.ModelSerializer):
    """Serializer para itens de campanha"""
    percentual_atingido = serializers.SerializerMethodField(read_only=True)
    
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_percentual_atingido(self, obj):
        return obj.percentual_atingido
    
    class Meta:
        model = ItemCampanha
        fields = [
            'id', 'campanha', 'nome', 'quantidade_solicitada', 
            'quantidade_contribuida', 'unidade', 'percentual_atingido',
            'data_criacao'
        ]
        read_only_fields = ['id', 'quantidade_contribuida', 'data_criacao']

class OrganizadoraSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer(read_only=True)
    pessoa_id = serializers.IntegerField(
        write_only=True,
        help_text="ID da pessoa que será organizadora"
    )
    data_cadastro = serializers.DateTimeField(
        read_only=True,
        help_text="Data de cadastro como organizadora"
    )
    ativo = serializers.BooleanField(
        help_text="Status ativo/inativo da organizadora"
    )
    
    class Meta:
        model = Organizadora
        fields = ['id', 'pessoa', 'pessoa_id', 'data_cadastro', 'ativo']
        read_only_fields = ['id', 'data_cadastro']

class CampanhaSerializer(serializers.ModelSerializer):
    organizadora = OrganizadoraSerializer(read_only=True)
    organizadora_id = serializers.IntegerField(
        write_only=True,
        help_text="ID da organizadora (preenchido automaticamente)"
    )
    beneficiaria = PessoaSerializer(read_only=True)
    beneficiaria_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID da beneficiária (opcional)"
    )
    beneficiaria_nome = serializers.CharField(source='beneficiaria.nome_exibicao', read_only=True, allow_null=True)
    
    titulo = serializers.CharField(
        help_text="Título da campanha"
    )
    descricao = serializers.CharField(
        help_text="Descrição detalhada da campanha"
    )
    # Campo para upload direto de imagem (será convertido para Imagem model)
    imagem_arquivo = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Arquivo de imagem da campanha (PNG, JPG, JPEG, GIF, WEBP)"
    )
    imagem_alt = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        default="Imagem da campanha",
        help_text="Texto alternativo da imagem para acessibilidade"
    )
    # Campo para leitura (retorna a URL da imagem)
    imagem_url = serializers.SerializerMethodField(read_only=True)
    
    # Campo para cadastrar itens junto com a campanha
    itens_cadastro = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Lista de itens para cadastrar junto com a campanha"
    )
    
    # Campos calculados
    percentual_atingido = serializers.SerializerMethodField(read_only=True)
    status_campanha = serializers.SerializerMethodField(read_only=True)
    total_itens = serializers.SerializerMethodField(read_only=True)
    itens_completos = serializers.SerializerMethodField(read_only=True)
    dias_restantes = serializers.SerializerMethodField(read_only=True)
    itens = ItemCampanhaSerializer(many=True, read_only=True)
    itens_campanha = ItemCampanhaSerializer(source='itens', many=True, read_only=True)
    doacoes = serializers.SerializerMethodField(read_only=True)
    
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_percentual_atingido(self, obj):
        return obj.percentual_atingido
    
    @extend_schema_field(OpenApiTypes.STR)
    def get_status_campanha(self, obj):
        return obj.status_campanha
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_total_itens(self, obj):
        return obj.total_itens
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_itens_completos(self, obj):
        return obj.itens_completos
    
    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_dias_restantes(self, obj):
        return obj.dias_restantes
    
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_imagem_url(self, obj):
        if obj.imagem and obj.imagem.src:
            return obj.imagem.src.url
        return None
    
    @extend_schema_field(DoacaoSerializer(many=True))
    def get_doacoes(self, obj):
        """Retorna apenas doações confirmadas pela beneficiária"""
        doacoes_confirmadas = obj.doacoes.filter(status__in=['confirmada', 'entregue'])
        return DoacaoSerializer(doacoes_confirmadas, many=True).data
    
    class Meta:
        model = Campanha
        fields = [
            'id', 'titulo', 'subtitulo', 'descricao', 
            'organizadora', 'organizadora_id',
            'beneficiaria', 'beneficiaria_id', 'beneficiaria_nome',
            'imagem_arquivo', 'imagem_alt', 'imagem_url',
            'categorias', 'whatsapp', 'localizacao',
            'data_inicio', 'prazo', 'dias_restantes',
            'percentual_atingido', 'status_campanha',
            'total_itens', 'itens_completos', 'itens', 'itens_campanha', 'itens_cadastro', 'doacoes',
            'ativa'
        ]
        read_only_fields = ['id', 'beneficiaria', 'percentual_atingido', 'status_campanha', 'total_itens', 'itens_completos', 'dias_restantes', 'doacoes', 'imagem_url', 'ativa']
    
    def create(self, validated_data):
        from .models import Imagem
        import os
        from django.core.files import File
        from django.conf import settings
        
        organizadora_id = validated_data.pop('organizadora_id')
        beneficiaria_id = validated_data.pop('beneficiaria_id', None)
        
        # Extrair campos many-to-many (não podem ser criados junto com o objeto)
        categorias = validated_data.pop('categorias', [])
        
        # Extrair lista de itens (se fornecida)
        itens_cadastro = validated_data.pop('itens_cadastro', [])
        
        # Processar imagem (se fornecida)
        imagem_arquivo = validated_data.pop('imagem_arquivo', None)
        imagem_alt = validated_data.pop('imagem_alt', 'Imagem da campanha')
        
        organizadora = Organizadora.objects.get(id=organizadora_id)
        validated_data['organizadora'] = organizadora
        
        if beneficiaria_id:
            from backend.pessoas.models import Pessoa
            beneficiaria = Pessoa.objects.get(id=beneficiaria_id)
            validated_data['beneficiaria'] = beneficiaria
        
        # Criar objeto Imagem se arquivo foi fornecido, senão usar imagem padrão
        if imagem_arquivo:
            imagem = Imagem.objects.create(
                src=imagem_arquivo,
                alt=imagem_alt
            )
            validated_data['imagem'] = imagem
        else:
            # Aplicar imagem padrão (PNG)
            default_image_path = settings.BASE_DIR / 'static' / 'campanha_default.png'
            
            if default_image_path.exists():
                with open(str(default_image_path), 'rb') as f:
                    default_file = File(f, name='campanha_default.png')
                    imagem = Imagem.objects.create(
                        src=default_file,
                        alt='Imagem padrão da campanha'
                    )
                    validated_data['imagem'] = imagem
            else:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Imagem padrão não encontrada em static/campanha_default.png")
        
        # Criar a campanha
        campanha = Campanha.objects.create(**validated_data)
        
        # Adicionar categorias (many-to-many)
        if categorias:
            campanha.categorias.set(categorias)
        
        # Cadastrar itens (se fornecidos)
        if itens_cadastro:
            for item_data in itens_cadastro:
                ItemCampanha.objects.create(
                    campanha=campanha,
                    nome=item_data.get('nome'),
                    quantidade_solicitada=item_data.get('quantidade_solicitada'),
                    unidade=item_data.get('unidade', 'unidade')
                )
        
        return campanha
