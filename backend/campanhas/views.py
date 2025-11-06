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
    description='''
    Cria uma nova campanha com itens opcionais.
    
    **Multipart/Form-Data:**
    - Envie a imagem como arquivo (`imagem_arquivo`)
    - Envie itens como JSON string no campo `itens_cadastro`
    
    **Exemplo de `itens_cadastro` (JSON string):**
    ```json
    [
        {"nome": "Arroz tipo 1", "quantidade_solicitada": 50, "unidade": "kg"},
        {"nome": "Feijão carioca", "quantidade_solicitada": 30, "unidade": "kg"}
    ]
    ```
    ''',
    tags=['Campanhas'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'titulo': {'type': 'string', 'description': 'Título da campanha'},
                'subtitulo': {'type': 'string', 'description': 'Subtítulo da campanha'},
                'descricao': {'type': 'string', 'description': 'Descrição detalhada da campanha'},
                'beneficiaria_id': {'type': 'integer', 'description': 'ID da beneficiária (opcional)', 'nullable': True},
                'imagem_arquivo': {'type': 'string', 'format': 'binary', 'description': 'Arquivo de imagem (PNG, JPG, JPEG, GIF, WEBP)'},
                'imagem_alt': {'type': 'string', 'description': 'Texto alternativo da imagem', 'default': 'Imagem da campanha'},
                'categorias': {'type': 'string', 'description': 'IDs das categorias separados por vírgula (ex: "1,2,3")'},
                'whatsapp': {'type': 'string', 'description': 'WhatsApp de contato', 'nullable': True},
                'localizacao': {'type': 'integer', 'description': 'ID da localização', 'nullable': True},
                'data_inicio': {'type': 'string', 'format': 'date-time', 'description': 'Data de início da campanha'},
                'prazo': {'type': 'string', 'format': 'date-time', 'description': 'Data de término da campanha'},
                'itens_cadastro': {'type': 'string', 'description': 'JSON string com lista de itens (opcional)'},
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
    """API para criar campanha com itens opcionais. Doadoras e Beneficiárias podem criar campanhas."""
    import json
    from backend.pessoas.models import TipoUsuario
    
    # Validar Content-Type se for multipart/form-data
    content_type = request.content_type or ''
    if 'multipart/form-data' in content_type.lower():
        if 'boundary=' not in content_type.lower():
            return Response({
                'error': 'Content-Type multipart/form-data sem boundary',
                'recebido': content_type,
                'dica': 'O boundary é gerado automaticamente pelo cliente HTTP. Certifique-se de que seu cliente está configurado corretamente para enviar multipart/form-data.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    # Processar dados do request - converter para dict mutável
    data = dict(request.data)
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 Dados recebidos (tipos): categorias={type(data.get('categorias'))}, itens_cadastro={type(data.get('itens_cadastro'))}")
    logger.info(f"🔍 Valores: categorias={data.get('categorias')}, itens_cadastro={data.get('itens_cadastro')}")
    
    # Helper: Normalizar campos que vêm como lista de um elemento do multipart
    def normalize_field(value):
        """Se o valor é uma lista com um único elemento, retorna o elemento"""
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value
    
    # Normalizar todos os campos (multipart envia alguns campos como lista)
    for field in ['titulo', 'subtitulo', 'descricao', 'beneficiaria_id', 'imagem_alt', 
                  'categorias', 'whatsapp', 'localizacao', 'data_inicio', 'prazo', 'itens_cadastro']:
        if field in data:
            data[field] = normalize_field(data[field])
    
    logger.info(f"✅ Após normalização: categorias={type(data.get('categorias'))}, itens_cadastro={type(data.get('itens_cadastro'))}")
    
    # Processar categorias (se vier como string separada por vírgula)
    if 'categorias' in data and isinstance(data['categorias'], str):
        try:
            data['categorias'] = [int(cat_id.strip()) for cat_id in data['categorias'].split(',') if cat_id.strip()]
        except ValueError:
            return Response({
                'error': 'Formato inválido para categorias. Use IDs separados por vírgula (ex: "1,2,3")'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Processar itens_cadastro (se vier como JSON string)
    if 'itens_cadastro' in data and isinstance(data['itens_cadastro'], str):
        try:
            data['itens_cadastro'] = json.loads(data['itens_cadastro'])
        except json.JSONDecodeError:
            return Response({
                'error': 'Formato inválido para itens_cadastro. Use JSON válido.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar formato dos itens (se fornecidos)
    if 'itens_cadastro' in data and data['itens_cadastro']:
        if not isinstance(data['itens_cadastro'], list):
            return Response({
                'error': 'itens_cadastro deve ser uma lista/array',
                'exemplo': '[{"nome":"Item 1","quantidade_solicitada":10,"unidade":"kg"}]'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        for idx, item in enumerate(data['itens_cadastro']):
            if not isinstance(item, dict):
                return Response({
                    'error': f'Item na posição {idx} deve ser um objeto',
                    'recebido': str(item),
                    'exemplo': '{"nome":"Item 1","quantidade_solicitada":10,"unidade":"kg"}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar campos obrigatórios
            if 'nome' not in item or not item['nome']:
                return Response({
                    'error': f'Item na posição {idx} está sem o campo "nome"',
                    'item_recebido': item,
                    'campos_obrigatorios': ['nome', 'quantidade_solicitada']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if 'quantidade_solicitada' not in item:
                return Response({
                    'error': f'Item na posição {idx} está sem o campo "quantidade_solicitada"',
                    'item_recebido': item,
                    'dica': 'Use "quantidade_solicitada" (não "quantidade")',
                    'exemplo': '{"nome":"Arroz","quantidade_solicitada":50,"unidade":"kg"}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tipo do campo quantidade_solicitada
            try:
                quantidade = int(item['quantidade_solicitada'])
                if quantidade <= 0:
                    return Response({
                        'error': f'Item "{item["nome"]}" tem quantidade_solicitada inválida',
                        'recebido': item['quantidade_solicitada'],
                        'dica': 'quantidade_solicitada deve ser um número inteiro positivo'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    'error': f'Item "{item["nome"]}" tem quantidade_solicitada em formato inválido',
                    'recebido': item['quantidade_solicitada'],
                    'tipo_recebido': type(item['quantidade_solicitada']).__name__,
                    'dica': 'quantidade_solicitada deve ser um número inteiro'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"✅ Após processamento: categorias={type(data.get('categorias'))} = {data.get('categorias')}")
    logger.info(f"✅ Após processamento: itens_cadastro={type(data.get('itens_cadastro'))} = {data.get('itens_cadastro')}")
    
    # Criar ou obter perfil de organizadora automaticamente
    organizadora, created = Organizadora.objects.get_or_create(
        pessoa=request.user,
        defaults={'ativo': True}
    )
    
    data['organizadora_id'] = organizadora.id
    
    serializer = CampanhaSerializer(data=data)
    if serializer.is_valid():
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Dados válidos para criar campanha: {data.keys()}")
        campanha = serializer.save()
        logger.info(f"✅ Campanha '{campanha.titulo}' (ID: {campanha.id}) criada com sucesso!")
        
        # AUTO-PUBLICAR campanha se:
        # 1. Não há beneficiária (campanha sem beneficiária específica)
        # 2. Organizadora É a beneficiária (beneficiária criando campanha para si mesma)
        if not campanha.beneficiaria or campanha.beneficiaria == request.user:
            campanha.publicada = True
            if campanha.beneficiaria == request.user:
                campanha.beneficiaria_confirmada = True
            campanha.save(update_fields=['publicada', 'beneficiaria_confirmada'])
        
        # Invalidar cache de listagens
        cache.delete_many([
            'campanhas_all',
            f'campanhas_user_{request.user.id}'
        ])
        
        message = f'Campanha "{campanha.titulo}" criada com sucesso!'
        if created:
            message += ' 🎉 Você agora é uma Organizadora!'
        
        if campanha.publicada:
            message += ' ✅ Campanha publicada e visível para todos!'
        else:
            message += ' ⏳ Aguardando confirmação da beneficiária para publicação.'
        
        # Adicionar info sobre itens cadastrados
        total_itens = campanha.itens.count()
        if total_itens > 0:
            message += f' 📦 {total_itens} item(ns) cadastrado(s)!'
        
        return Response({
            'message': message,
            'data': CampanhaSerializer(campanha).data,
            'organizadora_criada': created,
            'publicada': campanha.publicada,
            'total_itens_cadastrados': total_itens
        }, status=status.HTTP_201_CREATED)
    
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Erros de validação ao criar campanha: {serializer.errors}")
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
    operation_id='editar_campanha',
    summary='Editar Campanha',
    description='''
    Edita uma campanha existente. Apenas a organizadora pode editar.
    
    **Multipart/Form-Data:**
    - Envie a imagem como arquivo (`imagem_arquivo`)
    - Envie categorias como string separada por vírgula (`categorias`)
    
    **Campos editáveis:**
    - titulo, subtitulo, descricao
    - imagem_arquivo, imagem_alt
    - categorias, whatsapp, localizacao
    - data_inicio, prazo
    ''',
    tags=['Campanhas'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'titulo': {'type': 'string', 'description': 'Título da campanha'},
                'subtitulo': {'type': 'string', 'description': 'Subtítulo da campanha'},
                'descricao': {'type': 'string', 'description': 'Descrição detalhada'},
                'imagem_arquivo': {'type': 'string', 'format': 'binary', 'description': 'Nova imagem (opcional)'},
                'imagem_alt': {'type': 'string', 'description': 'Texto alternativo da imagem'},
                'categorias': {'type': 'string', 'description': 'IDs das categorias separados por vírgula (ex: "1,2,3")'},
                'whatsapp': {'type': 'string', 'description': 'Número do WhatsApp'},
                'localizacao': {'type': 'integer', 'description': 'ID da localização'},
                'data_inicio': {'type': 'string', 'format': 'date-time', 'description': 'Data de início (YYYY-MM-DDTHH:MM:SS)'},
                'prazo': {'type': 'string', 'format': 'date-time', 'description': 'Prazo final (YYYY-MM-DDTHH:MM:SS)'},
            }
        }
    },
    responses={
        200: CampanhaSerializer,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def editar_campanha(request, campanha_id: int):
    """Edita uma campanha existente"""
    import json
    
    # Validar Content-Type se for multipart/form-data
    content_type = request.content_type or ''
    if 'multipart/form-data' in content_type.lower():
        if 'boundary=' not in content_type.lower():
            return Response({
                'error': 'Content-Type multipart/form-data sem boundary',
                'recebido': content_type,
                'dica': 'O boundary é gerado automaticamente pelo cliente HTTP. Certifique-se de que seu cliente está configurado corretamente para enviar multipart/form-data.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar campanha
        campanha = Campanha.objects.select_related('organizadora__pessoa').get(id=campanha_id)
        
        # Verificar se o usuário é a organizadora
        try:
            organizadora = Organizadora.objects.get(pessoa=request.user)
            if campanha.organizadora != organizadora:
                return Response({
                    'error': 'Apenas a organizadora pode editar a campanha'
                }, status=status.HTTP_403_FORBIDDEN)
        except Organizadora.DoesNotExist:
            return Response({
                'error': 'Usuário não é uma organizadora'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Processar dados do request
        data = request.data.copy()
        
        # Processar categorias (se vier como string separada por vírgula)
        if 'categorias' in data and isinstance(data['categorias'], str):
            try:
                data['categorias'] = [int(cat_id.strip()) for cat_id in data['categorias'].split(',') if cat_id.strip()]
            except ValueError:
                return Response({
                    'error': 'Formato inválido para categorias. Use IDs separados por vírgula (ex: "1,2,3")'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Não permitir alterar organizadora ou beneficiaria via edição
        data.pop('organizadora_id', None)
        data.pop('beneficiaria_id', None)
        data.pop('itens_cadastro', None)  # Itens não são editados aqui
        
        # Se houver nova imagem, criar objeto Imagem
        if 'imagem_arquivo' in data and data['imagem_arquivo']:
            from .models import Imagem
            imagem_arquivo = data.pop('imagem_arquivo')
            imagem_alt = data.pop('imagem_alt', 'Imagem da campanha')
            
            # Criar nova imagem
            imagem = Imagem.objects.create(
                src=imagem_arquivo,
                alt=imagem_alt
            )
            
            # Deletar imagem antiga (se existir)
            if campanha.imagem:
                imagem_antiga = campanha.imagem
                campanha.imagem = None
                campanha.save(update_fields=['imagem'])
                imagem_antiga.delete()
            
            # Atribuir nova imagem
            campanha.imagem = imagem
            campanha.save(update_fields=['imagem'])
        elif 'imagem_alt' in data:
            data.pop('imagem_alt')  # Remover se não há arquivo
        
        # Atualizar campanha
        serializer = CampanhaSerializer(campanha, data=data, partial=True)
        
        if serializer.is_valid():
            campanha_atualizada = serializer.save()
            
            # Atualizar categorias (many-to-many)
            if 'categorias' in data:
                campanha_atualizada.categorias.set(data['categorias'])
            
            # Invalidar cache
            cache.delete(f'campanha_detail_{campanha_id}')
            cache.delete(f'campanhas_user_{request.user.id}')
            cache.delete('campanhas_publicas')
            
            return Response({
                'message': f'Campanha "{campanha_atualizada.titulo}" atualizada com sucesso!',
                'data': CampanhaSerializer(campanha_atualizada).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Campanha.DoesNotExist:
        return Response({
            'error': 'Campanha não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    operation_id='desativar_campanha',
    summary='Desativar Campanha',
    description='Desativa uma campanha (campo ativa=False). Apenas a organizadora pode desativar.',
    tags=['Campanhas'],
    responses={
        200: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def desativar_campanha(request, campanha_id: int):
    """Desativa uma campanha"""
    try:
        # Buscar campanha
        campanha = Campanha.objects.select_related('organizadora__pessoa').get(id=campanha_id)
        
        # Verificar se o usuário é a organizadora
        try:
            organizadora = Organizadora.objects.get(pessoa=request.user)
            if campanha.organizadora != organizadora:
                return Response({
                    'error': 'Apenas a organizadora pode desativar a campanha'
                }, status=status.HTTP_403_FORBIDDEN)
        except Organizadora.DoesNotExist:
            return Response({
                'error': 'Usuário não é uma organizadora'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Desativar campanha
        campanha.ativa = False
        campanha.save(update_fields=['ativa'])
        
        # Invalidar cache
        cache.delete(f'campanha_detail_{campanha_id}')
        cache.delete(f'campanhas_user_{request.user.id}')
        cache.delete('campanhas_publicas')
        
        return Response({
            'message': f'Campanha "{campanha.titulo}" desativada com sucesso!',
            'data': CampanhaSerializer(campanha).data
        }, status=status.HTTP_200_OK)
        
    except Campanha.DoesNotExist:
        return Response({
            'error': 'Campanha não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


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


@extend_schema(
    operation_id='cadastrar_item_campanha',
    summary='Cadastrar Item em Campanha',
    description='Cadastra um novo item de doação em uma campanha específica. Apenas a organizadora pode adicionar itens.',
    tags=['Campanhas'],
    request=ItemCampanhaSerializer,
    responses={
        201: ItemCampanhaSerializer,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastrar_item_campanha(request, campanha_id: int):
    """Cadastra um novo item em uma campanha"""
    try:
        # Verificar se a campanha existe
        campanha = Campanha.objects.select_related('organizadora__pessoa').get(id=campanha_id)
        
        # Verificar se o usuário é a organizadora da campanha
        try:
            organizadora = Organizadora.objects.get(pessoa=request.user)
            if campanha.organizadora != organizadora:
                return Response({
                    'error': 'Apenas a organizadora pode adicionar itens à campanha'
                }, status=status.HTTP_403_FORBIDDEN)
        except Organizadora.DoesNotExist:
            return Response({
                'error': 'Usuário não é uma organizadora'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Preparar dados
        data = request.data.copy()
        data['campanha'] = campanha_id
        
        # Validar e criar item
        serializer = ItemCampanhaSerializer(data=data)
        if serializer.is_valid():
            item = serializer.save()
            
            # Invalidar cache da campanha
            cache.delete(f'campanha_detail_{campanha_id}')
            cache.delete(f'campanhas_user_{request.user.id}')
            
            return Response({
                'message': f'Item "{item.nome}" cadastrado com sucesso!',
                'data': ItemCampanhaSerializer(item).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Campanha.DoesNotExist:
        return Response({
            'error': 'Campanha não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


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