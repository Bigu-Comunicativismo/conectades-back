"""
Custom exception handler para garantir que todos os erros retornem JSON
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler que sempre retorna JSON
    Previne retorno de HTML em erros 500
    """
    # Chamar o handler padrão do DRF primeiro
    response = exception_handler(exc, context)

    # Se o DRF não tratou (ex: erro 500), criar resposta JSON
    if response is None:
        # Log do erro para debug
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={'request': context.get('request')}
        )
        
        # Retornar JSON ao invés de HTML
        return Response(
            {
                'error': 'Erro interno do servidor',
                'detail': str(exc),
                'type': type(exc).__name__
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Adicionar informações extras no erro
    if hasattr(exc, 'detail'):
        response.data['error_type'] = type(exc).__name__
    
    return response

