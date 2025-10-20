from django.core.management.base import BaseCommand
from backend.doacoes.models import TipoServico


class Command(BaseCommand):
    help = 'Cria tipos de serviço padrão para doações independentes'

    def handle(self, *args, **options):
        # Tipos de Serviço
        tipos_servico = [
            {
                'nome': 'Saúde',
                'codigo': 'saude',
                'descricao': 'Serviços de saúde e atendimento médico',
                'icone': 'fas fa-stethoscope',
                'cor': '#dc3545',
                'ordem': 1
            },
            {
                'nome': 'Jurídico',
                'codigo': 'juridico',
                'descricao': 'Serviços jurídicos e consultoria legal',
                'icone': 'fas fa-gavel',
                'cor': '#6f42c1',
                'ordem': 2
            },
            {
                'nome': 'Educação',
                'codigo': 'educacao',
                'descricao': 'Serviços educacionais e ensino',
                'icone': 'fas fa-graduation-cap',
                'cor': '#007bff',
                'ordem': 3
            },
            {
                'nome': 'Técnico',
                'codigo': 'tecnico',
                'descricao': 'Serviços técnicos e manutenção',
                'icone': 'fas fa-tools',
                'cor': '#28a745',
                'ordem': 4
            },
            {
                'nome': 'Social',
                'codigo': 'social',
                'descricao': 'Serviços sociais e assistência',
                'icone': 'fas fa-heart',
                'cor': '#e83e8c',
                'ordem': 5
            },
            {
                'nome': 'Psicológico',
                'codigo': 'psicologico',
                'descricao': 'Serviços de apoio psicológico',
                'icone': 'fas fa-brain',
                'cor': '#fd7e14',
                'ordem': 6
            },
            {
                'nome': 'Beleza e Estética',
                'codigo': 'beleza',
                'descricao': 'Serviços de beleza e estética',
                'icone': 'fas fa-cut',
                'cor': '#20c997',
                'ordem': 7
            },
            {
                'nome': 'Outro',
                'codigo': 'outro',
                'descricao': 'Outros tipos de serviço',
                'icone': 'fas fa-cog',
                'cor': '#6c757d',
                'ordem': 8
            }
        ]

        # Criar tipos de serviço
        for tipo_data in tipos_servico:
            tipo, created = TipoServico.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Criado tipo de serviço: {tipo.nome}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de serviço já existe: {tipo.nome}')
                )

        self.stdout.write(
            self.style.SUCCESS('Tipos padrão criados com sucesso!')
        )
