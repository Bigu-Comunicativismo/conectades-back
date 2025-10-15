from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.cache import cache
from django.db import transaction
from .models import Pessoa, CodigoVerificacao
from .serializers import (
    PessoaSerializer,
    RegistroComCodigoSerializer,
    ConfirmarRegistroSerializer,
    LoginComCodigoSerializer,
    SolicitarCodigoSerializer,
    VerificarCodigoSerializer,
    TipoUsuarioSerializer,
    GeneroSerializer,
    CategoriaInteresseSerializer,
    LocalizacaoInteresseSerializer,
)
from .email_service import enviar_codigo_verificacao, verificar_codigo


# ============== ENDPOINTS PÚBLICOS (SEM AUTENTICAÇÃO) ==============

@extend_schema(
    operation_id='listar_opcoes_cadastro',
    summary='Listar Opções de Cadastro',
    description='Retorna todas as opções disponíveis para cadastro: tipos de usuário, gêneros, categorias e localizações',
    tags=['Cadastro - Público'],
    responses={200: OpenApiResponse(description="Opções disponíveis")}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_opcoes_cadastro(request):
    """
    Lista todas as opções disponíveis para o cadastro
    ENDPOINT PÚBLICO - não requer autenticação
    """
    from .models import TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse
    
    # Tentar buscar do cache primeiro
    cache_key = 'opcoes_cadastro_completo'
    dados_cache = cache.get(cache_key)
    
    if dados_cache:
        return Response(dados_cache)
    
    # Se não estiver em cache, buscar do banco
    dados = {
        'tipos_usuario': TipoUsuarioSerializer(
            TipoUsuario.objects.filter(ativo=True),
            many=True
        ).data,
        'generos': GeneroSerializer(
            Genero.objects.filter(ativo=True),
            many=True
        ).data,
        'categorias_interesse': CategoriaInteresseSerializer(
            CategoriaInteresse.objects.filter(ativo=True),
            many=True
        ).data,
        'localizacoes_interesse': LocalizacaoInteresseSerializer(
            LocalizacaoInteresse.objects.filter(ativo=True),
            many=True
        ).data,
    }
    
    # Armazenar em cache por 1 hora
    cache.set(cache_key, dados, 60 * 60)
    
    return Response(dados)


@extend_schema(
    operation_id='iniciar_registro',
    summary='1️⃣ Iniciar Registro',
    description='''
    ETAPA 1 de 2: Envia os dados de cadastro e recebe código por email.
    
    **Fluxo:**
    1. Preencha todos os campos obrigatórios
    2. Sistema valida os dados
    3. Código de 6 dígitos é enviado para o email
    4. Use o código na próxima etapa (confirmar_registro)
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Cadastro - Público'],
    request=RegistroComCodigoSerializer,
    responses={
        200: OpenApiResponse(description="Código enviado para o email"),
        400: OpenApiResponse(description="Erro de validação")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_registro(request):
    """
    ETAPA 1: Valida dados e envia código de verificação por email
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = RegistroComCodigoSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Armazenar dados temporariamente em cache (expira em 15 minutos)
    cache_key = f'registro_pendente_{email}'
    cache.set(cache_key, serializer.validated_data, 60 * 15)
    
    # Enviar código de verificação
    sucesso, mensagem, codigo_obj = enviar_codigo_verificacao(email, tipo='cadastro')
    
    if not sucesso:
        return Response(
            {'error': mensagem},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'Código de verificação enviado para seu email',
        'email': email,
        'validade': '10 minutos',
        'proximo_passo': 'Use o endpoint /api/auth/confirmar-registro/ com o código recebido'
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='confirmar_registro',
    summary='2️⃣ Confirmar Registro',
    description='''
    ETAPA 2 de 2: Confirma o código e cria a conta.
    
    **Fluxo:**
    1. Digite o código de 6 dígitos recebido no email
    2. Sistema verifica o código
    3. Conta é criada e ativada
    4. Retorna tokens JWT para login automático
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Cadastro - Público'],
    request=ConfirmarRegistroSerializer,
    responses={
        201: OpenApiResponse(description="Conta criada com sucesso"),
        400: OpenApiResponse(description="Código inválido ou expirado")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def confirmar_registro(request):
    """
    ETAPA 2: Verifica código e cria a conta
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = ConfirmarRegistroSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    codigo = serializer.validated_data['codigo']
    
    # Verificar código
    valido, mensagem, codigo_obj = verificar_codigo(email, codigo, tipo='cadastro')
    
    if not valido:
        return Response({'error': mensagem}, status=status.HTTP_400_BAD_REQUEST)
    
    # Recuperar dados do registro do cache
    cache_key = f'registro_pendente_{email}'
    dados_registro = cache.get(cache_key)
    
    if not dados_registro:
        return Response({
            'error': 'Dados de registro expirados. Inicie o registro novamente.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Criar usuário
        password = dados_registro.pop('password')
        categorias = dados_registro.pop('categorias_interesse', [])
        localizacoes = dados_registro.pop('localizacoes_interesse', [])
        
        pessoa = Pessoa.objects.create_user(
            password=password,
            **dados_registro
        )
        
        # Adicionar relações ManyToMany
        if categorias:
            pessoa.categorias_interesse.set(categorias)
        if localizacoes:
            pessoa.localizacoes_interesse.set(localizacoes)
        
        # Marcar código como usado
        codigo_obj.marcar_como_usado()
        
        # Limpar cache
        cache.delete(cache_key)
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(pessoa)
        
        return Response({
            'message': f'🎉 Conta criada com sucesso! Bem-vinda, {pessoa.nome_exibicao}!',
            'user': PessoaSerializer(pessoa).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'Erro ao criar conta: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='login',
    summary='🔐 Login',
    description='''
    Faz login com email e senha.
    
    **Retorna:**
    - Tokens JWT (access + refresh)
    - Dados do usuário
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Autenticação - Público'],
    request=LoginComCodigoSerializer,
    responses={
        200: OpenApiResponse(description="Login realizado com sucesso"),
        401: OpenApiResponse(description="Credenciais inválidas")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login com email e senha
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = LoginComCodigoSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    user = serializer.validated_data['user']
    
    # Gerar tokens JWT
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': f'Bem-vinda de volta, {user.nome_exibicao}!',
        'user': PessoaSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='solicitar_codigo',
    summary='📧 Solicitar Código',
    description='''
    Solicita envio de código de verificação por email.
    
    **Usos:**
    - `cadastro`: Verificar email no registro
    - `login`: Login com 2FA
    - `recuperacao`: Recuperar senha
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Autenticação - Público'],
    request=SolicitarCodigoSerializer,
    responses={
        200: OpenApiResponse(description="Código enviado"),
        400: OpenApiResponse(description="Email inválido")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def solicitar_codigo(request):
    """
    Solicita envio de código de verificação
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = SolicitarCodigoSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    tipo = serializer.validated_data['tipo']
    
    # Enviar código
    sucesso, mensagem, codigo_obj = enviar_codigo_verificacao(email, tipo=tipo)
    
    if not sucesso:
        return Response(
            {'error': mensagem},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': f'Código enviado para {email}',
        'tipo': tipo,
        'validade': '10 minutos',
        'tentativas_maximas': 3
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='verificar_codigo',
    summary='✅ Verificar Código',
    description='''
    Verifica se o código é válido.
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Autenticação - Público'],
    request=VerificarCodigoSerializer,
    responses={
        200: OpenApiResponse(description="Código válido"),
        400: OpenApiResponse(description="Código inválido ou expirado")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_codigo_view(request):
    """
    Verifica código de verificação
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = VerificarCodigoSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    codigo = serializer.validated_data['codigo']
    tipo = serializer.validated_data['tipo']
    
    # Verificar código
    valido, mensagem, codigo_obj = verificar_codigo(email, codigo, tipo=tipo)
    
    if not valido:
        return Response({'error': mensagem}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'message': 'Código verificado com sucesso',
        'email': email
    }, status=status.HTTP_200_OK)


# ============== ENDPOINTS PROTEGIDOS (REQUEREM AUTENTICAÇÃO) ==============

@extend_schema(
    operation_id='meu_perfil',
    summary='👤 Meu Perfil',
    description='Retorna dados do usuário logado',
    tags=['Perfil - Protegido'],
    responses={200: PessoaSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meu_perfil(request):
    """
    Retorna dados do usuário logado
    ENDPOINT PROTEGIDO - requer autenticação JWT
    """
    return Response(PessoaSerializer(request.user).data)


@extend_schema(
    operation_id='atualizar_perfil',
    summary='✏️ Atualizar Perfil',
    description='Atualiza dados do usuário logado',
    tags=['Perfil - Protegido'],
    request=PessoaSerializer,
    responses={200: PessoaSerializer}
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def atualizar_perfil(request):
    """
    Atualiza dados do usuário logado
    ENDPOINT PROTEGIDO - requer autenticação JWT
    """
    serializer = PessoaSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Perfil atualizado com sucesso',
            'user': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
