from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from backend.pessoas.models import Pessoa, LocalizacaoInteresse
from backend.campanhas.models import Imagem, Organizadora


class TipoServico(models.Model):
    """Model para gerenciar tipos de serviço dinamicamente"""
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome",
        help_text="Nome do tipo de serviço (ex: Saúde, Jurídico, Educação)"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do tipo de serviço"
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ícone",
        help_text="Classe do ícone (ex: fas fa-stethoscope, fas fa-gavel)"
    )
    cor = models.CharField(
        max_length=7,
        default="#28a745",
        verbose_name="Cor",
        help_text="Cor em hexadecimal (ex: #28a745)"
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
        verbose_name = "Tipo de Serviço"
        verbose_name_plural = "Tipos de Serviço"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Doacao(models.Model):
    """
    Model para doações - representa o que está sendo doado (serviço, objeto, etc.)
    """
    campanha = models.ForeignKey(
        'campanhas.Campanha',
        on_delete=models.CASCADE,
        related_name="doacoes",
        verbose_name="Campanha",
        help_text="Campanha para a qual esta doação é destinada"
    )
    doador = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="doacoes_feitas",
        verbose_name="Doador",
        help_text="Pessoa que está fazendo a doação"
    )
    item_campanha = models.ForeignKey(
        'campanhas.ItemCampanha',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="doacoes",
        verbose_name="Item da Campanha",
        help_text="Item específico da campanha que está sendo contribuído (opcional)"
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade",
        help_text="Quantidade do item/serviço sendo doado"
    )
    unidade = models.CharField(
        max_length=50,
        default="unidade",
        verbose_name="Unidade",
        help_text="Unidade de medida (kg, litros, horas, etc.)"
    )
    imagem = models.ForeignKey(
        'campanhas.Imagem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Imagem",
        help_text="Imagem do item/serviço sendo doado"
    )
    data_doacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Doação",
        help_text="Data e hora em que a doação foi registrada"
    )
    data_entrega = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Entrega",
        help_text="Data prevista ou efetiva da entrega"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('confirmada', 'Confirmada'),
            ('entregue', 'Entregue'),
            ('cancelada', 'Cancelada'),
        ],
        default='pendente',
        verbose_name="Status",
        help_text="Status atual da doação"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações adicionais sobre a doação"
    )

    class Meta:
        verbose_name = "Doação"
        verbose_name_plural = "Doações"
        ordering = ['-data_doacao']

    def __str__(self):
        item_nome = self.item_campanha.nome if self.item_campanha else "Doação genérica"
        return f"{self.doador.nome_exibicao} → {item_nome} ({self.quantidade} {self.unidade})"

    @property
    def descricao_completa(self):
        """Retorna uma descrição completa da doação"""
        item_nome = self.item_campanha.nome if self.item_campanha else "Doação genérica"
        return f"{self.quantidade} {self.unidade} de {item_nome} para {self.campanha.titulo}"

    @property
    def status_display(self):
        """Retorna o status formatado"""
        status_map = {
            'pendente': '⏳ Pendente',
            'confirmada': '✅ Confirmada',
            'entregue': '🎉 Entregue',
            'cancelada': '❌ Cancelada',
        }
        return status_map.get(self.status, self.status)

    def confirmar_doacao(self):
        """Confirma a doação"""
        self.status = 'confirmada'
        self.save(update_fields=['status'])

    def marcar_como_entregue(self):
        """Marca a doação como entregue"""
        self.status = 'entregue'
        self.data_entrega = timezone.now()
        self.save(update_fields=['status', 'data_entrega'])

    def cancelar_doacao(self):
        """Cancela a doação"""
        self.status = 'cancelada'
        self.save(update_fields=['status'])
    
    def save(self, *args, **kwargs):
        """
        Atualiza automaticamente a quantidade contribuída do item da campanha
        quando o status da doação muda
        """
        is_new = self.pk is None
        old_doacao = None
        
        if not is_new:
            # Buscar estado anterior da doação
            try:
                old_doacao = Doacao.objects.get(pk=self.pk)
            except Doacao.DoesNotExist:
                old_doacao = None
        
        if self.item_campanha:
            # Status que contam como contribuição
            status_contribuicao = ['confirmada', 'entregue']
            
            # Verificar se deve incrementar (nova doação confirmada/entregue)
            if is_new and self.status in status_contribuicao:
                self.item_campanha.quantidade_contribuida += self.quantidade
                self.item_campanha.save(update_fields=['quantidade_contribuida'])
            
            # Verificar mudanças de status em doações existentes
            elif old_doacao and old_doacao.status != self.status:
                old_status_contribuia = old_doacao.status in status_contribuicao
                new_status_contribui = self.status in status_contribuicao
                
                if not old_status_contribuia and new_status_contribui:
                    # Status mudou para contribuição: incrementar
                    self.item_campanha.quantidade_contribuida += self.quantidade
                    self.item_campanha.save(update_fields=['quantidade_contribuida'])
                
                elif old_status_contribuia and not new_status_contribui:
                    # Status mudou de contribuição para não-contribuição: decrementar
                    self.item_campanha.quantidade_contribuida = max(0, self.item_campanha.quantidade_contribuida - self.quantidade)
                    self.item_campanha.save(update_fields=['quantidade_contribuida'])
                
                elif old_status_contribuia and new_status_contribui and old_doacao.quantidade != self.quantidade:
                    # Quantidade mudou em doação já confirmada: ajustar diferença
                    diferenca = self.quantidade - old_doacao.quantidade
                    self.item_campanha.quantidade_contribuida = max(0, self.item_campanha.quantidade_contribuida + diferenca)
                    self.item_campanha.save(update_fields=['quantidade_contribuida'])
        
        super().save(*args, **kwargs)


