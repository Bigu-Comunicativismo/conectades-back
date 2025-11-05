"""
Middleware customizado para o projeto Conectades
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Desabilita verificação CSRF apenas para endpoints da API (/api/*).
    
    Isso permite que:
    - APIs REST funcionem sem CSRF token (padrão para APIs)
    - Django Admin continue protegido com CSRF
    - Swagger UI funcione sem problemas
    
    CSRF é importante para formulários web tradicionais, mas não é
    necessário para APIs REST que usam JWT/Token authentication.
    """
    
    def process_request(self, request):
        """
        Marca requisições para /api/* como isentas de CSRF.
        """
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)


class AutoClearCorruptedCacheMiddleware(MiddlewareMixin):
    """
    Middleware que detecta e limpa automaticamente cache corrompido.
    
    Quando ocorre um erro de unpickling do cache (dados corrompidos),
    este middleware limpa o cache automaticamente e permite que a
    requisição continue normalmente.
    
    Isso evita que o sistema fique inacessível devido a cache corrompido.
    """
    
    def process_exception(self, request, exception):
        """
        Intercepta exceções e limpa o cache se for erro de unpickling.
        """
        # Verifica se é um erro de cache corrompido
        if isinstance(exception, (ValueError, EOFError, TypeError)):
            error_msg = str(exception).lower()
            
            # Detecta erros relacionados a pickle/cache
            if any(keyword in error_msg for keyword in ['pickle', 'unpickl', 'marshal', 'cache']):
                logger.warning(
                    f"Cache corrompido detectado: {exception}. "
                    f"Limpando cache automaticamente..."
                )
                
                try:
                    # Limpa todo o cache
                    cache.clear()
                    logger.info("✅ Cache limpo com sucesso!")
                    
                    # Retorna None para que o Django continue processando
                    # a requisição normalmente (sem o dado em cache)
                    return None
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao limpar cache: {e}")
        
        # Se não for erro de cache, deixa o Django tratar normalmente
        return None
