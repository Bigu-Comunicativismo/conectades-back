import json
import logging

from django.http import QueryDict
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from .models import TipoServico, Doacao, DoacaoIndependente
from .email_service import enviar_notificacao_nova_doacao
from backend.campanhas.models import Campanha
from backend.pessoas.models import Pessoa
from .serializers import (
    TipoServicoSerializer, DoacaoSerializer, 
    DoacaoIndependenteSerializer, DoacaoIndependenteListSerializer,
    DoacaoIndependenteCreateSerializer, AtualizarStatusDoacaoSerializer
)

logger = logging.getLogger(__name__)


def _is_multipart_request(request):
    content_type = request.META.get('CONTENT_TYPE', '')
    return content_type.startswith('multipart/form-data')


def _validate_multipart_boundary(request):
    """
    Garante que requisições multipart contenham o boundary obrigatório.
    """
    content_type = request.META.get('CONTENT_TYPE', '')
    if _is_multipart_request(request) and 'boundary=' not in content_type:
        return False
    return True


def _normalize_request_data(data):
    """
    Normaliza dados vindos de multipart/form-data para evitar listas com um único valor.
    """
    if isinstance(data, QueryDict):
        data = data.copy()
        normalized = {}
        for key, values in data.lists():
            if len(values) == 1:
                normalized[key] = values[0]
            else:
                normalized[key] = values
        return normalized
    return data


