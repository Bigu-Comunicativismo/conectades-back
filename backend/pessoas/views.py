from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import authenticate
from .models import Pessoa
from .serializers import PessoaSerializer
from backend.campanhas.models import Organizadora

@extend_schema(
    operation_id='cadastro_beneficiaria',
    summary='Cadastrar Beneficiária',
    description='Cadastra uma nova beneficiária no sistema. O tipo é preenchido automaticamente como "beneficiaria".',
    tags=['Cadastro de Pessoas'],
    request=PessoaSerializer,
    responses={
        201: PessoaSerializer,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastro_beneficiaria(request):
    """API para cadastro de beneficiária com tipo preenchido automaticamente"""
    from .models import TipoUsuario
    
    data = request.data.copy()
    tipo_beneficiaria = TipoUsuario.objects.get(codigo='beneficiaria')
    data['tipo_usuario'] = tipo_beneficiaria.id  # Preencher automaticamente
    
    serializer = PessoaSerializer(data=data)
    if serializer.is_valid():
        pessoa = serializer.save()
        return Response({
            'message': f'Beneficiária {pessoa.nome_completo or pessoa.username} cadastrada com sucesso!',
            'data': PessoaSerializer(pessoa).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id='cadastro_doadora',
    summary='Cadastrar Doadora',
    description='Cadastra uma nova doadora no sistema. O tipo é preenchido automaticamente como "doadora".',
    tags=['Cadastro de Pessoas'],
    request=PessoaSerializer,
    responses={
        201: PessoaSerializer,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastro_doadora(request):
    """API para cadastro de doadora com tipo preenchido automaticamente"""
    from .models import TipoUsuario
    
    data = request.data.copy()
    tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
    data['tipo_usuario'] = tipo_doadora.id  # Preencher automaticamente
    
    serializer = PessoaSerializer(data=data)
    if serializer.is_valid():
        pessoa = serializer.save()
        return Response({
            'message': f'Doadora {pessoa.nome_completo or pessoa.username} cadastrada com sucesso!',
            'data': PessoaSerializer(pessoa).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    operation_id='cadastro_organizadora',
    summary='Cadastrar Organizadora',
    description='Cadastra uma nova organizadora no sistema. O tipo é preenchido automaticamente como "doadora" e um perfil de organizadora é criado.',
    tags=['Cadastro de Pessoas'],
    request=PessoaSerializer,
    responses={
        201: PessoaSerializer,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastro_organizadora(request):
    """API para cadastro de organizadora (uma doadora com perfil de organizadora)"""
    from .models import TipoUsuario
    
    data = request.data.copy()
    # Organizadora é uma Doadora com perfil de organizadora
    tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
    data['tipo_usuario'] = tipo_doadora.id
    
    serializer = PessoaSerializer(data=data)
    if serializer.is_valid():
        pessoa = serializer.save()
        
        # Criar perfil de organizadora (uma doadora que pode criar campanhas)
        organizadora = Organizadora.objects.create(pessoa=pessoa)
        
        return Response({
            'message': f'Organizadora {pessoa.nome_completo or pessoa.username} cadastrada com sucesso!',
            'data': PessoaSerializer(pessoa).data,
            'organizadora_id': organizadora.id,
            'info': 'Organizadora é uma doadora com permissão para criar campanhas'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
