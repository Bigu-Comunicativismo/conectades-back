"""
Middleware customizado para o projeto Conectades
"""
from django.utils.deprecation import MiddlewareMixin


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
