from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from .models import Organizadora, Campanha, ItemCampanha, SolicitacaoBeneficiaria
from .serializers import OrganizadoraSerializer, CampanhaSerializer, ItemCampanhaSerializer
from .serializers_solicitacao import SolicitacaoRespostaSerializer

@extend_schema(
    operation_id='criar_campanha',
    summary='Criar Campanha',
    description='Cria uma nova campanha. A organizadora é preenchida automaticamente com o usuário atual. Envie a imagem como arquivo multipart/form-data.',
    tags=['Campanhas'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'titulo': {'type': 'string', 'description': 'Título da campanha'},
                'subtitulo': {'type': 'string', 'description': 'Subtítulo da campanha'},
                'descricao': {'type': 'string', 'description': 'Descrição detalhada da campanha'},
                'beneficiaria_id': {'type': 'integer', 'description': 'ID da beneficiária (opcional)', 'nullable': True},
                'imagem': {'type': 'string', 'format': 'binary', 'description': 'Arquivo de imagem (PNG, JPG, JPEG, GIF, WEBP)'},
                'categorias': {'type': 'array', 'items': {'type': 'integer'}, 'description': 'IDs das categorias'},
                'whatsapp': {'type': 'string', 'description': 'WhatsApp de contato', 'nullable': True},
                'localizacao': {'type': 'integer', 'description': 'ID da localização', 'nullable': True},
                'data_inicio': {'type': 'string', 'format': 'date-time', 'description': 'Data de início da campanha'},
                'prazo': {'type': 'string', 'format': 'date-time', 'description': 'Data de término da campanha'},
                'ativa': {'type': 'boolean', 'description': 'Se a campanha está ativa', 'default': True},
            },
            'required': ['titulo', 'descricao', 'data_inicio', 'prazo']
        }
    },
    responses={
        201: CampanhaSerializer,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def criar_campanha(request):
    """API para criar campanha. Doadoras e Beneficiárias podem criar campanhas."""
    from backend.pessoas.models import TipoUsuario
    
    # Verificar se o usuário é uma Doadora ou Beneficiária
    try:
        tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
        tipo_beneficiaria = TipoUsuario.objects.get(codigo='beneficiaria')
        
        tipos_permitidos = [tipo_doadora, tipo_beneficiaria]
        
        if request.user.tipo_usuario not in tipos_permitidos:
            return Response({
                'error': 'Apenas Doadoras e Beneficiárias podem criar campanhas!',
                'tipo_usuario_atual': request.user.tipo_usuario.nome if request.user.tipo_usuario else 'Não definido',
                'tipos_permitidos': ['Doadora', 'Beneficiária']
            }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': f'Erro ao verificar tipo de usuário: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    data = request.data.copy()
    
    # Criar ou obter perfil de organizadora automaticamente
    organizadora, created = Organizadora.objects.get_or_create(
        pessoa=request.user,
        defaults={'ativo': True}
    )
    
    data['organizadora_id'] = organizadora.id
    
    serializer = CampanhaSerializer(data=data)
    if serializer.is_valid():
        campanha = serializer.save()
        
        # Invalidar cache de listagens
        cache.delete_many([
            'campanhas_all',
            f'campanhas_user_{request.user.id}'
        ])
        
        message = f'Campanha "{campanha.titulo}" criada com sucesso!'
        if created:
            message += ' 🎉 Você agora é uma Organizadora!'
        
        return Response({
            'message': message,
            'data': CampanhaSerializer(campanha).data,
            'organizadora_criada': created
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id='listar_campanhas',
    summary='Listar Todas as Campanhas',
    description='''
    Lista todas as campanhas do sistema com filtros, busca e ordenação.
    
    **Query Params:**
    - `busca`: Busca por título ou descrição
    - `categoria`: ID da categoria para filtrar
    - `localizacao`: ID da localização para filtrar
    - `status`: Status da campanha (ativa, encerrada, todas)
    - `ordenar`: Campo de ordenação (recente, antiga, prazo, progresso)
    ''',
    tags=['Campanhas'],
    parameters=[
        OpenApiParameter(name='busca', type=str, description='Busca por título ou descrição', required=False),
        OpenApiParameter(name='categoria', type=int, description='Filtrar por ID da categoria', required=False),
        OpenApiParameter(name='localizacao', type=int, description='Filtrar por ID da localização', required=False),
        OpenApiParameter(name='status', type=str, description='Filtrar por status: ativa, encerrada, todas', required=False, enum=['ativa', 'encerrada', 'todas']),
        OpenApiParameter(name='ordenar', type=str, description='Ordenar por: recente, antiga, prazo, progresso', required=False, enum=['recente', 'antiga', 'prazo', 'progresso']),
    ],
    responses={
        200: CampanhaSerializer(many=True),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_campanhas(request):
    """API para listar campanhas com filtros, busca e ordenação."""
    
    # Obter query params
    busca = request.query_params.get('busca', None)
    categoria_id = request.query_params.get('categoria', None)
    localizacao_id = request.query_params.get('localizacao', None)
    status_filtro = request.query_params.get('status', 'ativa')  # Padrão: apenas ativas
    ordenar = request.query_params.get('ordenar', 'recente')  # Padrão: mais recentes
    
    # Montar cache key baseado nos filtros
    cache_key = f'campanhas_{busca}_{categoria_id}_{localizacao_id}_{status_filtro}_{ordenar}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # Query base otimizada
        campanhas = Campanha.objects.select_related(
            'organizadora__pessoa',
            'beneficiaria'
        ).prefetch_related(
            'doacoes', 'itens'
        ).filter(publicada=True)
        
        # Filtro por status
        if status_filtro == 'ativa':
            campanhas = campanhas.filter(ativa=True)
        elif status_filtro == 'encerrada':
            campanhas = campanhas.filter(ativa=False)
        # Se 'todas', não filtra por ativa
        
        # Filtro por categoria
        if categoria_id:
            campanhas = campanhas.filter(categorias__id=categoria_id)
        
        # Filtro por localização
        if localizacao_id:
            campanhas = campanhas.filter(localizacao_id=localizacao_id)
        
        # Busca por título ou descrição
        if busca:
            campanhas = campanhas.filter(
                Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
            )
        
        # Ordenação
        if ordenar == 'recente':
            campanhas = campanhas.order_by('-data_inicio')
        elif ordenar == 'antiga':
            campanhas = campanhas.order_by('data_inicio')
        elif ordenar == 'prazo':
            campanhas = campanhas.order_by('prazo')
        elif ordenar == 'progresso':
            # Ordenar por percentual (requer anotação personalizada)
            campanhas = campanhas.order_by('-data_inicio')  # Fallback
        else:
            campanhas = campanhas.order_by('-data_inicio')
        
        serializer = CampanhaSerializer(campanhas, many=True)
        cached_data = serializer.data
        
        # Cache por 1 hora
        cache.set(cache_key, cached_data, settings.CACHE_TTL)
    
    return Response(cached_data)

@extend_schema(
    operation_id='minhas_campanhas',
    summary='Minhas Campanhas',
    description='Lista as campanhas criadas pelo usuário atual (organizadora) com cache.',
    tags=['Campanhas'],
    responses={
        200: CampanhaSerializer(many=True),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_campanhas(request):
    """API para listar campanhas do usuário atual com cache"""
    cache_key = f'campanhas_user_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        try:
            organizadora = Organizadora.objects.get(pessoa=request.user)
            campanhas = Campanha.objects.select_related(
                'organizadora__pessoa',
                'beneficiaria'
            ).prefetch_related(
                'doacoes', 'itens', 'doacoes__doadora', 'doacoes__item'
            ).filter(organizadora=organizadora)
            
            serializer = CampanhaSerializer(campanhas, many=True)
            cached_data = serializer.data
            
            # Cache por 30 minutos (dados do usuário mudam mais frequentemente)
            cache.set(cache_key, cached_data, settings.CACHE_TTL_USER)
            
        except Organizadora.DoesNotExist:
            cached_data = {
                'message': 'Usuário não é organizadora',
                'campanhas': []
            }
            cache.set(cache_key, cached_data, settings.CACHE_TTL_SHORT)  # Cache curto para erro
    
    return Response(cached_data)

@extend_schema(
    operation_id='detalhar_campanha',
    summary='Detalhar Campanha',
    description='Retorna os detalhes completos de uma campanha específica por ID com cache.',
    tags=['Campanhas'],
    responses={
        200: CampanhaSerializer,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def detalhar_campanha(request, campanha_id: int):
    """API para obter detalhes de uma campanha específica com cache"""
    cache_key = f'campanha_detail_{campanha_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        try:
            # Query otimizada com select_related e prefetch_related
            campanha = Campanha.objects.select_related(
                'organizadora__pessoa',
                'beneficiaria'
            ).prefetch_related(
                'doacoes', 'itens'
            ).get(id=campanha_id)
            
            # Verificar se a campanha é publicada (ou se o usuário é o dono)
            if not campanha.publicada:
                # Se não está publicada, só o dono pode ver
                if not request.user.is_authenticated:
                    return Response({
                        'error': 'Campanha não encontrada ou não publicada'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                try:
                    organizadora = Organizadora.objects.get(pessoa=request.user)
                    if campanha.organizadora != organizadora:
                        return Response({
                            'error': 'Campanha não encontrada ou não publicada'
                        }, status=status.HTTP_404_NOT_FOUND)
                except Organizadora.DoesNotExist:
                    return Response({
                        'error': 'Campanha não encontrada ou não publicada'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CampanhaSerializer(campanha)
            cached_data = serializer.data
            
            # Cache por 1 hora
            cache.set(cache_key, cached_data, settings.CACHE_TTL)
            
        except Campanha.DoesNotExist:
            return Response({
                'error': 'Campanha não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(cached_data)



@extend_schema(
    operation_id='listar_itens_campanha',
    summary='Listar Itens de uma Campanha',
    description='Lista todos os itens solicitados em uma campanha específica.',
    tags=['Campanhas'],
    responses={200: ItemCampanhaSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_itens_campanha(request, campanha_id: int):
    """Lista os itens de uma campanha"""
    itens = ItemCampanha.objects.filter(campanha_id=campanha_id).order_by('nome')
    serializer = ItemCampanhaSerializer(itens, many=True)
    return Response(serializer.data)


# ==================== SOLICITAÇÕES DE BENEFICIÁRIA ====================

@extend_schema(
    operation_id='minhas_solicitacoes_beneficiaria',
    summary='Minhas Solicitações (Beneficiária)',
    description='Lista as solicitações de associação como beneficiária para o usuário atual.',
    tags=['Solicitações de Beneficiária'],
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_solicitacoes_beneficiaria(request):
    """Lista as solicitações pendentes para o usuário como beneficiária"""
    solicitacoes = SolicitacaoBeneficiaria.objects.filter(
        beneficiaria=request.user
    ).select_related('campanha', 'organizadora__pessoa').order_by('-data_criacao')
    
    data = []
    for sol in solicitacoes:
        data.append({
            'id': sol.id,
            'campanha': {
                'id': sol.campanha.id,
                'titulo': sol.campanha.titulo,
                'descricao': sol.campanha.descricao,
                'imagem': sol.campanha.imagem.src.url if sol.campanha.imagem else None,
            },
            'organizadora': {
                'id': sol.organizadora.id,
                'nome': sol.organizadora.pessoa.nome_exibicao,
            },
            'status': sol.status,
            'status_display': sol.status_display,
            'mensagem_organizadora': sol.mensagem_organizadora,
            'mensagem_resposta': sol.mensagem_resposta,
            'data_criacao': sol.data_criacao,
            'data_resposta': sol.data_resposta,
        })
    
    return Response(data)


@extend_schema(
    operation_id='aceitar_solicitacao_beneficiaria',
    summary='Aceitar Solicitação',
    description='Aceita uma solicitação para ser beneficiária de uma campanha.',
    tags=['Solicitações de Beneficiária'],
    request=SolicitacaoRespostaSerializer,
    responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aceitar_solicitacao_beneficiaria(request, solicitacao_id: int):
    """Aceita uma solicitação para ser beneficiária"""
    try:
        solicitacao = SolicitacaoBeneficiaria.objects.select_related('campanha', 'beneficiaria').get(id=solicitacao_id)
        
        # Verificar se o usuário é a beneficiária
        if solicitacao.beneficiaria != request.user:
            return Response({
                'erro': 'Você não tem permissão para responder a esta solicitação'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar se já foi respondida
        if solicitacao.status != 'pendente':
            return Response({
                'erro': f'Esta solicitação já foi {solicitacao.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mensagem = request.data.get('mensagem', '')
        solicitacao.aceitar(mensagem)
        
        return Response({
            'mensagem': 'Solicitação aceita com sucesso!',
            'campanha': {
                'id': solicitacao.campanha.id,
                'titulo': solicitacao.campanha.titulo,
            }
        })
        
    except SolicitacaoBeneficiaria.DoesNotExist:
        return Response({
            'erro': 'Solicitação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='recusar_solicitacao_beneficiaria',
    summary='Recusar Solicitação',
    description='Recusa uma solicitação para ser beneficiária de uma campanha.',
    tags=['Solicitações de Beneficiária'],
    request=SolicitacaoRespostaSerializer,
    responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recusar_solicitacao_beneficiaria(request, solicitacao_id: int):
    """Recusa uma solicitação para ser beneficiária"""
    try:
        solicitacao = SolicitacaoBeneficiaria.objects.select_related('campanha', 'beneficiaria').get(id=solicitacao_id)
        
        # Verificar se o usuário é a beneficiária
        if solicitacao.beneficiaria != request.user:
            return Response({
                'erro': 'Você não tem permissão para responder a esta solicitação'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar se já foi respondida
        if solicitacao.status != 'pendente':
            return Response({
                'erro': f'Esta solicitação já foi {solicitacao.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mensagem = request.data.get('mensagem', '')
        solicitacao.recusar(mensagem)
        
        return Response({
            'mensagem': 'Solicitação recusada. Você foi removida como beneficiária desta campanha.',
            'campanha': {
                'id': solicitacao.campanha.id,
                'titulo': solicitacao.campanha.titulo,
            }
        })
        
    except SolicitacaoBeneficiaria.DoesNotExist:
        return Response({
            'erro': 'Solicitação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)