from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Pessoa

class PessoaSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        help_text="Senha do usuário (obrigatório para criação)"
    )
    tipo = serializers.ChoiceField(
        choices=[('beneficiaria', 'Beneficiária'), ('doadora', 'Doadora')],
        help_text="Tipo de pessoa: beneficiaria ou doadora"
    )
    nome = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nome completo da pessoa"
    )
    cpf = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="CPF da pessoa (formato: 000.000.000-00)"
    )
    telefone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Número de telefone"
    )
    cidade = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Cidade onde mora"
    )
    bairro = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Bairro onde mora"
    )
    endereco = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Endereço completo"
    )
    nome_alias = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nome que será exibido publicamente"
    )
    mini_bio = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Breve descrição sobre a pessoa"
    )
    foto = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Foto de perfil"
    )
    
    class Meta:
        model = Pessoa
        fields = [
            'id', 'username', 'email', 'password', 'tipo', 'nome', 'cpf', 
            'telefone', 'cidade', 'bairro', 'endereco', 'nome_alias', 
            'mini_bio', 'foto', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        pessoa = Pessoa.objects.create_user(password=password, **validated_data)
        return pessoa
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class PessoaLoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Nome de usuário")
    password = serializers.CharField(help_text="Senha do usuário")
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas')
            if not user.is_active:
                raise serializers.ValidationError('Usuário inativo')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Username e password são obrigatórios')
