"""
Comando Django para popular o banco de dados com dados fake para testes.
Cria usuários, campanhas, doações e doações independentes.

Uso:
    python manage.py populate_fake_data
    python manage.py populate_fake_data --usuarios 20 --campanhas 15
    python manage.py populate_fake_data --limpar  # Remove dados fake antes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import random

from backend.pessoas.models import (
    Pessoa, TipoUsuario, Genero, CategoriaInteresse, LocalizacaoInteresse
)
from backend.campanhas.models import (
    Campanha, ItemCampanha, PostAtualizacao, Organizadora, SolicitacaoBeneficiaria
)
from backend.doacoes.models import Doacao, DoacaoIndependente, TipoServico


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fake para testes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuarios',
            type=int,
            default=15,
            help='Número de usuários a criar (divide entre organizadoras, beneficiárias e doadoras)'
        )
        parser.add_argument(
            '--campanhas',
            type=int,
            default=10,
            help='Número de campanhas a criar'
        )
        parser.add_argument(
            '--doacoes-independentes',
            type=int,
            default=8,
            help='Número de doações independentes a criar'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove todos os dados fake antes de criar novos'
        )

    def handle(self, *args, **options):
        num_usuarios = options['usuarios']
        num_campanhas = options['campanhas']
        num_doacoes_independentes = options['doacoes_independentes']
        limpar = options['limpar']

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🚀 POPULANDO BANCO DE DADOS COM DADOS FAKE'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        if limpar:
            self.limpar_dados_fake()

        with transaction.atomic():
            # 1. Verificar dados iniciais necessários
            self.verificar_dados_iniciais()
            
            # 2. Criar usuários
            usuarios = self.criar_usuarios(num_usuarios)
            
            # 3. Criar campanhas com beneficiárias confirmadas
            campanhas = self.criar_campanhas(num_campanhas, usuarios)
            
            # 4. Criar doações para campanhas
            self.criar_doacoes(campanhas, usuarios)
            
            # 5. Criar doações independentes
            self.criar_doacoes_independentes(num_doacoes_independentes, usuarios)
            
            # 6. Resumo final
            self.mostrar_resumo(usuarios, campanhas)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ DADOS FAKE CRIADOS COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

    def limpar_dados_fake(self):
        """Remove todos os dados fake (exceto superusers)"""
        self.stdout.write(self.style.WARNING('🗑️  Limpando dados fake...'))
        
        # Remove doações
        Doacao.objects.all().delete()
        DoacaoIndependente.objects.all().delete()
        
        # Remove campanhas (cascade irá deletar itens e posts)
        Campanha.objects.all().delete()
        
        # Remove solicitações órfãs
        SolicitacaoBeneficiaria.objects.all().delete()
        
        # Remove organizadoras
        Organizadora.objects.all().delete()
        
        # Remove usuários não-superuser
        Pessoa.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('   ✅ Dados fake removidos\n'))

    def verificar_dados_iniciais(self):
        """Verifica se os dados iniciais necessários existem"""
        self.stdout.write('📋 Verificando dados iniciais...')
        
        # Verificar TipoUsuario
        tipos = ['organizadora', 'beneficiaria', 'doadora']
        for tipo in tipos:
            TipoUsuario.objects.get_or_create(
                codigo=tipo,
                defaults={'nome': tipo.capitalize()}
            )
        
        # Verificar Genero
        generos = [
            ('feminino', 'Feminino'),
            ('masculino', 'Masculino'),
            ('outro', 'Outro'),
        ]
        for codigo, nome in generos:
            Genero.objects.get_or_create(codigo=codigo, defaults={'nome': nome})
        
        # Verificar TipoServico
        tipos_servico = [
            ('Saúde', 'Serviços de saúde', 'fas fa-stethoscope', '#dc3545'),
            ('Educação', 'Serviços educacionais', 'fas fa-graduation-cap', '#007bff'),
            ('Jurídico', 'Serviços jurídicos', 'fas fa-gavel', '#6c757d'),
            ('Transporte', 'Serviços de transporte', 'fas fa-car', '#ffc107'),
            ('Tecnologia', 'Serviços de TI', 'fas fa-laptop', '#17a2b8'),
        ]
        for nome, desc, icone, cor in tipos_servico:
            TipoServico.objects.get_or_create(
                nome=nome,
                defaults={
                    'descricao': desc,
                    'icone': icone,
                    'cor': cor,
                    'ativo': True,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('   ✅ Dados iniciais verificados\n'))

    def criar_usuarios(self, num_usuarios):
        """Cria usuários fake"""
        self.stdout.write(f'👥 Criando {num_usuarios} usuários...')
        
        # Buscar tipos e gêneros
        tipo_org = TipoUsuario.objects.get(codigo='organizadora')
        tipo_benef = TipoUsuario.objects.get(codigo='beneficiaria')
        tipo_doadora = TipoUsuario.objects.get(codigo='doadora')
        genero_fem = Genero.objects.get(codigo='feminino')
        genero_masc = Genero.objects.get(codigo='masculino')
        
        nomes_fem = [
            'Maria Silva', 'Ana Santos', 'Juliana Costa', 'Fernanda Lima',
            'Carla Souza', 'Patricia Oliveira', 'Beatriz Alves', 'Camila Rodrigues',
            'Larissa Ferreira', 'Mariana Pereira', 'Gabriela Martins', 'Amanda Rocha'
        ]
        nomes_masc = [
            'João Silva', 'Carlos Santos', 'Pedro Costa', 'Lucas Lima',
            'Rafael Souza', 'Bruno Oliveira', 'Marcos Alves', 'Felipe Rodrigues'
        ]
        
        usuarios = {
            'organizadoras': [],
            'beneficiarias': [],
            'doadoras': []
        }
        
        # Dividir usuários: 25% org, 35% benef, 40% doadoras
        num_org = max(3, int(num_usuarios * 0.25))
        num_benef = max(4, int(num_usuarios * 0.35))
        num_doadoras = max(5, num_usuarios - num_org - num_benef)
        
        cpf_counter = 10000000000
        
        # Criar organizadoras
        for i in range(num_org):
            username = f'org{i+1}'
            nome = random.choice(nomes_fem + nomes_masc)
            cpf = str(cpf_counter).zfill(11)
            cpf_counter += 1
            
            user, created = Pessoa.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@conectades.fake',
                    'nome_completo': nome,
                    'nome_exibicao': nome.split()[0],
                    'cpf': cpf,
                    'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'genero': random.choice([genero_fem, genero_masc]),
                    'tipo_usuario': tipo_org,
                    'password': make_password('teste123'),
                    'is_active': True,
                }
            )
            
            # Criar perfil Organizadora
            org, _ = Organizadora.objects.get_or_create(pessoa=user)
            usuarios['organizadoras'].append(user)
        
        # Criar beneficiárias
        for i in range(num_benef):
            username = f'benef{i+1}'
            nome = random.choice(nomes_fem)
            cpf = str(cpf_counter).zfill(11)
            cpf_counter += 1
            
            user, created = Pessoa.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@conectades.fake',
                    'nome_completo': nome,
                    'nome_exibicao': nome.split()[0],
                    'cpf': cpf,
                    'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'genero': genero_fem,
                    'tipo_usuario': tipo_benef,
                    'password': make_password('teste123'),
                    'is_active': True,
                }
            )
            usuarios['beneficiarias'].append(user)
        
        # Criar doadoras
        for i in range(num_doadoras):
            username = f'doadora{i+1}'
            nome = random.choice(nomes_fem + nomes_masc)
            cpf = str(cpf_counter).zfill(11)
            cpf_counter += 1
            
            user, created = Pessoa.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@conectades.fake',
                    'nome_completo': nome,
                    'nome_exibicao': nome.split()[0],
                    'cpf': cpf,
                    'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'genero': random.choice([genero_fem, genero_masc]),
                    'tipo_usuario': tipo_doadora,
                    'password': make_password('teste123'),
                    'is_active': True,
                }
            )
            usuarios['doadoras'].append(user)
        
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {len(usuarios["organizadoras"])} organizadoras, '
            f'{len(usuarios["beneficiarias"])} beneficiárias, '
            f'{len(usuarios["doadoras"])} doadoras\n'
        ))
        
        return usuarios

    def criar_campanhas(self, num_campanhas, usuarios):
        """Cria campanhas com beneficiárias já confirmadas"""
        self.stdout.write(f'📢 Criando {num_campanhas} campanhas...')
        
        titulos = [
            'Alimentos para Família Silva',
            'Roupas de Inverno - Comunidade Santa Maria',
            'Material Escolar para Crianças',
            'Fraldas e Produtos para Bebês',
            'Cestas Básicas - Bairro Vila Nova',
            'Móveis para Casa Nova',
            'Medicamentos Essenciais',
            'Material de Limpeza e Higiene',
            'Livros e Material Didático',
            'Equipamentos para Cozinha Comunitária',
            'Cobertores e Agasalhos',
            'Utensílios Domésticos',
            'Produtos de Higiene Pessoal',
            'Alimentação para Mês Inteiro',
            'Enxoval para Recém-Nascido',
        ]
        
        itens_possiveis = [
            ('Arroz', 'kg', 10, 50),
            ('Feijão', 'kg', 5, 30),
            ('Óleo', 'litros', 3, 15),
            ('Açúcar', 'kg', 5, 20),
            ('Macarrão', 'pacotes', 10, 40),
            ('Leite', 'litros', 10, 30),
            ('Fraldas', 'pacotes', 5, 20),
            ('Sabonete', 'unidades', 10, 50),
            ('Pasta de dente', 'unidades', 5, 30),
            ('Shampoo', 'unidades', 5, 20),
            ('Cobertor', 'unidades', 2, 10),
            ('Roupa infantil', 'peças', 10, 30),
            ('Caderno', 'unidades', 10, 50),
            ('Lápis', 'caixas', 5, 20),
        ]
        
        campanhas = []
        organizadoras = usuarios['organizadoras']
        beneficiarias = usuarios['beneficiarias']
        
        localizacoes = list(LocalizacaoInteresse.objects.all())
        
        for i in range(num_campanhas):
            # Escolher organizadora e beneficiária
            organizadora_user = random.choice(organizadoras)
            organizadora = Organizadora.objects.get(pessoa=organizadora_user)
            beneficiaria = random.choice(beneficiarias)
            
            # Criar campanha
            titulo = random.choice(titulos)
            campanha = Campanha.objects.create(
                titulo=f'{titulo} #{i+1}',
                subtitulo=f'Ajude com {titulo.lower()}',
                descricao=f'Campanha para ajudar com {titulo.lower()}. Sua doação fará toda a diferença!',
                organizadora=organizadora,
                beneficiaria=beneficiaria,
                beneficiaria_confirmada=True,  # JÁ CONFIRMADA!
                publicada=True,  # JÁ PUBLICADA!
                ativa=True,
                whatsapp='(81) 99999-9999',
                data_inicio=timezone.now() - timedelta(days=random.randint(1, 30)),
                prazo=timezone.now() + timedelta(days=random.randint(15, 90)),
                localizacao=random.choice(localizacoes) if localizacoes else None,
            )
            
            # Adicionar categorias (ManyToMany)
            if categorias:
                campanha.categorias.add(*random.sample(categorias, min(2, len(categorias))))
            
            # Criar solicitação já aceita
            SolicitacaoBeneficiaria.objects.get_or_create(
                campanha=campanha,
                beneficiaria=beneficiaria,
                defaults={
                    'organizadora': organizadora,
                    'status': 'aceita',
                    'mensagem_organizadora': f'Gostaria de ajudá-la com esta campanha.',
                    'mensagem_resposta': 'Aceito com gratidão!',
                    'data_resposta': timezone.now() - timedelta(days=random.randint(1, 10))
                }
            )
            
            # Criar 3-6 itens por campanha
            num_itens = random.randint(3, 6)
            itens_campanha = random.sample(itens_possiveis, min(num_itens, len(itens_possiveis)))
            
            for nome, unidade, qtd_min, qtd_max in itens_campanha:
                quantidade_solicitada = random.randint(qtd_min, qtd_max)
                ItemCampanha.objects.create(
                    campanha=campanha,
                    nome=nome,
                    quantidade_solicitada=quantidade_solicitada,
                    quantidade_contribuida=0,  # Será atualizado pelas doações
                    unidade=unidade,
                )
            
            # Criar post de atualização
            if random.random() > 0.5:
                PostAtualizacao.objects.create(
                    campanha=campanha,
                    mensagem='🎉 Campanha iniciada! Agradecemos a todos que já demonstraram interesse em ajudar. Vamos juntos fazer a diferença!'
                )
            
            campanhas.append(campanha)
        
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {len(campanhas)} campanhas criadas (todas publicadas e confirmadas)\n'
        ))
        
        return campanhas

    def criar_doacoes(self, campanhas, usuarios):
        """Cria doações para as campanhas"""
        self.stdout.write('🎁 Criando doações...')
        
        doadoras = usuarios['doadoras']
        total_doacoes = 0
        
        status_opcoes = ['pendente', 'confirmada', 'entregue']
        pesos_status = [0.2, 0.5, 0.3]  # 20% pendente, 50% confirmada, 30% entregue
        
        for campanha in campanhas:
            # Cada campanha recebe 2-8 doações
            num_doacoes = random.randint(2, 8)
            itens = list(campanha.itens.all())
            
            for _ in range(num_doacoes):
                doadora = random.choice(doadoras)
                item = random.choice(itens)
                
                # Quantidade entre 1 e 30% da solicitada
                max_qtd = max(1, int(item.quantidade_solicitada * 0.3))
                quantidade = random.randint(1, max_qtd)
                
                status = random.choices(status_opcoes, weights=pesos_status)[0]
                
                doacao = Doacao.objects.create(
                    campanha=campanha,
                    doador=doadora,
                    item_campanha=item,
                    quantidade=quantidade,
                    unidade=item.unidade,
                    status=status,
                    observacoes=f'Doação de {quantidade} {item.unidade} de {item.nome}',
                )
                
                # Se entregue, definir data de entrega
                if status == 'entregue':
                    doacao.data_entrega = timezone.now() - timedelta(
                        days=random.randint(1, 15)
                    )
                    doacao.save()
                
                total_doacoes += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {total_doacoes} doações criadas\n'
        ))

    def criar_doacoes_independentes(self, num_doacoes_independentes, usuarios):
        """Cria doações independentes (serviços)"""
        self.stdout.write(f'💼 Criando {num_doacoes_independentes} doações independentes...')
        
        doadoras = usuarios['doadoras']
        tipos_servico = list(TipoServico.objects.filter(ativo=True))
        categorias = list(CategoriaInteresse.objects.all())
        localizacoes = list(LocalizacaoInteresse.objects.all())
        
        descricoes = [
            'Ofereço aulas particulares de reforço escolar.',
            'Faço entregas de mercadorias gratuitamente.',
            'Ofereço consultas médicas gratuitas.',
            'Disponibilizo serviço de tradução de documentos.',
            'Ofereço aulas de informática básica.',
            'Faço pequenos consertos domésticos.',
            'Ofereço corte de cabelo gratuito.',
            'Disponibilizo consultoria jurídica gratuita.',
            'Ofereço aulas de música para crianças.',
            'Faço design gráfico para materiais de divulgação.',
        ]
        
        for _ in range(num_doacoes_independentes):
            doadora = random.choice(doadoras)
            tipo_servico = random.choice(tipos_servico)
            titulo = f"{tipo_servico.nome} voluntário(a)"
            
            doacao = DoacaoIndependente.objects.create(
                doadora=doadora,
                titulo=titulo,
                descricao=random.choice(descricoes),
                data_inicio=timezone.now(),
                data_fim=timezone.now() + timedelta(days=random.randint(30, 120)),
                localizacao=random.choice(localizacoes) if localizacoes else None,
                status='ativa',
                ativa=True,
            )
            
            if tipos_servico:
                doacao.categorias.set(random.sample(tipos_servico, min(2, len(tipos_servico))))
        
        self.stdout.write(self.style.SUCCESS(
            f'   ✅ {num_doacoes_independentes} doações independentes criadas\n'
        ))

    def mostrar_resumo(self, usuarios, campanhas):
        """Mostra resumo dos dados criados"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO DOS DADOS CRIADOS'))
        self.stdout.write('='*70 + '\n')
        
        # Usuários
        self.stdout.write(self.style.HTTP_INFO('👥 USUÁRIOS:'))
        self.stdout.write(f'   • Organizadoras: {len(usuarios["organizadoras"])}')
        self.stdout.write(f'   • Beneficiárias: {len(usuarios["beneficiarias"])}')
        self.stdout.write(f'   • Doadoras: {len(usuarios["doadoras"])}')
        self.stdout.write(f'   • TOTAL: {sum(len(v) for v in usuarios.values())}\n')
        
        # Campanhas
        total_itens = sum(c.itens.count() for c in campanhas)
        self.stdout.write(self.style.HTTP_INFO('📢 CAMPANHAS:'))
        self.stdout.write(f'   • Campanhas criadas: {len(campanhas)}')
        self.stdout.write(f'   • Todas publicadas: ✅')
        self.stdout.write(f'   • Todas com beneficiária confirmada: ✅')
        self.stdout.write(f'   • Total de itens: {total_itens}\n')
        
        # Doações
        total_doacoes = Doacao.objects.count()
        doacoes_por_status = {
            'pendente': Doacao.objects.filter(status='pendente').count(),
            'confirmada': Doacao.objects.filter(status='confirmada').count(),
            'entregue': Doacao.objects.filter(status='entregue').count(),
        }
        self.stdout.write(self.style.HTTP_INFO('🎁 DOAÇÕES:'))
        self.stdout.write(f'   • Total: {total_doacoes}')
        self.stdout.write(f'   • Pendentes: {doacoes_por_status["pendente"]}')
        self.stdout.write(f'   • Confirmadas: {doacoes_por_status["confirmada"]}')
        self.stdout.write(f'   • Entregues: {doacoes_por_status["entregue"]}\n')
        
        # Doações Independentes
        total_doacoes_ind = DoacaoIndependente.objects.count()
        disponiveis = DoacaoIndependente.objects.filter(ativa=True).count()
        self.stdout.write(self.style.HTTP_INFO('💼 DOAÇÕES INDEPENDENTES:'))
        self.stdout.write(f'   • Total: {total_doacoes_ind}')
        self.stdout.write(f'   • Disponíveis: {disponiveis}\n')
        
        # Credenciais
        self.stdout.write(self.style.WARNING('🔑 CREDENCIAIS DE ACESSO:'))
        self.stdout.write('   • Senha para todos os usuários: teste123')
        self.stdout.write('   • Exemplos de usuários:')
        self.stdout.write('     - org1, org2, org3 (organizadoras)')
        self.stdout.write('     - benef1, benef2, benef3 (beneficiárias)')
        self.stdout.write('     - doadora1, doadora2, doadora3 (doadoras)\n')

