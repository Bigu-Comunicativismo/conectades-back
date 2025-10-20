from django.db import models
from django.utils import timezone
from backend.pessoas.models import Pessoa, CategoriaInteresse, LocalizacaoInteresse


class Imagem(models.Model):
    """Model para armazenar informações de imagens"""
    src = models.ImageField(
        upload_to='campanhas/imagens/',
        verbose_name="Arquivo da Imagem",
        help_text="Arquivo da imagem baseado no tipo de arquivo"
    )
    alt = models.CharField(
        max_length=200,
        verbose_name="Texto Alternativo",
        help_text="Texto alternativo para acessibilidade"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Imagem"
        verbose_name_plural = "Imagens"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Imagem: {self.alt}"


class ItemCampanha(models.Model):
    """
    Model para itens solicitados em uma campanha específica.
    Cada item pertence a UMA campanha e tem suas próprias quantidades.
    """
    campanha = models.ForeignKey(
        'Campanha',
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Campanha",
        help_text="Campanha à qual este item pertence"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome do Item",
        help_text="Nome do item solicitado (ex: 'Arroz tipo 1', 'Feijão carioca')"
    )
    quantidade_solicitada = models.PositiveIntegerField(
        verbose_name="Quantidade Solicitada",
        help_text="Quantidade total solicitada do item"
    )
    quantidade_contribuida = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade Contribuída",
        help_text="Quantidade já contribuída do item"
    )
    unidade = models.CharField(
        max_length=50,
        default="unidade",
        verbose_name="Unidade",
        help_text="Unidade de medida (kg, litros, unidades, pacotes, etc.)"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Item da Campanha"
        verbose_name_plural = "Itens das Campanhas"
        ordering = ['campanha', 'nome']
        # Não pode ter item duplicado na mesma campanha
        unique_together = [['campanha', 'nome']]

    def __str__(self):
        return f"{self.campanha.titulo} - {self.nome} ({self.quantidade_contribuida}/{self.quantidade_solicitada} {self.unidade})"

    @property
    def percentual_atingido(self):
        """Calcula o percentual de contribuição atingido"""
        if self.quantidade_solicitada == 0:
            return 0
        return (self.quantidade_contribuida / self.quantidade_solicitada) * 100


class PostAtualizacao(models.Model):
    """
    Model para posts de atualização das campanhas.
    Cada post pertence a UMA campanha específica.
    """
    campanha = models.ForeignKey(
        'Campanha',
        on_delete=models.CASCADE,
        related_name='posts_atualizacao',
        verbose_name="Campanha",
        help_text="Campanha à qual este post pertence"
    )
    mensagem = models.TextField(
        verbose_name="Mensagem",
        help_text="Conteúdo da atualização"
    )
    imagem = models.ForeignKey(
        Imagem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Imagem",
        help_text="Imagem opcional da atualização"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )

    class Meta:
        verbose_name = "Post de Atualização"
        verbose_name_plural = "Posts de Atualização"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.campanha.titulo} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"


class Organizadora(models.Model):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="perfil_organizadora"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Organizadora: {self.pessoa.nome_social or self.pessoa.nome_completo or self.pessoa.username}"


class Campanha(models.Model):
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Título da campanha"
    )
    subtitulo = models.CharField(
        max_length=300,
        default="",
        verbose_name="Subtítulo",
        help_text="Subtítulo da campanha"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada da campanha"
    )
    imagem = models.ForeignKey(
        Imagem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Imagem",
        help_text="Imagem principal da campanha"
    )
    categorias = models.ManyToManyField(
        CategoriaInteresse,
        verbose_name="Categorias",
        help_text="Categorias relacionadas à campanha"
    )
    organizadora = models.ForeignKey(
        Organizadora,
        on_delete=models.CASCADE,
        related_name="campanhas",
        verbose_name="Organizadora",
        help_text="Organizadora é a usuária que criou a campanha"
    )
    beneficiaria = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campanhas_como_beneficiaria",
        verbose_name="Beneficiária",
        help_text="Pessoa beneficiária desta campanha (opcional)"
    )
    whatsapp = models.CharField(
        max_length=20,
        default="",
        verbose_name="WhatsApp",
        help_text="Número do WhatsApp para contato"
    )
    data_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Início",
        help_text="Data e hora de início da campanha"
    )
    prazo = models.DateTimeField(
        default=timezone.now,
        verbose_name="Prazo",
        help_text="Data e hora limite da campanha"
    )
    localizacao = models.ForeignKey(
        LocalizacaoInteresse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Localização",
        help_text="Localização da campanha"
    )
    # Itens são acessíveis via reverse relation 'itens' (ItemCampanha.campanha)
    # Posts de atualização são acessíveis via reverse relation 'posts_atualizacao' (PostAtualizacao.campanha)
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a campanha está ativa"
    )

    class Meta:
        verbose_name = "Campanha"
        verbose_name_plural = "Campanhas"
        ordering = ['-data_inicio']

    def __str__(self):
        return self.titulo

    @property
    def dias_restantes(self):
        """Calcula quantos dias restam para o prazo"""
        if not self.prazo:
            return None
        agora = timezone.now()
        if self.prazo <= agora:
            return 0
        diferenca = self.prazo - agora
        return diferenca.days

    @property
    def percentual_atingido(self):
        """
        Calcula o percentual total de conclusão da campanha baseado nos itens.
        Retorna a média ponderada do percentual de cada item.
        """
        itens = self.itens.all()
        
        if not itens.exists():
            return 0
        
        total_solicitado = sum(item.quantidade_solicitada for item in itens)
        total_contribuido = sum(item.quantidade_contribuida for item in itens)
        
        if total_solicitado == 0:
            return 0
        
        return (total_contribuido / total_solicitado) * 100
    
    @property
    def total_itens(self):
        """Retorna o total de itens solicitados"""
        return self.itens.count()
    
    @property
    def itens_completos(self):
        """Retorna quantos itens já foram 100% atingidos"""
        return self.itens.filter(
            quantidade_contribuida__gte=models.F('quantidade_solicitada')
        ).count()
    
    @property
    def status_campanha(self):
        """Retorna o status visual da campanha"""
        percentual = self.percentual_atingido
        
        if percentual >= 100:
            return '🎉 Completa'
        elif percentual >= 75:
            return '🟢 Quase lá'
        elif percentual >= 50:
            return '🟡 Progredindo'
        elif percentual >= 25:
            return '🟠 Começando'
        elif percentual > 0:
            return '🔵 Iniciada'
        else:
            return '⚪ Aguardando'