class DoacaoIndependente(models.Model):
    """
    Model para doações independentes - serviços contínuos oferecidos por doadoras
    Ex: Dentista que atende 2x por mês, Advogado que faz consultas voluntárias
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    # Informações básicas
    doadora = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="doacoes_independentes",
        verbose_name="Doadora",
        help_text="Pessoa que está oferecendo o serviço"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título do Serviço",
        help_text="Ex: 'Atendimento Odontológico Voluntário'"
    )
    subtitulo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Subtítulo",
        help_text="Subtítulo do serviço (opcional)"
    )
    descricao = models.TextField(
        verbose_name="Descrição",
        help_text="Descrição detalhada do serviço oferecido"
    )
    # Detalhes do serviço
    data_inicio = models.DateTimeField(
        verbose_name="Data de Início",
        help_text="Quando o serviço começará a ser oferecido"
    )
    data_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Fim",
        help_text="Quando o serviço terminará (opcional)"
    )
    
    localizacao = models.ForeignKey(
        LocalizacaoInteresse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Localização",
        help_text="Onde o serviço será prestado"
    )
    endereco_detalhado = models.TextField(
        blank=True,
        null=True,
        verbose_name="Endereço Detalhado",
        help_text="Endereço específico ou instruções de localização"
    )
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="WhatsApp",
        help_text="Número de contato via WhatsApp"
    )
    
    # Contato e informações adicionais
    categorias = models.ManyToManyField(
        TipoServico,
        verbose_name="Categorias",
        help_text="Categorias relacionadas ao serviço"
    )
    imagem = models.ForeignKey(
        'campanhas.Imagem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Imagem",
        help_text="Imagem representativa do serviço"
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ativa',
        verbose_name="Status",
        help_text="Status atual da doação independente"
    )
    ativa = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se a doação está ativa para receber solicitações"
    )
    
    # Requisitos e observações
    
    # Timestamps
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )

    class Meta:
        verbose_name = "Doação Independente"
        verbose_name_plural = "Doações Independentes"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.titulo} - {self.doadora.nome_exibicao}"

    @property
    def status_display(self):
        status_map = {
            'ativa': '🟢 Ativa',
            'pausada': '⏸️ Pausada',
            'finalizada': '✅ Finalizada',
            'cancelada': '❌ Cancelada',
        }
        return status_map.get(self.status, self.status)

    def pausar_servico(self):
        """Pausa o serviço"""
        self.status = 'pausada'
        self.ativa = False
        self.save(update_fields=['status', 'ativa'])

    def reativar_servico(self):
        """Reativa o serviço"""
        self.status = 'ativa'
        self.ativa = True
        self.save(update_fields=['status', 'ativa'])

    def finalizar_servico(self):
        """Finaliza o serviço"""
        self.status = 'finalizada'
        self.ativa = False
        self.save(update_fields=['status', 'ativa'])

    def cancelar_servico(self):
        """Cancela o serviço"""
        self.status = 'cancelada'
        self.ativa = False
        self.save(update_fields=['status', 'ativa'])


# ==================== SINAIS DJANGO ====================

@receiver(post_save, sender=Doacao)
def atualizar_progresso_campanha_doacao(sender, instance, created, **kwargs):
    """
    Atualiza o progresso da campanha quando uma doação é salva
    """
    if instance.item_campanha and instance.item_campanha.campanha:
        campanha = instance.item_campanha.campanha
        # Força o recálculo do percentual_atingido
        campanha.save(update_fields=[])  # Salva sem campos específicos para forçar recálculo


@receiver(post_delete, sender=Doacao)
def atualizar_progresso_campanha_doacao_delete(sender, instance, **kwargs):
    """
    Atualiza o progresso da campanha quando uma doação é deletada
    """
    if instance.item_campanha and instance.item_campanha.campanha:
        campanha = instance.item_campanha.campanha
        # Força o recálculo do percentual_atingido
        campanha.save(update_fields=[])
