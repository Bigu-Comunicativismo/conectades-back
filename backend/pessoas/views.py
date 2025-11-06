from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
from .models import Pessoa, CodigoVerificacao
from .serializers import (
    PessoaSerializer,
    RegistroComCodigoSerializer,
    ConfirmarRegistroSerializer,
    LoginComCodigoSerializer,
    SolicitarCodigoSerializer,
    VerificarCodigoSerializer,
    SolicitarRecuperacaoSenhaSerializer,
    RedefinirSenhaSerializer,
    TipoUsuarioSerializer,
    GeneroSerializer,
    CategoriaInteresseSerializer,
    LocalizacaoInteresseSerializer,
)
from .email_service import enviar_codigo_verificacao, verificar_codigo, enviar_link_ativacao


# ============== ENDPOINTS PÚBLICOS (SEM AUTENTICAÇÃO) ==============

@extend_schema(
    operation_id='listar_opcoes_cadastro',
    summary='Listar Opções de Cadastro',
    description='''
    Retorna todas as opções disponíveis para cadastro.
    
    **Estrutura de Localizações:**
    - `cidades`: Lista de cidades disponíveis
    - `bairros_por_cidade`: Dicionário com bairros agrupados por cidade
    
    Isso facilita a criação de dropdowns dependentes (cidade → bairro).
    ''',
    tags=['Cadastro - Público'],
    responses={200: OpenApiResponse(description="Opções disponíveis")}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_opcoes_cadastro(request):
    """
    Lista todas as opções disponíveis para o cadastro
    ENDPOINT PÚBLICO - não requer autenticação
    
    Query params:
    - refresh=true: Force cache refresh
    """
    from .models import TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse
    
    # Verificar se deve forçar refresh do cache
    force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
    
    # Tentar buscar do cache primeiro (se não for refresh)
    cache_key = 'opcoes_cadastro_completo'
    if not force_refresh:
        dados_cache = cache.get(cache_key)
        if dados_cache:
            return Response(dados_cache)
    
    # Buscar cidades e bairros separadamente
    cidades = LocalizacaoInteresse.objects.filter(
        ativo=True,
        tipo='cidade'
    ).order_by('ordem', 'nome')
    
    bairros = LocalizacaoInteresse.objects.filter(
        ativo=True,
        tipo='bairro'
    ).order_by('cidade', 'ordem', 'nome')
    
    # Agrupar bairros por cidade
    bairros_por_cidade = {}
    for bairro in bairros:
        cidade_nome = bairro.cidade or 'Outros'
        if cidade_nome not in bairros_por_cidade:
            bairros_por_cidade[cidade_nome] = []
        bairros_por_cidade[cidade_nome].append({
            'id': bairro.id,
            'nome': bairro.nome,
            'codigo': bairro.codigo,
        })
    
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
        'cidades': [
            {
                'id': cidade.id,
                'nome': cidade.nome,
                'codigo': cidade.codigo,
                'estado': cidade.estado,
            }
            for cidade in cidades
        ],
        'bairros_por_cidade': bairros_por_cidade,
        # Mantido para compatibilidade retroativa
        'localizacoes_interesse': LocalizacaoInteresseSerializer(
            LocalizacaoInteresse.objects.filter(ativo=True),
            many=True
        ).data,
    }
    
    # Armazenar em cache por 1 hora
    cache.set(cache_key, dados, 60 * 60)
    
    return Response(dados)


