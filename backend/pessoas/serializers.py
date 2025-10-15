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


# ========== NOVOS SERIALIZERS PARA AUTENTICAÇÃO COM CÓDIGO ===========

class SolicitarCodigoSerializer(serializers.Serializer):
    """Serializer para solicitar código de verificação"""
    email = serializers.EmailField(help_text="Email para receber o código")
    tipo = serializers.ChoiceField(
        choices=['cadastro', 'login', 'recuperacao'],
        default='cadastro',
        help_text="Tipo do código: cadastro, login ou recuperacao"
    )


class VerificarCodigoSerializer(serializers.Serializer):
    """Serializer para verificar código de verificação"""
    email = serializers.EmailField(help_text="Email que recebeu o código")
    codigo = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="Código de 6 dígitos recebido por email"
    )
    tipo = serializers.ChoiceField(
        choices=['cadastro', 'login', 'recuperacao'],
        default='cadastro',
        help_text="Tipo do código"
    )


class RegistroComCodigoSerializer(serializers.Serializer):
    """
    Serializer para registro de usuário (primeira etapa - sem código)
    O código será enviado por email após validação inicial
    """
    # Dados obrigatórios para cadastro
    email = serializers.EmailField(help_text="Email válido (receberá código de verificação)")
    username = serializers.CharField(
        min_length=3,
        max_length=150,
        help_text="Nome de usuário único (mínimo 3 caracteres)"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Senha forte (mínimo 8 caracteres)"
    )
    nome_completo = serializers.CharField(help_text="Nome completo")
    cpf = serializers.CharField(help_text="CPF (formato: 000.000.000-00)")
    telefone = serializers.CharField(help_text="Telefone com DDD")
    
    tipo_usuario = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.all(),
        help_text="ID do tipo de usuário (1=Beneficiária, 2=Doadora)"
    )
    genero = serializers.PrimaryKeyRelatedField(
        queryset=Genero.objects.all(),
        help_text="ID do gênero"
    )
    
    cidade = serializers.CharField(help_text="Cidade onde mora")
    bairro = serializers.CharField(help_text="Bairro onde mora")
    nome_social = serializers.CharField(help_text="Nome social (como prefere ser chamada)")
    mini_bio = serializers.CharField(help_text="Mini biografia")
    
    # Campos opcionais
    avatar = serializers.ImageField(required=False, help_text="Foto de perfil")
    categorias_interesse = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaInteresse.objects.all(),
        required=False,
        help_text="IDs das categorias de interesse"
    )
    localizacoes_interesse = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalizacaoInteresse.objects.all(),
        required=False,
        help_text="IDs das localizações de interesse"
    )
    
    def validate_email(self, value):
        """Verifica se email já está em uso"""
        if Pessoa.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está cadastrado")
        return value
    
    def validate_username(self, value):
        """Verifica se username já está em uso"""
        if Pessoa.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso")
        return value
    
    def validate_cpf(self, value):
        """Valida formato do CPF"""
        cpf_limpo = value.replace('.', '').replace('-', '')
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise serializers.ValidationError("CPF inválido")
        if Pessoa.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado")
        return value


class ConfirmarRegistroSerializer(serializers.Serializer):
    """
    Serializer para confirmar registro com código de verificação
    """
    email = serializers.EmailField(help_text="Email que recebeu o código")
    codigo = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="Código de 6 dígitos recebido por email"
    )


class LoginComCodigoSerializer(serializers.Serializer):
    """
    Serializer para login com email e senha
    Retorna JWT tokens após verificação
    """
    email = serializers.EmailField(help_text="Email cadastrado")
    password = serializers.CharField(
        write_only=True,
        help_text="Senha da conta"
    )
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            pessoa = Pessoa.objects.get(email=email)
            user = authenticate(username=pessoa.username, password=password)
            
            if not user:
                raise serializers.ValidationError("Email ou senha inválidos")
            if not user.is_active:
                raise serializers.ValidationError("Conta inativa. Entre em contato com o suporte")
            
            attrs['user'] = user
            return attrs
        except Pessoa.DoesNotExist:
            raise serializers.ValidationError("Email ou senha inválidos")
