from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import unicodedata
import random
import string

class TipoUsuario(models.Model):
    """Tipos de usuário do sistema"""
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome",
        help_text="Nome exibido do tipo (ex: Doadora, Beneficiária)"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Código",
        help_text="Código único gerado automaticamente do tipo"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do tipo de usuário"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se este tipo está disponível para seleção"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Tipo de Usuário"
        verbose_name_plural = "Tipos de Usuário"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gera código a partir do nome
            self.codigo = slugify(unicodedata.normalize('NFKD', self.nome).encode('ascii', 'ignore').decode('ascii'))
        super().save(*args, **kwargs)


class Genero(models.Model):
    """Gêneros/identidades de gênero"""
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome",
        help_text="Nome exibido do gênero (ex: Mulher Cis, Não-binário)"
    )
    codigo = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Código",
        help_text="Código único gerado automaticamente do gênero"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do gênero/identidade"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se esta opção está disponível para seleção"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gera código a partir do nome
            self.codigo = slugify(unicodedata.normalize('NFKD', self.nome).encode('ascii', 'ignore').decode('ascii'))
        super().save(*args, **kwargs)


class CategoriaInteresse(models.Model):
    """Categorias de interesse das pessoas"""
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome",
        help_text="Nome exibido da categoria (ex: Alimentação, Vestuário)"
    )
    codigo = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Código",
        help_text="Código único gerado automaticamente da categoria"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada da categoria"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se esta categoria está disponível para seleção"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Categoria de Interesse"
        verbose_name_plural = "Categorias de Interesse"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gera código a partir do nome
            self.codigo = slugify(unicodedata.normalize('NFKD', self.nome).encode('ascii', 'ignore').decode('ascii'))
        super().save(*args, **kwargs)


class LocalizacaoInteresse(models.Model):
    """Localizações de interesse (bairros/cidades)"""
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('bairro', 'Bairro'),
            ('cidade', 'Cidade'),
            ('regiao', 'Região'),
        ],
        default='bairro',
        verbose_name="Tipo",
        help_text="Tipo da localização"
    )
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome",
        help_text="Nome da localização"
    )
    codigo = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        verbose_name="Código",
        help_text="Código único gerado automaticamente da localização"
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade",
        help_text="Cidade da localização (se for bairro)"
    )
    estado = models.CharField(
        max_length=2,
        default='PE',
        verbose_name="Estado",
        help_text="Estado da localização"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se esta localização está disponível para seleção"
    )
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Localização de Interesse"
        verbose_name_plural = "Localizações de Interesse"
        ordering = ['estado', 'cidade', 'ordem', 'nome']

    def __str__(self):
        if self.cidade:
            return f"{self.nome} - {self.cidade}/{self.estado}"
        return f"{self.nome} - {self.estado}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gera código diferenciado por tipo para evitar conflitos
            # Para cidade: "recife-cidade"
            # Para bairro: "recife-bairro" ou apenas "boa-viagem"
            nome_normalizado = slugify(unicodedata.normalize('NFKD', self.nome).encode('ascii', 'ignore').decode('ascii'))
            
            # Se já existe com esse nome em outro tipo, adicionar sufixo
            if LocalizacaoInteresse.objects.filter(codigo=nome_normalizado).exists():
                self.codigo = f"{nome_normalizado}-{self.tipo}"
            else:
                self.codigo = nome_normalizado
        super().save(*args, **kwargs)


