"""
Configuração do app Core.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
    verbose_name = 'Core'

    def ready(self):
        """
        Importa signals quando o app estiver pronto.
        """
        import backend.core.signals  # noqa

