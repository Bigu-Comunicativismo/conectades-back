"""
Comando Django para carregar todas as localizações da Região Metropolitana do Recife
Uso: python manage.py carregar_localizacoes_rmr
"""

from django.core.management.base import BaseCommand
from backend.pessoas.models import LocalizacaoInteresse


class Command(BaseCommand):
    help = 'Carrega cidades e bairros da Região Metropolitana do Recife'

    # 15 Municípios da Região Metropolitana do Recife
    CIDADES_RMR = [
        'Abreu e Lima',
        'Araçoiaba',
        'Cabo de Santo Agostinho',
        'Camaragibe',
        'Goiana',
        'Igarassu',
        'Ipojuca',
        'Itamaracá',
        'Itapissuma',
        'Jaboatão dos Guararapes',
        'Moreno',
        'Olinda',
        'Paulista',
        'Recife',
        'São Lourenço da Mata',
    ]

    # 94 Bairros Oficiais de Recife
    # Fonte: Lei Municipal nº 16.293/1997 e atualizações
    BAIRROS_RECIFE = [
        'Aflitos', 'Afogados', 'Água Fria', 'Alto do Mandu', 'Alto José Bonifácio',
        'Alto José do Pinho', 'Alto Santa Terezinha', 'Apipucos', 'Areias', 'Arruda',
        'Barro', 'Beberibe', 'Boa Viagem', 'Boa Vista', 'Bomba do Hemetério',
        'Bongi', 'Brasília Teimosa', 'Brejo da Guabiraba', 'Brejo de Beberibe', 'Cabanga',
        'Caxangá', 'Campina do Barreto', 'Campo Grande', 'Casa Amarela', 'Casa Forte',
        'Cavaleiro', 'Cidade Universitária', 'Coelhos', 'Cohab', 'Coqueiral',
        'Cordeiro', 'Córrego do Jenipapo', 'Curado', 'Derby', 'Dois Irmãos',
        'Dois Unidos', 'Encruzilhada', 'Engenho do Meio', 'Espinheiro', 'Estância',
        'Fundão', 'Graças', 'Guabiraba', 'Hipódromo', 'Ibura',
        'Ilha do Leite', 'Ilha do Retiro', 'Ilha Joana Bezerra', 'Imbiribeira', 'Ipsep',
        'Iputinga', 'Jardim São Paulo', 'Jiquiá', 'Jordão', 'Linha do Tiro',
        'Macaxeira', 'Madalena', 'Mangueira', 'Mangabeira', 'Monteiro',
        'Morro da Conceição', 'Mustardinha', 'Nova Descoberta', 'Paissandu', 'Parnamirim',
        'Peixinhos', 'Pena', 'Pina', 'Poço da Panela', 'Ponto de Parada',
        'Porto da Madeira', 'Recife', 'Rosarinho', 'San Martin', 'Sancho',
        'Santana', 'Santo Amaro', 'Santo Antônio', 'São José', 'Sítio dos Pintos',
        'Sítio Wanderley', 'Soledade', 'Sucupira', 'Tamarineira', 'Tejipió',
        'Torre', 'Torreão', 'Torrões', 'Várzea', 'Vasco da Gama', 'Zumbi',
    ]
    
    # Bairros de Olinda
    BAIRROS_OLINDA = [
        'Águas Compridas', 'Alto da Bondade', 'Alto da Conquista', 'Amaro Branco',
        'Bairro Novo', 'Barbalho', 'Bonsucesso', 'Bultrins',
        'Caixa d\'Água', 'Campo do São Bento', 'Capunga', 'Carmo',
        'Casa Caiada', 'Cidade Tabajara', 'Fragoso', 'Guadalupe',
        'Jardim Atlântico', 'Monte', 'Mouraria', 'Ouro Preto',
        'Passarinho', 'Peixinhos', 'Prado', 'Quadramares',
        'Rio Doce', 'Santa Tereza', 'Santana', 'São Benedito',
        'Salgadinho', 'Socorro', 'Tabajaras', 'Varadouro', 'Vila Popular',
    ]
    
    # Bairros de Jaboatão dos Guararapes
    BAIRROS_JABOATAO = [
        'Barra de Jangada', 'Behengue', 'Candeias', 'Cavaleiro',
        'Comportas', 'Curado', 'Engenho Velho', 'Floriano',
        'Guararapes', 'Jardim Jordão', 'Jardim Piedade', 'Manoel Belo',
        'Marcos Freire', 'Muribeca', 'Prazeres', 'Piedade',
        'Porta Larga', 'Praias de Piedade', 'Santa Luzia', 'Santo Aleixo',
        'Severiano Moraes Filho', 'Socorro', 'Sucupira', 'Zumbi',
    ]
    
    # Bairros de São Lourenço da Mata
    BAIRROS_SAO_LOURENCO = [
        'Caetés I', 'Caetés II', 'Caetés III', 'Centro',
        'Engenho Tapado', 'Jardim Brasil', 'Jardim Marrocos',
        'Laranjeiras', 'Matias de Albuquerque', 'Monteiro',
        'Passarinho', 'Pitanga', 'Pixete', 'Quinta do Maracujá',
        'Salgadinho', 'São João', 'Tiúma', 'Vila Romana',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpar localizações existentes antes de carregar',
        )
        parser.add_argument(
            '--apenas-cidades',
            action='store_true',
            help='Carregar apenas cidades',
        )
        parser.add_argument(
            '--apenas-bairros',
            action='store_true',
            help='Carregar apenas bairros',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌍 Carregando localizações da RMR...'))

        cidades_criadas = 0
        bairros_criados = 0
        
        # Carregar cidades
        if not options['apenas_bairros']:
            if options['limpar']:
                LocalizacaoInteresse.objects.filter(tipo='cidade', estado='PE').delete()
            
            self.stdout.write('📍 Carregando cidades da RMR...')
            for ordem, cidade in enumerate(sorted(self.CIDADES_RMR), start=1):
                obj, created = LocalizacaoInteresse.objects.get_or_create(
                    nome=cidade,
                    tipo='cidade',
                    defaults={
                        'cidade': cidade,
                        'estado': 'PE',
                        'ordem': ordem,
                        'ativo': True,
                    }
                )
                if created:
                    cidades_criadas += 1
        
        # Carregar bairros
        if not options['apenas_cidades']:
            if options['limpar']:
                LocalizacaoInteresse.objects.filter(tipo='bairro').delete()
            
            # Carregar bairros de cada cidade
            bairros_por_cidade = [
                ('Recife', self.BAIRROS_RECIFE),
                ('Olinda', self.BAIRROS_OLINDA),
                ('Jaboatão dos Guararapes', self.BAIRROS_JABOATAO),
                ('São Lourenço da Mata', self.BAIRROS_SAO_LOURENCO),
            ]
            
            for cidade, bairros in bairros_por_cidade:
                self.stdout.write(f'🏘️  Carregando bairros de {cidade}...')
                # Remover duplicatas e ordenar
                bairros_unicos = sorted(set(bairros))
                
                for ordem, bairro in enumerate(bairros_unicos, start=1):
                    obj, created = LocalizacaoInteresse.objects.get_or_create(
                        nome=bairro,
                        tipo='bairro',
                        cidade=cidade,
                        defaults={
                            'estado': 'PE',
                            'ordem': ordem,
                            'ativo': True,
                        }
                    )
                    if created:
                        bairros_criados += 1

        # Resumo
        total_cidades = LocalizacaoInteresse.objects.filter(tipo='cidade', estado='PE').count()
        total_bairros = LocalizacaoInteresse.objects.filter(tipo='bairro', estado='PE').count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 Resumo:'))
        self.stdout.write(f'  ✅ Cidades criadas: {cidades_criadas}')
        self.stdout.write(f'  ✅ Bairros criados: {bairros_criados}')
        self.stdout.write(f'  📍 Total cidades: {total_cidades}')
        self.stdout.write(f'  🏘️  Total bairros: {total_bairros}')
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Total: {total_cidades + total_bairros} localizações!'))