class Pessoa(AbstractUser):
    # Campos básicos obrigatórios
    nome_completo = models.CharField(
        max_length=100, 
        verbose_name="Nome Completo",
        help_text="Nome completo da pessoa"
    )
    cpf = models.CharField(
        max_length=14, 
        unique=True,
        verbose_name="CPF",
        help_text="CPF no formato XXX.XXX.XXX-XX",
        validators=[MinLengthValidator(11)]
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        help_text="Número de telefone com DDD"
    )
    
    # Relacionamentos com tabelas dinâmicas
    tipo_usuario = models.ForeignKey(
        TipoUsuario,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Usuário",
        help_text="Selecione seu tipo de usuário"
    )
    
    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        verbose_name="Gênero",
        help_text="Como você se identifica"
    )
    
    # Localização
    cidade = models.CharField(
        max_length=100,
        verbose_name="Cidade",
        help_text="Cidade onde você mora"
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name="Bairro",
        help_text="Bairro onde você mora"
    )
    
    # Campos obrigatórios adicionais
    nome_social = models.CharField(
        max_length=50,
        verbose_name="Nome Social",
        help_text="Nome que você gostaria de ser chamada"
    )
    mini_bio = models.TextField(
        max_length=500,
        verbose_name="Mini Biografia",
        help_text="Conte um pouco sobre você"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Foto de Perfil",
        help_text="Sua foto de perfil"
    )
    
    # Relacionamentos Many-to-Many para interesses
    categorias_interesse = models.ManyToManyField(
        CategoriaInteresse,
        verbose_name="Categorias de Interesse",
        help_text="Áreas que você tem interesse"
    )
    localizacoes_interesse = models.ManyToManyField(
        LocalizacaoInteresse,
        verbose_name="Localizações de Interesse",
        help_text="Bairros/cidades de interesse"
    )

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        ordering = ['nome_completo']

    def __str__(self):
        display_name = self.nome_social or self.nome_completo or self.username
        return f"{display_name} ({self.tipo_usuario.nome})"
    
    @property
    def nome_exibicao(self):
        """Retorna o nome que deve ser exibido publicamente"""
        return self.nome_social or self.nome_completo
    
    def get_categorias_interesse_display(self):
        """Retorna as categorias de interesse formatadas"""
        if not self.categorias_interesse.exists():
            return "Nenhuma"
        return [categoria.nome for categoria in self.categorias_interesse.all()]
    
    def get_localizacoes_interesse_display(self):
        """Retorna as localizações de interesse formatadas"""
        if not self.localizacoes_interesse.exists():
            return "Nenhuma"
        return [localizacao.nome for localizacao in self.localizacoes_interesse.all()]


class CodigoVerificacao(models.Model):
    """
    Modelo para armazenar códigos de verificação de email
    Usado para autenticação de 2 fatores e verificação de cadastro
    """
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email para o qual o código foi enviado"
    )
    codigo = models.CharField(
        max_length=6,
        verbose_name="Código",
        help_text="Código de 6 dígitos gerado aleatoriamente"
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('cadastro', 'Cadastro'),
            ('login', 'Login'),
            ('recuperacao', 'Recuperação de Senha')
        ],
        default='cadastro',
        verbose_name="Tipo",
        help_text="Finalidade do código"
    )
    usado = models.BooleanField(
        default=False,
        verbose_name="Usado",
        help_text="Se o código já foi utilizado"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_expiracao = models.DateTimeField(
        verbose_name="Data de Expiração",
        help_text="Código expira após 10 minutos"
    )
    tentativas = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentativas",
        help_text="Número de tentativas de verificação"
    )
    
    class Meta:
        verbose_name = "Código de Verificação"
        verbose_name_plural = "Códigos de Verificação"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['email', 'codigo', 'usado']),
            models.Index(fields=['data_expiracao']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.codigo} ({self.get_tipo_display()})"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            # Gerar código de 6 dígitos
            self.codigo = ''.join(random.choices(string.digits, k=6))
        if not self.data_expiracao:
            # Código expira em 10 minutos
            self.data_expiracao = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def esta_valido(self):
        """Verifica se o código ainda é válido"""
        if self.usado:
            return False, "Código já foi utilizado"
        if timezone.now() > self.data_expiracao:
            return False, "Código expirado. Solicite um novo código"
        if self.tentativas >= 3:
            return False, "Número máximo de tentativas excedido"
        return True, "Código válido"
    
    def incrementar_tentativa(self):
        """Incrementa o contador de tentativas"""
        self.tentativas += 1
        self.save(update_fields=['tentativas'])
    
    def marcar_como_usado(self):
        """Marca o código como usado"""
        self.usado = True
        self.save(update_fields=['usado'])
    
    @classmethod
    def limpar_codigos_expirados(cls):
        """Remove códigos expirados (executar periodicamente)"""
        limite = timezone.now() - timedelta(hours=24)
        cls.objects.filter(data_criacao__lt=limite).delete()
    
    @classmethod
    def gerar_codigo(cls, email, tipo='cadastro'):
        """Gera um novo código para o email especificado"""
        # Invalidar códigos anteriores do mesmo email e tipo
        cls.objects.filter(
            email=email,
            tipo=tipo,
            usado=False
        ).update(usado=True)
        
        # Criar novo código
        codigo = cls.objects.create(email=email, tipo=tipo)
        return codigo