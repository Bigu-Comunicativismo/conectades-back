from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
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
    beneficiaria_confirmada = models.BooleanField(
        default=False,
        verbose_name="Beneficiária Confirmada",
        help_text="Se a beneficiária aceitou ser associada a esta campanha"
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
        help_text="Se a campanha está ativa e visível publicamente"
    )
    publicada = models.BooleanField(
        default=False,
        verbose_name="Publicada",
        help_text="Se a campanha foi publicada e está visível para doadores. Só pode ser True se beneficiária confirmar OU se não houver beneficiária."
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
    
    @property
    def pode_ser_publicada(self):
        """Verifica se a campanha pode ser publicada"""
        # Campanha sem beneficiária pode ser publicada
        if not self.beneficiaria:
            return True
        
        # Campanha com beneficiária só pode ser publicada se confirmada
        return self.beneficiaria_confirmada
    
    @property
    def status_publicacao(self):
        """Retorna o status de publicação da campanha"""
        if self.publicada:
            return '✅ Publicada'
        elif not self.beneficiaria:
            return '⏳ Rascunho (sem beneficiária)'
        elif self.beneficiaria_confirmada:
            return '⏳ Pronta para publicar'
        else:
            return '⏳ Aguardando confirmação da beneficiária'
    
    def publicar(self):
        """Publica a campanha se as condições forem atendidas"""
        if self.pode_ser_publicada:
            self.publicada = True
            self.save(update_fields=['publicada'])
            return True, "Campanha publicada com sucesso!"
        else:
            return False, "Campanha não pode ser publicada: beneficiária ainda não confirmou"
    
    def despublicar(self):
        """Despublica a campanha"""
        self.publicada = False
        self.save(update_fields=['publicada'])
        return True, "Campanha despublicada com sucesso!"


class SolicitacaoBeneficiaria(models.Model):
    """
    Model para gerenciar solicitações de associação de beneficiárias a campanhas.
    Quando uma organizadora adiciona uma beneficiária a uma campanha,
    uma solicitação é criada e a beneficiária precisa aceitar ou recusar.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aceita', 'Aceita'),
        ('recusada', 'Recusada'),
    ]
    
    campanha = models.ForeignKey(
        Campanha,
        on_delete=models.CASCADE,
        related_name='solicitacoes_beneficiaria',
        verbose_name="Campanha",
        help_text="Campanha para a qual a beneficiária foi indicada"
    )
    beneficiaria = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name='solicitacoes_campanha',
        verbose_name="Beneficiária",
        help_text="Pessoa que foi indicada como beneficiária"
    )
    organizadora = models.ForeignKey(
        Organizadora,
        on_delete=models.CASCADE,
        related_name='solicitacoes_enviadas',
        verbose_name="Organizadora",
        help_text="Organizadora que criou a solicitação"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status",
        help_text="Status da solicitação"
    )
    mensagem_organizadora = models.TextField(
        blank=True,
        default="",
        verbose_name="Mensagem da Organizadora",
        help_text="Mensagem da organizadora explicando por que a beneficiária foi escolhida"
    )
    mensagem_resposta = models.TextField(
        blank=True,
        default="",
        verbose_name="Mensagem de Resposta",
        help_text="Mensagem da beneficiária ao aceitar ou recusar"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_resposta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Resposta",
        help_text="Data em que a beneficiária respondeu à solicitação"
    )
    
    class Meta:
        verbose_name = "Solicitação de Beneficiária"
        verbose_name_plural = "Solicitações de Beneficiária"
        ordering = ['-data_criacao']
        # Apenas uma solicitação pendente por campanha-beneficiária
        unique_together = [['campanha', 'beneficiaria']]
    
    def __str__(self):
        return f"{self.campanha.titulo} → {self.beneficiaria.nome_exibicao} ({self.status})"
    
    @property
    def status_display(self):
        """Retorna status com emoji"""
        emojis = {
            'pendente': '⏳',
            'aceita': '✅',
            'recusada': '❌'
        }
        return f"{emojis.get(self.status, '❓')} {self.get_status_display()}"
    
    def aceitar(self, mensagem=""):
        """Aceita a solicitação e confirma a beneficiária na campanha"""
        self.status = 'aceita'
        self.mensagem_resposta = mensagem
        self.data_resposta = timezone.now()
        self.save()
        
        # Confirmar a beneficiária na campanha
        self.campanha.beneficiaria_confirmada = True
        self.campanha.save(update_fields=['beneficiaria_confirmada'])
        
        # Agora a campanha pode ser publicada
        # A organizadora pode publicá-la manualmente ou podemos publicar automaticamente
        # Por enquanto, apenas marcamos como pronta para publicação
    
    def recusar(self, mensagem=""):
        """Recusa a solicitação e remove a beneficiária da campanha"""
        self.status = 'recusada'
        self.mensagem_resposta = mensagem
        self.data_resposta = timezone.now()
        self.save()
        
        # Remover a beneficiária da campanha
        self.campanha.beneficiaria = None
        self.campanha.beneficiaria_confirmada = False
        self.campanha.save(update_fields=['beneficiaria', 'beneficiaria_confirmada'])


# ==================== SINAIS DJANGO ====================

@receiver(post_save, sender=Campanha)
def criar_solicitacao_beneficiaria(sender, instance, created, **kwargs):
    """
    Cria uma solicitação quando uma beneficiária é adicionada a uma campanha.
    Envia email de notificação para a beneficiária.
    """
    # Não processar se é uma nova campanha ou se não há beneficiária
    if not instance.beneficiaria:
        return
    
    # Verificar se a beneficiária mudou (comparando com o estado anterior)
    if not created:
        try:
            campanha_anterior = Campanha.objects.get(pk=instance.pk)
            # Se a beneficiária não mudou, não fazer nada
            if campanha_anterior.beneficiaria == instance.beneficiaria:
                return
        except Campanha.DoesNotExist:
            pass
    
    # Verificar se já existe uma solicitação pendente
    solicitacao_existente = SolicitacaoBeneficiaria.objects.filter(
        campanha=instance,
        beneficiaria=instance.beneficiaria,
        status='pendente'
    ).first()
    
    if not solicitacao_existente:
        # Criar nova solicitação
        solicitacao = SolicitacaoBeneficiaria.objects.create(
            campanha=instance,
            beneficiaria=instance.beneficiaria,
            organizadora=instance.organizadora,
            mensagem_organizadora=f"A organizadora {instance.organizadora.pessoa.nome_exibicao} gostaria de associar você como beneficiária da campanha '{instance.titulo}'."
        )
        
        # Marcar campanha como não confirmada
        if instance.beneficiaria_confirmada:
            instance.beneficiaria_confirmada = False
            instance.save(update_fields=['beneficiaria_confirmada'])
        
        # Enviar email de notificação
        try:
            from backend.pessoas.email_service import enviar_notificacao_solicitacao_beneficiaria
            sucesso, mensagem = enviar_notificacao_solicitacao_beneficiaria(solicitacao)
            if sucesso:
                print(f"✅ {mensagem}")
            else:
                print(f"⚠️ {mensagem}")
        except Exception as e:
            print(f"❌ Erro ao enviar notificação por email: {e}")