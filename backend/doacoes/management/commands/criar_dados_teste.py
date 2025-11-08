from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from backend.pessoas.models import Pessoa, TipoUsuario, CategoriaInteresse, LocalizacaoInteresse
from backend.campanhas.models import Campanha, Organizadora, Imagem, ItemCampanha, PostAtualizacao
from backend.doacoes.models import TipoServico, Doacao, DoacaoIndependente
import random


class Command(BaseCommand):
    help = 'Cria dados fake para testes locais'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Criando dados de teste...'))
        
        # Criar usuários de teste
        usuarios = self.criar_usuarios()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(usuarios)} usuários criados'))
        
        # Criar campanhas de teste
        campanhas = self.criar_campanhas(usuarios)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(campanhas)} campanhas criadas'))
        
        # Criar doações de teste
        doacoes = self.criar_doacoes(usuarios, campanhas)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(doacoes)} doações criadas'))
        
        # Criar doações independentes de teste
        doacoes_independentes = self.criar_doacoes_independentes(usuarios)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(doacoes_independentes)} doações independentes criadas'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Dados de teste criados com sucesso!'))
        self.stdout.write(self.style.SUCCESS('\n📊 Resumo:'))
        self.stdout.write(f'   • {len(usuarios)} usuários')
        self.stdout.write(f'   • {len(campanhas)} campanhas')
        self.stdout.write(f'   • {len(doacoes)} doações')
        self.stdout.write(f'   • {len(doacoes_independentes)} doações independentes')

    def criar_usuarios(self):
        """Cria usuários de teste"""
        usuarios = []
        
        # Pegar categorias, localizações e gêneros existentes
        from backend.pessoas.models import Genero
        categorias = list(CategoriaInteresse.objects.all()[:3])
        localizacoes = list(LocalizacaoInteresse.objects.all()[:5])
        generos = list(Genero.objects.all())
        
        if not categorias or not localizacoes:
            self.stdout.write(self.style.WARNING('⚠ Categorias ou localizações não encontradas. Execute primeiro as migrações.'))
            return []
        
        if not generos:
            self.stdout.write(self.style.WARNING('⚠ Gêneros não encontrados. Criando gêneros padrão...'))
            generos = [
                Genero.objects.create(nome='Feminino', codigo='feminino'),
                Genero.objects.create(nome='Masculino', codigo='masculino'),
                Genero.objects.create(nome='Outro', codigo='outro'),
            ]
        
        # Dados de exemplo
        dados_usuarios = [
            {
                'email': 'maria.silva@exemplo.com',
                'nome_completo': 'Maria Silva',
                'cpf': '12345678901',
                'telefone': '11987654321',
                'cidade': 'Recife',
                'tipo': 'doadora'
            },
            {
                'email': 'joao.santos@exemplo.com',
                'nome_completo': 'João Santos',
                'cpf': '23456789012',
                'telefone': '11976543210',
                'cidade': 'Recife',
                'tipo': 'organizadora'
            },
            {
                'email': 'ana.costa@exemplo.com',
                'nome_completo': 'Ana Costa',
                'cpf': '34567890123',
                'telefone': '11965432109',
                'cidade': 'Recife',
                'tipo': 'doadora'
            },
            {
                'email': 'pedro.oliveira@exemplo.com',
                'nome_completo': 'Pedro Oliveira',
                'cpf': '45678901234',
                'telefone': '11954321098',
                'cidade': 'Recife',
                'tipo': 'organizadora'
            },
            {
                'email': 'julia.ferreira@exemplo.com',
                'nome_completo': 'Julia Ferreira',
                'cpf': '56789012345',
                'telefone': '11943210987',
                'cidade': 'Recife',
                'tipo': 'doadora'
            }
        ]
        
        for dados in dados_usuarios:
            # Verificar se já existe
            if Pessoa.objects.filter(email=dados['email']).exists():
                usuario = Pessoa.objects.get(email=dados['email'])
                usuarios.append(usuario)
                continue
            
            # Criar tipo de usuário
            tipo_usuario, _ = TipoUsuario.objects.get_or_create(codigo=dados['tipo'])
            
            # Criar usuário
            usuario = Pessoa.objects.create_user(
                username=dados['email'].split('@')[0],
                email=dados['email'],
                password='senha123',
                nome_completo=dados['nome_completo'],
                cpf=dados['cpf'],
                telefone=dados['telefone'],
                cidade=dados['cidade'],
                bairro=random.choice(localizacoes),
                tipo_usuario=tipo_usuario,
                genero=random.choice(generos)
            )
            
            # Adicionar categorias de interesse
            usuario.categorias_interesse.set(random.sample(categorias, min(2, len(categorias))))
            
            # Adicionar localizações de interesse
            usuario.localizacoes_interesse.set(random.sample(localizacoes, min(3, len(localizacoes))))
            
            usuarios.append(usuario)
        
        return usuarios

    def criar_campanhas(self, usuarios):
        """Cria campanhas de teste"""
        campanhas = []
        
        if not usuarios:
            return []
        
        # Filtrar organizadoras
        organizadoras = [u for u in usuarios if u.tipo_usuario and u.tipo_usuario.codigo == 'organizadora']
        
        if not organizadoras:
            self.stdout.write(self.style.WARNING('⚠ Nenhuma organizadora encontrada'))
            return []
        
        categorias = list(CategoriaInteresse.objects.all()[:3])
        localizacoes = list(LocalizacaoInteresse.objects.all()[:5])
        
        dados_campanhas = [
            {
                'titulo': 'Campanha de Alimentos para Famílias Carentes',
                'subtitulo': 'Ajude famílias em situação de vulnerabilidade',
                'descricao': 'Nossa campanha visa arrecadar alimentos não perecíveis para distribuir entre famílias carentes da região. Cada doação faz a diferença!',
                'whatsapp': '11987654321',
                'prazo_dias': 30
            },
            {
                'titulo': 'Roupas de Inverno para Moradores de Rua',
                'subtitulo': 'Doe agasalhos e ajude quem mais precisa',
                'descricao': 'Com a chegada do inverno, precisamos de roupas quentes para distribuir entre moradores em situação de rua.',
                'whatsapp': '11976543210',
                'prazo_dias': 45
            },
            {
                'titulo': 'Brinquedos para o Dia das Crianças',
                'subtitulo': 'Faça uma criança feliz!',
                'descricao': 'Estamos arrecadando brinquedos novos e usados em bom estado para distribuir no Dia das Crianças.',
                'whatsapp': '11965432109',
                'prazo_dias': 20
            }
        ]
        
        for dados in dados_campanhas:
            organizadora_pessoa = random.choice(organizadoras)
            organizadora, _ = Organizadora.objects.get_or_create(pessoa=organizadora_pessoa)
            
            campanha = Campanha.objects.create(
                titulo=dados['titulo'],
                subtitulo=dados['subtitulo'],
                descricao=dados['descricao'],
                organizadora=organizadora,
                whatsapp=dados['whatsapp'],
                data_inicio=timezone.now(),
                prazo=timezone.now() + timedelta(days=dados['prazo_dias']),
                localizacao=random.choice(localizacoes) if localizacoes else None,
                ativa=True
            )
            
            # Adicionar categorias
            if categorias:
                campanha.categorias.set(random.sample(categorias, min(2, len(categorias))))
            
            # Adicionar itens solicitados (agora são criados diretamente vinculados à campanha)
            self.criar_itens_campanha(campanha)
            
            campanhas.append(campanha)
        
        return campanhas

    def criar_itens_campanha(self, campanha):
        """Cria itens para uma campanha"""
        itens_dados = [
            {'nome': 'Arroz tipo 1', 'quantidade': 100, 'unidade': 'kg'},
            {'nome': 'Feijão carioca', 'quantidade': 80, 'unidade': 'kg'},
            {'nome': 'Óleo de soja', 'quantidade': 50, 'unidade': 'litros'},
            {'nome': 'Açúcar refinado', 'quantidade': 60, 'unidade': 'kg'},
            {'nome': 'Leite em pó', 'quantidade': 40, 'unidade': 'latas'},
        ]
        
        for dados in random.sample(itens_dados, min(3, len(itens_dados))):
            ItemCampanha.objects.create(
                campanha=campanha,
                nome=dados['nome'],
                quantidade_solicitada=dados['quantidade'],
                quantidade_contribuida=random.randint(0, dados['quantidade'] // 2),
                unidade=dados['unidade']
            )

    def criar_doacoes(self, usuarios, campanhas):
        """Cria doações de teste"""
        doacoes = []
        
        if not usuarios or not campanhas:
            return []
        
        # Doadores
        doadores = [u for u in usuarios if u.tipo_usuario and u.tipo_usuario.codigo == 'doadora']
        
        if not doadores:
            doadores = usuarios[:3]  # Usar qualquer usuário
        
        # Criar doações para cada campanha
        for campanha in campanhas:
            itens_campanha = list(ItemCampanha.objects.filter(campanha=campanha))
            
            if not itens_campanha:
                continue
            
            # Criar 2-4 doações por campanha
            num_doacoes = random.randint(2, min(4, len(itens_campanha)))
            
            for _ in range(num_doacoes):
                item = random.choice(itens_campanha)
                
                # Quantidade entre 10% e 50% do solicitado
                quantidade_max = int(item.quantidade_solicitada * 0.5)
                quantidade_min = int(item.quantidade_solicitada * 0.1)
                quantidade = random.randint(max(1, quantidade_min), max(1, quantidade_max))
                
                doacao = Doacao.objects.create(
                    campanha=campanha,
                    doador=random.choice(doadores),
                    item_campanha=item,
                    quantidade=quantidade,
                    unidade=item.unidade,
                    status=random.choice(['pendente', 'confirmada', 'entregue']),
                    data_doacao=timezone.now() - timedelta(days=random.randint(1, 30)),
                    observacoes=f'Doação de {quantidade} {item.unidade} de {item.nome}'
                )
                doacoes.append(doacao)
        
        return doacoes

    def criar_doacoes_independentes(self, usuarios):
        """Cria doações independentes de teste"""
        doacoes = []
        
        if not usuarios:
            return []
        
        tipos_servico = list(TipoServico.objects.filter(ativo=True))
        categorias = list(CategoriaInteresse.objects.all()[:3])
        localizacoes = list(LocalizacaoInteresse.objects.all()[:5])
        
        if not tipos_servico:
            self.stdout.write(self.style.WARNING('⚠ Nenhum tipo de serviço encontrado'))
            return []
        
        # Doadores
        doadores = [u for u in usuarios if u.tipo_usuario and u.tipo_usuario.codigo == 'doadora']
        
        if not doadores:
            doadores = usuarios[:3]
        
        dados_doacoes = [
            {
                'titulo': 'Atendimento Odontológico Voluntário',
                'descricao': 'Consultas odontológicas gratuitas para pessoas de baixa renda.',
                'tipo_nome': 'Saúde'
            },
            {
                'titulo': 'Consultoria Jurídica Pro Bono',
                'descricao': 'Atendimento jurídico gratuito para questões trabalhistas e previdenciárias.',
                'tipo_nome': 'Jurídico'
            },
            {
                'titulo': 'Aulas de Reforço Escolar',
                'descricao': 'Aulas de matemática e português para crianças do ensino fundamental.',
                'tipo_nome': 'Educação'
            },
            {
                'titulo': 'Cortes de Cabelo Gratuitos',
                'descricao': 'Cortes de cabelo gratuitos para pessoas em situação de vulnerabilidade.',
                'tipo_nome': 'Beleza'
            }
        ]
        
        for dados in dados_doacoes:
            tipo_servico_principal = TipoServico.objects.filter(nome=dados['tipo_nome']).first()
            if not tipo_servico_principal:
                tipo_servico_principal = random.choice(tipos_servico)
            
            doacao = DoacaoIndependente.objects.create(
                doadora=random.choice(doadores),
                titulo=dados['titulo'],
                descricao=dados['descricao'],
                data_inicio=timezone.now(),
                data_fim=timezone.now() + timedelta(days=90),
                localizacao=random.choice(localizacoes) if localizacoes else None,
                status='ativa',
                ativa=True
            )
            
            # Adicionar categorias (tipos de serviço)
            categorias_tipos = set([tipo_servico_principal])
            if len(tipos_servico) > 1:
                categorias_tipos.update(random.sample(tipos_servico, min(2, len(tipos_servico))))
            doacao.categorias.set(list(categorias_tipos))
            
            doacoes.append(doacao)
        
        return doacoes