def _parse_int_list(value):
    """
    Converte diferentes representações (string, lista, JSON) em uma lista de inteiros.
    """
    if value is None or value == '':
        return []

    if isinstance(value, list):
        items = value
    else:
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return []
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    items = parsed
                else:
                    items = [parsed]
            except json.JSONDecodeError:
                items = [item.strip() for item in value.split(',')]
        else:
            items = [value]

    int_items = []
    for item in items:
        if item in (None, '', []):
            continue
        if isinstance(item, list):
            raise ValueError("Lista aninhada não suportada")
        int_items.append(int(item))
    return int_items


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

        notificacao_sucesso, notificacao_msg = enviar_notificacao_nova_doacao(doacao)
        if notificacao_sucesso:
            logger.info("Notificação de nova doação enviada: %s", notificacao_msg)
        else:
            logger.info("Notificação de nova doação não enviada: %s", notificacao_msg)
        
        return Response(DoacaoSerializer(doacao).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='listar_doacoes_por_campanha',
    summary='Listar Doações por Campanha',
    description='Lista todas as doações vinculadas a uma campanha com cache.',
    tags=['Doações'],
    responses={200: DoacaoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_doacoes_por_campanha(request, campanha_id: int):
    cache_key = f'doacoes_campanha_{campanha_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        doacoes = Doacao.objects.select_related(
            'doador',
            'campanha',
            'item_campanha'
        ).filter(campanha_id=campanha_id)
        
        serializer = DoacaoSerializer(doacoes, many=True)
        cached_data = serializer.data
        
        # Cache por 15 minutos (doações mudam mais frequentemente)
        cache.set(cache_key, cached_data, settings.CACHE_TTL_SHORT)
    
    return Response(cached_data)


@extend_schema(
    operation_id='minhas_doacoes',
    summary='Minhas Doações (Doadora)',
    description='Lista as doações criadas pelo usuário atual (doadora).',
    tags=['Doações'],
    responses={200: DoacaoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_doacoes(request):
    """Lista as doações do usuário atual (doadora)"""
    doacoes = Doacao.objects.select_related(
        'campanha',
        'item_campanha',
        'doador'
    ).filter(doador=request.user).order_by('-data_doacao')
    
    serializer = DoacaoSerializer(doacoes, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='doacoes_minhas_campanhas',
    summary='Doações das Minhas Campanhas (Beneficiária)',
    description='Lista as doações das campanhas onde o usuário é beneficiária.',
    tags=['Doações'],
    responses={200: DoacaoSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doacoes_minhas_campanhas(request):
    """Lista as doações das campanhas onde o usuário é beneficiária"""
    doacoes = Doacao.objects.select_related(
        'campanha',
        'item_campanha',
        'doador'
    ).filter(campanha__beneficiaria=request.user).order_by('-data_doacao')
    
    serializer = DoacaoSerializer(doacoes, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='atualizar_status_doacao',
    summary='Atualizar Status de Doação',
    description='Permite que doadora cancele suas doações ou beneficiária atualize status e data de entrega.',
    tags=['Doações'],
    request=AtualizarStatusDoacaoSerializer,
    responses={200: DoacaoSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def atualizar_status_doacao(request, doacao_id: int):
    """
    Atualiza o status de uma doação.
    - Doadora pode cancelar suas próprias doações
    - Beneficiária pode atualizar status e data_entrega de doações de suas campanhas
    """
    try:
        doacao = Doacao.objects.select_related('campanha', 'doador').get(id=doacao_id)
        
        # Verificar permissões
        is_doadora = doacao.doador == request.user
        is_beneficiaria = doacao.campanha.beneficiaria == request.user
        is_admin = request.user.is_superuser
        
        if not (is_doadora or is_beneficiaria or is_admin):
            return Response({
                'erro': 'Você não tem permissão para editar esta doação'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar campos permitidos por tipo de usuário
        novo_status = request.data.get('status')
        nova_data_entrega = request.data.get('data_entrega')
        novas_observacoes = request.data.get('observacoes')
        
        # Doadora pode apenas cancelar
        if is_doadora and not is_admin:
            if novo_status and novo_status != 'cancelada':
                return Response({
                    'erro': 'Doadora só pode cancelar suas doações'
                }, status=status.HTTP_403_FORBIDDEN)
            if nova_data_entrega:
                return Response({
                    'erro': 'Doadora não pode alterar a data de entrega'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Atualizar campos permitidos
        if novo_status:
            doacao.status = novo_status
        
        if nova_data_entrega and (is_beneficiaria or is_admin):
            from datetime import datetime
            doacao.data_entrega = datetime.fromisoformat(nova_data_entrega)
        
        if novas_observacoes is not None:
            doacao.observacoes = novas_observacoes
        
        doacao.save()
        
        # Invalidar cache
        cache.delete(f'doacoes_campanha_{doacao.campanha.id}')
        
        serializer = DoacaoSerializer(doacao)
        return Response({
            'mensagem': 'Doação atualizada com sucesso',
            'doacao': serializer.data
        })
        
    except Doacao.DoesNotExist:
        return Response({
            'erro': 'Doação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='detalhar_doacao',
    summary='Detalhar Doação',
    description='Retorna detalhes de uma doação específica.',
    tags=['Doações'],
    responses={200: DoacaoSerializer, 404: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhar_doacao(request, doacao_id: int):
    """Retorna detalhes de uma doação"""
    try:
        doacao = Doacao.objects.select_related(
            'campanha',
            'item_campanha',
            'doador'
        ).get(id=doacao_id)
        
        # Verificar permissões
        is_doadora = doacao.doador == request.user
        is_beneficiaria = doacao.campanha.beneficiaria == request.user
        is_admin = request.user.is_superuser
        
        if not (is_doadora or is_beneficiaria or is_admin):
            return Response({
                'erro': 'Você não tem permissão para visualizar esta doação'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DoacaoSerializer(doacao)
        return Response(serializer.data)
        
    except Doacao.DoesNotExist:
        return Response({
            'erro': 'Doação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


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
def listar_tipos_servico(request):
    """Lista todos os tipos de serviço ativos com cache manual"""
    cache_key = 'tipos_servico_all'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        tipos = TipoServico.objects.filter(ativo=True).order_by('ordem', 'nome')
        serializer = TipoServicoSerializer(tipos, many=True)
        # Armazenar apenas os dados serializados (dicionário Python)
        cached_data = serializer.data
        cache.set(cache_key, cached_data, settings.CACHE_TTL)
    
    return Response(cached_data)


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
        # Invalidar cache (usar mesma chave da listagem)
        cache.delete('tipos_servico_all')
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
    busca = request.query_params.get('busca')
    categoria_param = request.query_params.get('categoria') or request.query_params.get('tipo_servico')
    localizacao = request.query_params.get('localizacao')
    status_filter = request.query_params.get('status', 'ativa')
    ordenar = request.query_params.get('ordenar', 'recente')
    ativa_param = request.query_params.get('ativa')

    queryset = DoacaoIndependente.objects.select_related(
        'doadora', 'localizacao'
    ).prefetch_related('categorias')
    
    # Filtro por status (padrão: apenas ativas)
    if status_filter == 'ativa':
        queryset = queryset.filter(status='ativa', ativa=True)
    elif status_filter == 'todas':
        pass
    else:
        queryset = queryset.filter(status=status_filter)
    
    # Filtro por flag ativa (se fornecido explicitamente)
    if ativa_param is not None:
        ativa_normalizada = ativa_param.lower()
        if ativa_normalizada in ('true', '1'):
            queryset = queryset.filter(ativa=True)
        elif ativa_normalizada in ('false', '0'):
            queryset = queryset.filter(ativa=False)

    # Filtro por categoria / tipo de serviço
    if categoria_param:
        try:
            queryset = queryset.filter(categorias__id=int(categoria_param))
        except (TypeError, ValueError):
            queryset = queryset.filter(categorias__nome__iexact=categoria_param)
    
    if localizacao:
        queryset = queryset.filter(localizacao__codigo=localizacao)
    
    if status_filter:
        # Se status=todas já tratado acima
        if status_filter not in ('todas', 'ativa'):
            queryset = queryset.filter(status=status_filter)
    
    if busca:
        queryset = queryset.filter(
            Q(titulo__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(doadora__nome_completo__icontains=busca)
        )
    
    # Ordenação
    if ordenar == 'recente':
        queryset = queryset.order_by('-data_criacao')
    elif ordenar == 'antiga':
        queryset = queryset.order_by('data_criacao')
    elif ordenar == 'inicio':
        queryset = queryset.order_by('data_inicio')
    elif ordenar == 'fim':
        queryset = queryset.order_by('data_fim')
    else:
        queryset = queryset.order_by('-data_criacao')
    
    serializer = DoacaoIndependenteListSerializer(queryset, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='criar_doacao_independente',
    summary='Criar Doação Independente',
    description='Cria uma nova doação independente (serviço contínuo).',
    tags=['Doações Independentes'],
    request=DoacaoIndependenteCreateSerializer,
    responses={201: DoacaoIndependenteSerializer, 400: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_doacao_independente(request):
    """Cria uma nova doação independente"""
    if not _validate_multipart_boundary(request):
        return Response(
            {
                'erro': 'Requisições multipart/form-data devem incluir o parâmetro boundary no header Content-Type.',
                'exemplo': 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    data = _normalize_request_data(request.data)
    if not isinstance(data, dict):
        data = dict(data)

    # Converter campos que podem chegar como string
    conversion_errors = {}

    if 'imagem_arquivo' in data and 'imagem' not in data:
        data['imagem'] = data.pop('imagem_arquivo')

    if 'localizacao' in data and isinstance(data['localizacao'], str) and data['localizacao'].strip():
        try:
            data['localizacao'] = int(data['localizacao'])
        except ValueError:
            conversion_errors['localizacao'] = ['Informe um ID numérico válido.']

    if 'categorias' in data and data['categorias'] not in (None, '', []):
        try:
            data['categorias'] = _parse_int_list(data['categorias'])
        except (ValueError, TypeError):
            conversion_errors['categorias'] = ['Informe uma lista de IDs numéricos (ex: "1,2,3").']

    if conversion_errors:
        return Response(conversion_errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = DoacaoIndependenteCreateSerializer(
        data=data,
        context={'doadora': request.user}
    )
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
            'doadora', 'localizacao'
        ).prefetch_related('categorias').get(id=doacao_id, ativa=True)
        
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

        if not _validate_multipart_boundary(request):
            return Response(
                {
                    'erro': 'Requisições multipart/form-data devem incluir o parâmetro boundary no header Content-Type.',
                    'exemplo': 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = _normalize_request_data(request.data)
        if not isinstance(data, dict):
            data = dict(data)

        conversion_errors = {}

        if 'imagem_arquivo' in data and 'imagem' not in data:
            data['imagem'] = data.pop('imagem_arquivo')

        if 'localizacao' in data and isinstance(data['localizacao'], str) and data['localizacao'].strip():
            try:
                data['localizacao'] = int(data['localizacao'])
            except ValueError:
                conversion_errors['localizacao'] = ['Informe um ID numérico válido.']

        if 'categorias' in data and data['categorias'] not in (None, '', []):
            try:
                data['categorias'] = _parse_int_list(data['categorias'])
            except (ValueError, TypeError):
                conversion_errors['categorias'] = ['Informe uma lista de IDs numéricos (ex: "1,2,3").']

        if conversion_errors:
            return Response(conversion_errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = DoacaoIndependenteSerializer(
            doacao,
            data=data,
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
    request=None,
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
    request=None,
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


@extend_schema(
    operation_id='minhas_doacoes_independentes',
    summary='Minhas Doações Independentes',
    description='Lista as doações independentes criadas pela doadora autenticada com filtros opcionais.',
    tags=['Doações Independentes'],
    responses={200: DoacaoIndependenteSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minhas_doacoes_independentes(request):
    """Lista e permite filtrar doações independentes da doadora autenticada"""
    queryset = DoacaoIndependente.objects.filter(
        doadora=request.user
    ).select_related(
        'localizacao'
    ).prefetch_related('categorias').order_by('-data_criacao')

    status_filter = request.GET.get('status')
    ativa_filter = request.GET.get('ativa')
    busca = request.GET.get('busca')

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if ativa_filter is not None:
        ativa_normalizada = ativa_filter.lower()
        if ativa_normalizada in ('true', '1'):
            queryset = queryset.filter(ativa=True)
        elif ativa_normalizada in ('false', '0'):
            queryset = queryset.filter(ativa=False)

    if busca:
        queryset = queryset.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    serializer = DoacaoIndependenteSerializer(queryset, many=True)
    return Response(serializer.data)