@extend_schema(
    operation_id='listar_bairros_cidade',
    summary='Listar Bairros por Cidade',
    description='''
    Retorna todos os bairros de uma cidade específica.
    
    **Uso:** Útil para popular o dropdown de bairros após selecionar a cidade.
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Cadastro - Público'],
    responses={
        200: OpenApiResponse(description="Lista de bairros"),
        404: OpenApiResponse(description="Cidade não encontrada")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_bairros_cidade(request, cidade):
    """
    Lista bairros de uma cidade específica
    ENDPOINT PÚBLICO - não requer autenticação
    """
    from .models import LocalizacaoInteresse
    
    # Tentar buscar do cache primeiro
    cache_key = f'bairros_cidade_{cidade}'
    dados_cache = cache.get(cache_key)
    
    if dados_cache:
        return Response(dados_cache)
    
    # Verificar se a cidade existe
    cidade_existe = LocalizacaoInteresse.objects.filter(
        tipo='cidade',
        nome=cidade,
        ativo=True
    ).exists()
    
    if not cidade_existe:
        return Response(
            {'error': f'Cidade "{cidade}" não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Buscar bairros
    bairros = LocalizacaoInteresse.objects.filter(
        tipo='bairro',
        cidade=cidade,
        ativo=True
    ).order_by('ordem', 'nome')
    
    dados = {
        'cidade': cidade,
        'total': bairros.count(),
        'bairros': [
            {
                'id': bairro.id,
                'nome': bairro.nome,
                'codigo': bairro.codigo,
            }
            for bairro in bairros
        ]
    }
    
    # Armazenar em cache por 1 hora
    cache.set(cache_key, dados, 60 * 60)
    
    return Response(dados)


@extend_schema(
    operation_id='iniciar_registro',
    summary='📝 Criar Conta',
    description='''
    Cria uma conta e envia link de ativação por email.
    
    **Fluxo:**
    1. Preencha todos os campos obrigatórios
    2. Sistema valida os dados e salva temporariamente
    3. Link de ativação é enviado para o email
    4. Clique no link para ativar a conta
    5. Após ativação, é redirecionado para o frontend já autenticado
    
    **Upload de Avatar:**
    - Formato aceito: `multipart/form-data`
    - Campo `avatar`: arquivo de imagem (JPG, PNG, etc.)
    - Outros campos: valores normais (text)
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Cadastro - Público'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'description': 'Email válido (receberá código de verificação)'},
                'username': {'type': 'string', 'minLength': 3, 'description': 'Nome de usuário único'},
                'password': {'type': 'string', 'minLength': 8, 'format': 'password', 'description': 'Senha forte'},
                'nome_completo': {'type': 'string', 'description': 'Nome completo'},
                'cpf': {'type': 'string', 'description': 'CPF (formato: 000.000.000-00)'},
                'telefone': {'type': 'string', 'description': 'Telefone com DDD'},
                'tipo_usuario': {'type': 'integer', 'description': 'ID do tipo de usuário'},
                'genero': {'type': 'integer', 'description': 'ID do gênero'},
                'cidade': {'type': 'string', 'description': 'Cidade onde mora'},
                'bairro': {'type': 'string', 'description': 'Bairro onde mora'},
                'nome_social': {'type': 'string', 'description': 'Nome social (opcional)'},
                'mini_bio': {'type': 'string', 'description': 'Mini biografia'},
                'avatar': {'type': 'string', 'format': 'binary', 'description': '📸 Foto de perfil (arquivo de imagem)'},
                'categorias_interesse': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs das categorias de interesse'},
                'localizacoes_interesse': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs das localizações de interesse'},
            },
            'required': ['email', 'username', 'password', 'nome_completo', 'cpf', 'telefone', 'tipo_usuario', 'genero', 'cidade', 'bairro', 'mini_bio']
        }
    },
    responses={
        200: OpenApiResponse(description="Link de ativação enviado para o email"),
        400: OpenApiResponse(description="Erro de validação")
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def iniciar_registro(request):
    """
    Valida dados e envia link de ativação por email
    ENDPOINT PÚBLICO - não requer autenticação
    
    **IMPORTANTE:** Use multipart/form-data para enviar os dados (necessário para upload de avatar)
    """
    try:
        # Validar Content-Type
        content_type = request.content_type
        
        if not content_type:
            return Response({
                'error': 'Content-Type não especificado',
                'dica': 'Use Content-Type: multipart/form-data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Se for application/json, rejeitar com mensagem clara
        if 'application/json' in content_type.lower():
            return Response({
                'error': 'Content-Type incorreto',
                'recebido': content_type,
                'esperado': 'multipart/form-data',
                'dica': 'Este endpoint requer multipart/form-data para suportar upload de avatar. Configure seu cliente HTTP corretamente.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar se tem boundary no multipart
        if 'multipart/form-data' in content_type.lower():
            if 'boundary=' not in content_type.lower():
                return Response({
                    'error': 'Content-Type multipart/form-data sem boundary',
                    'recebido': content_type,
                    'dica': 'O boundary é gerado automaticamente pelo cliente HTTP. Certifique-se de que seu cliente está configurado corretamente para enviar multipart/form-data.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalizar campos multipart (mesmo fix aplicado em campanhas)
        data = dict(request.data)
        
        def normalize_field(value):
            """Se o valor é uma lista com um único elemento, retorna o elemento"""
            if isinstance(value, list) and len(value) == 1:
                return value[0]
            return value
        
        # Normalizar todos os campos do formulário de registro
        for field in list(data.keys()):
            data[field] = normalize_field(data[field])
        
        # Processar campos que devem ser arrays (IDs separados por vírgula)
        for field in ['categorias_interesse', 'localizacoes_interesse']:
            if field in data and data[field]:
                value = data[field]
                # Se for string, converter para lista de IDs
                if isinstance(value, str):
                    try:
                        # Separar por vírgula e converter para inteiros
                        data[field] = [int(id.strip()) for id in value.split(',') if id.strip()]
                    except ValueError:
                        return Response({
                            'error': f'Formato inválido para {field}',
                            'recebido': value,
                            'formato_esperado': 'IDs separados por vírgula (ex: "1,2,3") ou lista de inteiros'
                        }, status=status.HTTP_400_BAD_REQUEST)
                # Se já for lista, garantir que são inteiros
                elif isinstance(value, list):
                    try:
                        data[field] = [int(id) for id in value if id]
                    except ValueError:
                        return Response({
                            'error': f'Formato inválido para {field}',
                            'recebido': value,
                            'formato_esperado': 'Lista de IDs inteiros'
                        }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegistroComCodigoSerializer(data=data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        # Converter dados para formato serializável (dict com IDs ao invés de objetos)
        # IMPORTANTE: Arquivos (avatar) são salvos temporariamente e referenciados por caminho
        dados_cache = {}
        avatar_temp_path = None
        
        for key, value in serializer.validated_data.items():
            # Salvar avatar em arquivo temporário
            if key == 'avatar' and value:
                import os
                from django.core.files.uploadedfile import UploadedFile
                from django.conf import settings
                import logging
                logger = logging.getLogger(__name__)
                
                logger.info(f"📸 Avatar detectado! Tipo: {type(value)}, Nome: {getattr(value, 'name', 'sem nome')}")
                
                # Criar diretório temporário se não existir
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'avatars_temp')
                os.makedirs(temp_dir, exist_ok=True)
                logger.info(f"📁 Diretório temporário: {temp_dir}")
                
                # Gerar nome único para o arquivo temporário
                import uuid
                ext = os.path.splitext(value.name)[1] if hasattr(value, 'name') else '.jpg'
                temp_filename = f"{uuid.uuid4()}{ext}"
                avatar_temp_path = os.path.join(temp_dir, temp_filename)
                
                logger.info(f"💾 Salvando avatar em: {avatar_temp_path}")
                
                # Salvar arquivo temporário
                with open(avatar_temp_path, 'wb+') as destination:
                    for chunk in value.chunks():
                        destination.write(chunk)
                
                # Verificar se arquivo foi salvo
                if os.path.exists(avatar_temp_path):
                    file_size = os.path.getsize(avatar_temp_path)
                    logger.info(f"✅ Avatar salvo com sucesso! Tamanho: {file_size} bytes")
                else:
                    logger.error(f"❌ Erro: arquivo não foi salvo em {avatar_temp_path}")
                
                # Armazenar apenas o caminho relativo no cache
                avatar_temp_relative = os.path.join('avatars_temp', temp_filename)
                dados_cache['avatar_temp'] = avatar_temp_relative
                logger.info(f"🗂️ Caminho armazenado no cache: {avatar_temp_relative}")
                continue
            
            # Pular valores bytes (por segurança)
            if isinstance(value, bytes):
                continue
            
            # Pular valores None
            if value is None:
                dados_cache[key] = None
            # Converter objetos Django (ForeignKey) para IDs
            elif hasattr(value, 'pk'):
                dados_cache[key] = value.pk
            # Converter QuerySets e listas de objetos para listas de IDs
            elif hasattr(value, '__iter__') and not isinstance(value, (str, dict)):
                try:
                    dados_cache[key] = [item.pk if hasattr(item, 'pk') else item for item in value]
                except (TypeError, AttributeError):
                    dados_cache[key] = value
            else:
                dados_cache[key] = value
        
        # Armazenar dados temporariamente em cache (expira em 24 horas)
        cache_key = f'registro_pendente_{email}'
        cache.set(cache_key, dados_cache, 60 * 60 * 24)
        
        # Enviar link de ativação
        sucesso, mensagem, codigo_obj = enviar_link_ativacao(email, tipo='cadastro')
        
        if not sucesso:
            return Response(
                {'error': mensagem},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Link de ativação enviado para seu email',
            'email': email,
            'validade': '24 horas',
            'proximo_passo': 'Clique no link enviado para ativar sua conta'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Log do erro para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao iniciar registro: {str(e)}", exc_info=True)
        
        return Response({
            'error': 'Erro ao processar cadastro',
            'detail': str(e) if settings.DEBUG else 'Erro interno do servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        categorias_ids = dados_registro.pop('categorias_interesse', [])
        localizacoes_ids = dados_registro.pop('localizacoes_interesse', [])
        
        # Reconstituir objetos ForeignKey a partir dos IDs
        from .models import TipoUsuario, Genero
        if 'tipo_usuario' in dados_registro and isinstance(dados_registro['tipo_usuario'], int):
            dados_registro['tipo_usuario'] = TipoUsuario.objects.get(pk=dados_registro['tipo_usuario'])
        if 'genero' in dados_registro and isinstance(dados_registro['genero'], int):
            dados_registro['genero'] = Genero.objects.get(pk=dados_registro['genero'])
        
        pessoa = Pessoa.objects.create_user(
            password=password,
            **dados_registro
        )
        
        # Adicionar relações ManyToMany (usando IDs)
        if categorias_ids:
            pessoa.categorias_interesse.set(categorias_ids)
        if localizacoes_ids:
            pessoa.localizacoes_interesse.set(localizacoes_ids)
        
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
    operation_id='ativar_conta',
    summary='✅ Ativar Conta',
    description='''
    Ativa a conta do usuário via token enviado por email.
    
    **Fluxo:**
    1. Usuário clica no link de ativação recebido por email
    2. Sistema valida o token
    3. Conta é criada e ativada
    4. Retorna tokens JWT para login automático
    5. Frontend deve redirecionar para a página inicial já autenticado
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Cadastro - Público'],
    responses={
        200: OpenApiResponse(description="Conta ativada com sucesso"),
        400: OpenApiResponse(description="Token inválido ou expirado")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@transaction.atomic
def ativar_conta(request, token):
    """
    Ativa conta via token único
    ENDPOINT PÚBLICO - não requer autenticação
    """
    try:
        # Buscar token
        codigo_obj = CodigoVerificacao.objects.filter(
            token=token,
            tipo='cadastro',
            usado=False
        ).first()
        
        if not codigo_obj:
            return Response({
                'error': 'Token inválido ou já utilizado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar validade
        valido, mensagem = codigo_obj.esta_valido()
        
        if not valido:
            return Response({'error': mensagem}, status=status.HTTP_400_BAD_REQUEST)
        
        # Recuperar dados do registro do cache
        cache_key = f'registro_pendente_{codigo_obj.email}'
        dados_registro = cache.get(cache_key)
        
        if not dados_registro:
            return Response({
                'error': 'Dados de registro expirados. Inicie o registro novamente.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Criar usuário
        password = dados_registro.pop('password')
        categorias_ids = dados_registro.pop('categorias_interesse', [])
        localizacoes_ids = dados_registro.pop('localizacoes_interesse', [])
        
        # Reconstituir objetos ForeignKey a partir dos IDs
        # tipo_usuario e genero já vêm como IDs do cache
        from .models import TipoUsuario, Genero
        if 'tipo_usuario' in dados_registro and isinstance(dados_registro['tipo_usuario'], int):
            dados_registro['tipo_usuario'] = TipoUsuario.objects.get(pk=dados_registro['tipo_usuario'])
        if 'genero' in dados_registro and isinstance(dados_registro['genero'], int):
            dados_registro['genero'] = Genero.objects.get(pk=dados_registro['genero'])
        
        pessoa = Pessoa.objects.create_user(
            password=password,
            **dados_registro
        )
        
        # Adicionar relações ManyToMany (usando IDs)
        if categorias_ids:
            pessoa.categorias_interesse.set(categorias_ids)
        if localizacoes_ids:
            pessoa.localizacoes_interesse.set(localizacoes_ids)
        
        # Marcar token como usado
        codigo_obj.marcar_como_usado()
        
        # Limpar cache
        cache.delete(cache_key)
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(pessoa)
        
        # Retornar HTML que redireciona para o frontend com os tokens
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        html_response = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Conta Ativada - Conectades</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    text-align: center;
                    background: white;
                    padding: 3rem;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                .success {{
                    color: #10b981;
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }}
                h1 {{
                    color: #1f2937;
                    margin-bottom: 1rem;
                }}
                p {{
                    color: #6b7280;
                    margin-bottom: 2rem;
                }}
                .spinner {{
                    border: 4px solid #f3f4f6;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅</div>
                <h1>Conta Ativada com Sucesso!</h1>
                <p>Bem-vinda à Conectades, {pessoa.nome_exibicao}!</p>
                <p>Redirecionando para o aplicativo...</p>
                <div class="spinner"></div>
            </div>
            <script>
                // Salvar tokens no localStorage e redirecionar
                setTimeout(() => {{
                    const tokens = {{
                        access: '{access_token}',
                        refresh: '{refresh_token}'
                    }};
                    const user = {PessoaSerializer(pessoa).data};
                    
                    // Redirecionar para o frontend com os dados
                    window.location.href = '{frontend_url}/auth/ativacao-sucesso?access=' + encodeURIComponent(tokens.access) + '&refresh=' + encodeURIComponent(tokens.refresh);
                }}, 2000);
            </script>
        </body>
        </html>
        '''
        
        from django.http import HttpResponse
        return HttpResponse(html_response)
    
    except Exception as e:
        return Response(
            {'error': f'Erro ao ativar conta: {str(e)}'},
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


@extend_schema(
    operation_id='solicitar_recuperacao_senha',
    summary='🔑 Solicitar Recuperação de Senha',
    description='''
    ETAPA 1 de 2: Solicita recuperação de senha.
    
    **Fluxo:**
    1. Informe seu email cadastrado
    2. Sistema verifica se o email existe
    3. Código de 6 dígitos é enviado para o email
    4. Use o código na próxima etapa (redefinir_senha)
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Recuperação de Senha - Público'],
    request=SolicitarRecuperacaoSenhaSerializer,
    responses={
        200: OpenApiResponse(description="Código enviado para o email"),
        404: OpenApiResponse(description="Email não encontrado")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def solicitar_recuperacao_senha(request):
    """
    ETAPA 1: Solicita recuperação de senha e envia código por email
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = SolicitarRecuperacaoSenhaSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Enviar código de verificação
    sucesso, mensagem, codigo_obj = enviar_codigo_verificacao(email, tipo='recuperacao')
    
    if not sucesso:
        return Response(
            {'error': mensagem},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'Código de recuperação enviado para seu email',
        'email': email,
        'validade': '10 minutos',
        'proximo_passo': 'Use o endpoint /api/auth/senha/redefinir/ com o código recebido'
    }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='redefinir_senha',
    summary='🔐 Redefinir Senha',
    description='''
    ETAPA 2 de 2: Redefine a senha com código de verificação.
    
    **Fluxo:**
    1. Digite o código de 6 dígitos recebido no email
    2. Digite a nova senha (mínimo 8 caracteres)
    3. Confirme a nova senha
    4. Sistema verifica o código e atualiza a senha
    5. Retorna tokens JWT para login automático
    
    **ENDPOINT PÚBLICO** - não requer autenticação
    ''',
    tags=['Recuperação de Senha - Público'],
    request=RedefinirSenhaSerializer,
    responses={
        200: OpenApiResponse(description="Senha redefinida com sucesso"),
        400: OpenApiResponse(description="Código inválido ou senhas não coincidem")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def redefinir_senha(request):
    """
    ETAPA 2: Verifica código e redefine a senha
    ENDPOINT PÚBLICO - não requer autenticação
    """
    serializer = RedefinirSenhaSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    codigo = serializer.validated_data['codigo']
    nova_senha = serializer.validated_data['nova_senha']
    
    # Verificar código
    valido, mensagem, codigo_obj = verificar_codigo(email, codigo, tipo='recuperacao')
    
    if not valido:
        return Response({'error': mensagem}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar usuário pelo email
        pessoa = Pessoa.objects.get(email=email)
        
        # Redefinir senha
        pessoa.set_password(nova_senha)
        pessoa.save()
        
        # Marcar código como usado
        codigo_obj.marcar_como_usado()
        
        # Gerar tokens JWT para login automático
        refresh = RefreshToken.for_user(pessoa)
        
        return Response({
            'message': f'✅ Senha redefinida com sucesso! Você já está logada, {pessoa.nome_exibicao}!',
            'user': PessoaSerializer(pessoa).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    except Pessoa.DoesNotExist:
        return Response({
            'error': 'Usuário não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {'error': f'Erro ao redefinir senha: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
    description='''
    Atualiza dados do usuário logado.
    
    **Upload de Avatar:**
    - Formato aceito: `multipart/form-data` (para upload de imagem)
    - Campo `avatar`: arquivo de imagem (JPG, PNG, etc.)
    - Outros campos: valores normais (text)
    ''',
    tags=['Perfil - Protegido'],
    request=PessoaSerializer,
    responses={200: PessoaSerializer}
)
@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def atualizar_perfil(request):
    """
    Atualiza dados do usuário logado
    ENDPOINT PROTEGIDO - requer autenticação JWT
    
    **IMPORTANTE:** Use multipart/form-data para enviar os dados (necessário para upload de avatar)
    """
    # Validar Content-Type se for multipart
    content_type = request.content_type or ''
    if 'multipart/form-data' in content_type.lower():
        if 'boundary=' not in content_type.lower():
            return Response({
                'error': 'Content-Type multipart/form-data sem boundary',
                'recebido': content_type,
                'dica': 'Configure seu cliente HTTP corretamente para enviar multipart/form-data com boundary.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normalizar campos multipart (mesmo fix aplicado em campanhas)
    data = dict(request.data)
    
    def normalize_field(value):
        """Se o valor é uma lista com um único elemento, retorna o elemento"""
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value
    
    # Normalizar todos os campos
    for field in list(data.keys()):
        data[field] = normalize_field(data[field])
    
    # Processar campos que devem ser arrays (IDs separados por vírgula)
    for field in ['categorias_interesse', 'localizacoes_interesse']:
        if field in data and data[field]:
            value = data[field]
            # Se for string, converter para lista de IDs
            if isinstance(value, str):
                try:
                    data[field] = [int(id.strip()) for id in value.split(',') if id.strip()]
                except ValueError:
                    return Response({
                        'error': f'Formato inválido para {field}',
                        'recebido': value,
                        'formato_esperado': 'IDs separados por vírgula (ex: "1,2,3")'
                    }, status=status.HTTP_400_BAD_REQUEST)
            # Se já for lista, garantir que são inteiros
            elif isinstance(value, list):
                try:
                    data[field] = [int(id) for id in value if id]
                except ValueError:
                    return Response({
                        'error': f'Formato inválido para {field}',
                        'recebido': value,
                        'formato_esperado': 'Lista de IDs inteiros'
                    }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = PessoaSerializer(
        request.user,
        data=data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Perfil atualizado com sucesso',
            'user': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
