from rest_framework import serializers
from .models import Organizadora, Campanha, ItemCampanha
from backend.pessoas.serializers import PessoaSerializer


class ItemCampanhaSerializer(serializers.ModelSerializer):
    """Serializer para itens de campanha"""
    percentual_atingido = serializers.SerializerMethodField(read_only=True)
    
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
    imagem = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Arquivo de imagem da campanha (PNG, JPG, JPEG, GIF, WEBP)"
    )
    
    # Campos calculados
    percentual_atingido = serializers.SerializerMethodField(read_only=True)
    status_campanha = serializers.SerializerMethodField(read_only=True)
    total_itens = serializers.SerializerMethodField(read_only=True)
    itens_completos = serializers.SerializerMethodField(read_only=True)
    dias_restantes = serializers.SerializerMethodField(read_only=True)
    itens = ItemCampanhaSerializer(many=True, read_only=True)
    
    def get_percentual_atingido(self, obj):
        return obj.percentual_atingido
    
    def get_status_campanha(self, obj):
        return obj.status_campanha
    
    def get_total_itens(self, obj):
        return obj.total_itens
    
    def get_itens_completos(self, obj):
        return obj.itens_completos
    
    def get_dias_restantes(self, obj):
        return obj.dias_restantes
    
    class Meta:
        model = Campanha
        fields = [
            'id', 'titulo', 'subtitulo', 'descricao', 
            'organizadora', 'organizadora_id',
            'beneficiaria', 'beneficiaria_id', 'beneficiaria_nome',
            'imagem', 'categorias', 'whatsapp', 'localizacao',
            'data_inicio', 'prazo', 'dias_restantes',
            'percentual_atingido', 'status_campanha', 
            'total_itens', 'itens_completos', 'itens',
            'ativa'
        ]
        read_only_fields = ['id', 'beneficiaria', 'percentual_atingido', 'status_campanha', 'total_itens', 'itens_completos', 'dias_restantes']
    
    def create(self, validated_data):
        organizadora_id = validated_data.pop('organizadora_id')
        beneficiaria_id = validated_data.pop('beneficiaria_id', None)
        
        organizadora = Organizadora.objects.get(id=organizadora_id)
        validated_data['organizadora'] = organizadora
        
        if beneficiaria_id:
            from backend.pessoas.models import Pessoa
            beneficiaria = Pessoa.objects.get(id=beneficiaria_id)
            validated_data['beneficiaria'] = beneficiaria
        
        return Campanha.objects.create(**validated_data)
