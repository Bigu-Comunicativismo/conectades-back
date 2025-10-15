from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Pessoa, TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse


class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['id', 'codigo', 'nome', 'descricao', 'ativo', 'ordem', 'data_criacao']


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['id', 'codigo', 'nome', 'descricao', 'ativo', 'ordem', 'data_criacao']


class CategoriaInteresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaInteresse
        fields = ['id', 'codigo', 'nome', 'descricao', 'ativo', 'ordem', 'data_criacao']


class LocalizacaoInteresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalizacaoInteresse
        fields = ['id', 'tipo', 'nome', 'codigo', 'cidade', 'estado', 'ativo', 'ordem', 'data_criacao']

class PessoaSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        help_text="Senha do usuário (obrigatório para criação)"
    )
    
    # Campos obrigatórios
    nome_completo = serializers.CharField(
        help_text="Nome completo da pessoa"
    )
    cpf = serializers.CharField(
        help_text="CPF da pessoa (formato: 000.000.000-00)"
    )
    telefone = serializers.CharField(
        help_text="Número de telefone com DDD"
    )
    email = serializers.EmailField(
        help_text="E-mail para contato"
    )
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.all(),
        help_text="Tipo de usuário: beneficiária, doadora ou organizadora"
    )
    genero = serializers.PrimaryKeyRelatedField(
        queryset=Genero.objects.all(),
        help_text="Gênero/identidade de gênero"
    )
    cidade = serializers.CharField(
        help_text="Cidade onde mora"
    )
    bairro = serializers.CharField(
        help_text="Bairro onde mora"
    )
    
    # Campos obrigatórios adicionais
    nome_social = serializers.CharField(
        help_text="Nome que você gostaria de ser chamada"
    )
    mini_bio = serializers.CharField(
        help_text="Breve descrição sobre você"
    )
    avatar = serializers.ImageField(
        help_text="Foto de perfil"
    )
    categorias_interesse = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaInteresse.objects.all(),
        help_text="Lista de categorias de interesse"
    )
    localizacoes_interesse = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalizacaoInteresse.objects.all(),
        help_text="Lista de localizações de interesse"
    )
    
    # Campos de exibição
    nome_exibicao = serializers.ReadOnlyField(
        help_text="Nome que será exibido publicamente"
    )
    categorias_interesse_display = serializers.SerializerMethodField(
        help_text="Categorias de interesse formatadas"
    )
    
    class Meta:
        model = Pessoa
        fields = [
            'id', 'username', 'password', 'nome_completo', 'cpf', 'telefone', 
            'email', 'tipo_usuario', 'genero', 'cidade', 'bairro', 
            'nome_social', 'mini_bio', 'avatar', 'categorias_interesse', 
            'localizacoes_interesse', 'nome_exibicao', 'categorias_interesse_display',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'nome_exibicao', 'categorias_interesse_display']
    
    def get_categorias_interesse_display(self, obj):
        """Retorna as categorias de interesse formatadas"""
        return obj.get_categorias_interesse_display()
    
    def validate_cpf(self, value):
        """Validação básica do CPF"""
        if value:
            # Remove pontos e hífens
            cpf_limpo = value.replace('.', '').replace('-', '')
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                raise serializers.ValidationError("CPF deve ter 11 dígitos")
        return value
    
    def validate_telefone(self, value):
        """Validação básica do telefone"""
        if value:
            # Remove caracteres especiais
            telefone_limpo = value.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            if len(telefone_limpo) < 10 or not telefone_limpo.isdigit():
                raise serializers.ValidationError("Telefone deve ter pelo menos 10 dígitos")
        return value
    
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
