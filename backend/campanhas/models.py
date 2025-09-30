from django.db import models
from backend.pessoas.models import Pessoa

class Organizadora(models.Model):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="perfil_organizadora"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Organizadora: {self.pessoa.nome_alias or self.pessoa.nome or self.pessoa.username}"

class Campanha(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    organizadora = models.ForeignKey(
        Organizadora,
        on_delete=models.CASCADE,
        related_name="campanhas"
    )
    beneficiaria = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE,
        related_name="campanhas_beneficiaria",
        limit_choices_to={"tipo": "beneficiaria"},
        blank=True,
        null=True
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.titulo