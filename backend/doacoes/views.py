from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.db.models import Q
from .models import TipoServico, Doacao, DoacaoIndependente
from backend.campanhas.models import Campanha
from backend.pessoas.models import Pessoa
from .serializers import (
    TipoServicoSerializer, DoacaoSerializer, 
    DoacaoIndependenteSerializer, DoacaoIndependenteListSerializer
)


@extend_schema(
    operation_id='criar_doacao',
    summary='Criar Doação',
    description='Cria uma doação vinculada a uma campanha. O doador é o usuário autenticado.',
    tags=['Doações'],
    request=DoacaoSerializer,
    responses={201: DoacaoSerializer, 400: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_doacao(request):
    data = request.data.copy()
    data['doador_id'] = request.user.id
    serializer = DoacaoSerializer(data=data)
    if serializer.is_valid():
        doacao = serializer.save()
        
        # Invalidar cache de doações da campanha
        campanha_id = doacao.campanha.id
        cache.delete(f'doacoes_campanha_{campanha_id}')
        
        return Response(DoacaoSerializer(doacao).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='listar_doacoes_por_campanha',
    summary='Listar Doações por Campanha',
    description='Lista todas as doações vinculadas a uma campanha com cache.',
    tags=['Doações'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_doacoes_por_campanha(request, campanha_id: int):
    cache_key = f'doacoes_campanha_{campanha_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        doacoes = Doacao.objects.select_related(
            'doador',
            'campanha'
        ).filter(campanha_id=campanha_id)
        
        serializer = DoacaoSerializer(doacoes, many=True)
        cached_data = serializer.data
        
        # Cache por 15 minutos (doações mudam mais frequentemente)
        cache.set(cache_key, cached_data, settings.CACHE_TTL_SHORT)
    
    return Response(cached_data)


# ==================== TIPOS DE SERVIÇO ====================

@extend_schema(
    operation_id='listar_tipos_servico',
    summary='Listar Tipos de Serviço',
    description='Lista todos os tipos de serviço ativos com cache.',
    tags=['Tipos de Serviço'],
    responses={200: TipoServicoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(settings.CACHE_TTL)
def listar_tipos_servico(request):
    """Lista todos os tipos de serviço ativos"""
    tipos = TipoServico.objects.filter(ativo=True).order_by('ordem', 'nome')
    serializer = TipoServicoSerializer(tipos, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='criar_tipo_servico',
    summary='Criar Tipo de Serviço',
    description='Cria um novo tipo de serviço (apenas admin).',
    tags=['Tipos de Serviço'],
    request=TipoServicoSerializer,
    responses={201: TipoServicoSerializer, 400: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_tipo_servico(request):
    """Cria um novo tipo de serviço"""
    if not request.user.is_staff:
        return Response(
            {'erro': 'Apenas administradores podem criar tipos de serviço'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = TipoServicoSerializer(data=request.data)
    if serializer.is_valid():
        tipo = serializer.save()
        # Invalidar cache
        cache.delete('tipos_servico')
        return Response(TipoServicoSerializer(tipo).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== DOAÇÕES INDEPENDENTES ====================

@extend_schema(
    operation_id='listar_doacoes_independentes',
    summary='Listar Doações Independentes',
    description='Lista doações independentes com filtros opcionais.',
    tags=['Doações Independentes'],
    responses={200: DoacaoIndependenteListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def listar_doacoes_independentes(request):
    """Lista doações independentes com filtros"""
    queryset = DoacaoIndependente.objects.filter(ativa=True).select_related(
        'doadora', 'tipo_servico', 'localizacao'
    )
    
    # Filtros
    tipo_servico = request.GET.get('tipo_servico')
    localizacao = request.GET.get('localizacao')
    status_filter = request.GET.get('status')
    busca = request.GET.get('busca')
    
    if tipo_servico:
        queryset = queryset.filter(tipo_servico__codigo=tipo_servico)
    
    if localizacao:
        queryset = queryset.filter(localizacao__codigo=localizacao)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if busca:
        queryset = queryset.filter(
            Q(titulo__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(doadora__nome_completo__icontains=busca)
        )
    
    queryset = queryset.order_by('-data_criacao')
    
    serializer = DoacaoIndependenteListSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='criar_doacao_independente',
    summary='Criar Doação Independente',
    description='Cria uma nova doação independente (serviço contínuo).',
    tags=['Doações Independentes'],
    request=DoacaoIndependenteSerializer,
    responses={201: DoacaoIndependenteSerializer, 400: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_doacao_independente(request):
    """Cria uma nova doação independente"""
    data = request.data.copy()
    data['doadora_id'] = request.user.id
    
    serializer = DoacaoIndependenteSerializer(data=data)
    if serializer.is_valid():
        doacao = serializer.save()
        return Response(DoacaoIndependenteSerializer(doacao).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='detalhar_doacao_independente',
    summary='Detalhar Doação Independente',
    description='Retorna detalhes de uma doação independente específica.',
    tags=['Doações Independentes'],
    responses={200: DoacaoIndependenteSerializer, 404: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def detalhar_doacao_independente(request, doacao_id: int):
    """Retorna detalhes de uma doação independente"""
    try:
        doacao = DoacaoIndependente.objects.select_related(
            'doadora', 'tipo_servico', 'localizacao'
        ).get(id=doacao_id, ativa=True)
        
        serializer = DoacaoIndependenteSerializer(doacao)
        return Response(serializer.data)
    except DoacaoIndependente.DoesNotExist:
        return Response(
            {'erro': 'Doação independente não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id='atualizar_doacao_independente',
    summary='Atualizar Doação Independente',
    description='Atualiza uma doação independente (apenas o criador).',
    tags=['Doações Independentes'],
    request=DoacaoIndependenteSerializer,
    responses={200: DoacaoIndependenteSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT}
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def atualizar_doacao_independente(request, doacao_id: int):
    """Atualiza uma doação independente"""
    try:
        doacao = DoacaoIndependente.objects.get(id=doacao_id)
        
        # Verificar se o usuário é o criador
        if doacao.doadora != request.user:
            return Response(
                {'erro': 'Você só pode editar suas próprias doações independentes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DoacaoIndependenteSerializer(
            doacao, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            doacao = serializer.save()
            return Response(DoacaoIndependenteSerializer(doacao).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except DoacaoIndependente.DoesNotExist:
        return Response(
            {'erro': 'Doação independente não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id='pausar_doacao_independente',
    summary='Pausar Doação Independente',
    description='Pausa uma doação independente (apenas o criador).',
    tags=['Doações Independentes'],
    responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pausar_doacao_independente(request, doacao_id: int):
    """Pausa uma doação independente"""
    try:
        doacao = DoacaoIndependente.objects.get(id=doacao_id)
        
        if doacao.doadora != request.user:
            return Response(
                {'erro': 'Você só pode pausar suas próprias doações independentes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        doacao.pausar_servico()
        return Response({'mensagem': 'Doação independente pausada com sucesso'})
        
    except DoacaoIndependente.DoesNotExist:
        return Response(
            {'erro': 'Doação independente não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    operation_id='reativar_doacao_independente',
    summary='Reativar Doação Independente',
    description='Reativa uma doação independente pausada (apenas o criador).',
    tags=['Doações Independentes'],
    responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reativar_doacao_independente(request, doacao_id: int):
    """Reativa uma doação independente"""
    try:
        doacao = DoacaoIndependente.objects.get(id=doacao_id)
        
        if doacao.doadora != request.user:
            return Response(
                {'erro': 'Você só pode reativar suas próprias doações independentes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        doacao.reativar_servico()
        return Response({'mensagem': 'Doação independente reativada com sucesso'})
        
    except DoacaoIndependente.DoesNotExist:
        return Response(
            {'erro': 'Doação independente não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )
