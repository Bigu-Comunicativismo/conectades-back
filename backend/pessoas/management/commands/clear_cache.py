"""
Comando management para limpar o cache Redis.

Uso:
    python manage.py clear_cache
    
No Docker:
    docker exec conectades-backend-1 python backend/manage.py clear_cache
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Limpa todo o cache Redis do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keys',
            type=str,
            help='Limpar apenas chaves específicas (separadas por vírgula)',
        )

    def handle(self, *args, **options):
        keys = options.get('keys')
        
        if keys:
            # Limpar chaves específicas
            key_list = [k.strip() for k in keys.split(',')]
            self.stdout.write(f'🗑️  Limpando {len(key_list)} chave(s) específica(s)...')
            
            deleted_count = 0
            for key in key_list:
                if cache.delete(key):
                    deleted_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ {key}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  {key} (não encontrada)'))
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✨ {deleted_count}/{len(key_list)} chave(s) removida(s) com sucesso!')
            )
        else:
            # Limpar todo o cache
            self.stdout.write('🗑️  Limpando TODO o cache Redis...')
            
            try:
                cache.clear()
                self.stdout.write(
                    self.style.SUCCESS('✨ Cache limpo com sucesso!')
                )
                self.stdout.write(
                    self.style.SUCCESS('\n📝 Dica: O cache será reconstruído automaticamente nas próximas requisições.')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao limpar cache: {str(e)}')
                )
                raise

