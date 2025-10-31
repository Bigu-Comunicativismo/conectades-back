"""
Middleware customizado para o sistema Conectades.
"""

from django.core.cache import cache
from django.http import JsonResponse
import logging
import traceback

logger = logging.getLogger(__name__)


class AutoClearCorruptedCacheMiddleware:
    """
    Middleware que detecta cache corrompido e limpa automaticamente.
    
    Quando detecta erro de serialização (TypeError: Object of type Response is not JSON serializable),
    limpa o cache automaticamente e retorna erro 503 para o cliente tentar novamente.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_cleared = False

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
            
        except TypeError as e:
            error_str = str(e)
            
            # Detecta erros de serialização de cache
            if 'not JSON serializable' in error_str or 'Object of type Response' in error_str:
                
                if not self.cache_cleared:
                    logger.warning(f"🔧 Cache corrompido detectado: {error_str}")
                    logger.info("🗑️  Limpando cache automaticamente...")
                    
                    try:
                        cache.clear()
                        self.cache_cleared = True
                        logger.info("✅ Cache limpo com sucesso!")
                        
                        # Retorna 503 para o cliente tentar novamente
                        return JsonResponse({
                            'error': 'Cache corrompido detectado e limpo automaticamente',
                            'detail': 'Por favor, tente novamente em alguns segundos.',
                            'error_type': 'CacheCorruptedError',
                            'retry_after': 2
                        }, status=503)
                        
                    except Exception as cache_error:
                        logger.error(f"❌ Erro ao limpar cache: {str(cache_error)}")
                        raise
                else:
                    # Se já limpou o cache e ainda deu erro, é outro problema
                    logger.error(f"❌ Erro persistente após limpar cache: {error_str}")
                    raise
            else:
                # Outro tipo de TypeError, repassar
                raise
                
        except Exception as e:
            # Outros erros não são tratados aqui
            raise

    def process_exception(self, request, exception):
        """
        Processa exceções não capturadas no __call__.
        """
        if isinstance(exception, TypeError):
            error_str = str(exception)
            
            if 'not JSON serializable' in error_str and not self.cache_cleared:
                logger.warning(f"🔧 Cache corrompido detectado em exception: {error_str}")
                
                try:
                    cache.clear()
                    self.cache_cleared = True
                    logger.info("✅ Cache limpo via process_exception!")
                    
                    return JsonResponse({
                        'error': 'Cache corrompido detectado e limpo',
                        'detail': 'Tente novamente em alguns segundos.',
                        'error_type': 'CacheCorruptedError',
                        'retry_after': 2
                    }, status=503)
                    
                except Exception as cache_error:
                    logger.error(f"❌ Erro ao limpar cache: {str(cache_error)}")
        
        return None  # Deixa Django processar normalmente
