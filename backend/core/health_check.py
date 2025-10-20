"""
Health check endpoint para monitoramento do sistema
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import sys


def health_check(request):
    """
    Endpoint de health check para monitoramento.
    Verifica:
    - Database connection
    - Cache (Redis)
    - Python version
    - Django running
    
    Returns 200 OK se tudo estiver funcionando
    Returns 500 Internal Server Error se houver problemas
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Check 1: Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'ok',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Check 2: Cache (Redis)
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        
        if cache_value == 'ok':
            health_status['checks']['cache'] = {
                'status': 'ok',
                'message': 'Cache connection successful'
            }
        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['cache'] = {
                'status': 'error',
                'message': 'Cache read/write failed'
            }
    except Exception as e:
        # Cache não é crítico em desenvolvimento
        health_status['checks']['cache'] = {
            'status': 'warning',
            'message': f'Cache unavailable: {str(e)}'
        }
    
    # Check 3: Python Version
    health_status['checks']['python'] = {
        'status': 'ok',
        'version': sys.version.split()[0]
    }
    
    # Check 4: Django
    import django
    health_status['checks']['django'] = {
        'status': 'ok',
        'version': django.get_version()
    }
    
    # Determinar status code
    status_code = 200 if health_status['status'] == 'healthy' else 500
    
    return JsonResponse(health_status, status=status_code)


def simple_health_check(request):
    """
    Health check simples que apenas retorna OK.
    Útil para load balancers que só precisam saber se está online.
    """
    return JsonResponse({'status': 'ok'}, status=200)

