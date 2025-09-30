from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from django.conf import settings
from .models import Organizadora, Campanha
from .serializers import OrganizadoraSerializer, CampanhaSerializer

@extend_schema(
    operation_id='criar_campanha',
    summary='Criar Campanha',
    description='Cria uma nova campanha. A organizadora é preenchida automaticamente com o usuário atual.',
    tags=['Campanhas'],
    request=CampanhaSerializer,
    responses={
        201: CampanhaSerializer,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_campanha(request):
    """API para criar campanha com organizadora preenchida automaticamente"""
    data = request.data.copy()
    
    # Preencher organizadora automaticamente com o usuário atual
    try:
        organizadora = Organizadora.objects.get(pessoa=request.user)
        data['organizadora_id'] = organizadora.id
    except Organizadora.DoesNotExist:
        # Criar perfil de organizadora se não existir
        organizadora = Organizadora.objects.create(pessoa=request.user)
        data['organizadora_id'] = organizadora.id
    
    serializer = CampanhaSerializer(data=data)
    if serializer.is_valid():
        campanha = serializer.save()
        
        # Invalidar cache de listagens
        cache.delete_many([
            'campanhas_all',
            f'campanhas_user_{request.user.id}',
            f'campanhas_beneficiaria_{request.user.id}'
        ])
        
        return Response({
            'message': f'Campanha "{campanha.titulo}" criada com sucesso!',
            'data': CampanhaSerializer(campanha).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id='listar_campanhas',
    summary='Listar Todas as Campanhas',
    description='Lista todas as campanhas do sistema com cache e otimizações.',
    tags=['Campanhas'],
    responses={
        200: CampanhaSerializer(many=True),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(settings.CACHE_TTL)  # Cache por 1 hora
def listar_campanhas(request):
    """API para listar campanhas com cache e otimizações"""
    cache_key = 'campanhas_all'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # Query otimizada com select_related e prefetch_related
        campanhas = Campanha.objects.select_related(
            'organizadora__pessoa',
            'beneficiaria'
        ).prefetch_related(
            'doacoes'
        ).all()
        
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
                'doacoes'
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
    operation_id='campanhas_beneficiaria',
    summary='Campanhas como Beneficiária',
    description='Lista as campanhas onde o usuário atual é beneficiária com cache.',
    tags=['Campanhas'],
    responses={
        200: CampanhaSerializer(many=True),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campanhas_beneficiaria(request):
    """API para listar campanhas onde o usuário é beneficiária com cache"""
    cache_key = f'campanhas_beneficiaria_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        campanhas = Campanha.objects.select_related(
            'organizadora__pessoa',
            'beneficiaria'
        ).prefetch_related(
            'doacoes'
        ).filter(beneficiaria=request.user)
        
        serializer = CampanhaSerializer(campanhas, many=True)
        cached_data = serializer.data
        
        # Cache por 30 minutos
        cache.set(cache_key, cached_data, settings.CACHE_TTL_USER)
    
    return Response(cached_data)