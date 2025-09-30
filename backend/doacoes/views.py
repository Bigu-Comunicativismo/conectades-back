from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.conf import settings
from .models import Doacao
from backend.campanhas.models import Campanha
from backend.pessoas.models import Pessoa
from .serializers import DoacaoSerializer


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

# Create your views here.
