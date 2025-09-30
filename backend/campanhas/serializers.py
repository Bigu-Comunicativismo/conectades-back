from rest_framework import serializers
from .models import Organizadora, Campanha
from backend.pessoas.serializers import PessoaSerializer

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
    titulo = serializers.CharField(
        help_text="Título da campanha"
    )
    descricao = serializers.CharField(
        help_text="Descrição detalhada da campanha"
    )
    data_inicio = serializers.DateField(
        help_text="Data de início da campanha (formato: YYYY-MM-DD)"
    )
    data_fim = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Data de fim da campanha (formato: YYYY-MM-DD)"
    )
    
    class Meta:
        model = Campanha
        fields = [
            'id', 'titulo', 'descricao', 'organizadora', 'organizadora_id',
            'beneficiaria', 'beneficiaria_id', 'data_inicio', 'data_fim'
        ]
        read_only_fields = ['id']
    
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
