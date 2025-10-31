"""
Signals para automação de tarefas do sistema.
"""

from django.core.cache import cache
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def clear_cache_after_migrate(sender, **kwargs):
    """
    Limpa o cache Redis automaticamente após executar migrations.
    
    Isso garante que dados cacheados não fiquem desatualizados
    quando há mudanças no schema do banco ou estrutura de dados.
    """
    try:
        cache.clear()
        logger.info("✅ Cache Redis limpo automaticamente após migrations")
        
        if kwargs.get('verbosity', 1) >= 2:
            print("✅ Cache Redis limpo automaticamente")
            
    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache após migrations: {str(e)}")

