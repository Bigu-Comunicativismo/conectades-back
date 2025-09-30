from django.db import models
from backend.pessoas.models import Pessoa
from backend.campanhas.models import Campanha

class Doacao(models.Model):
    TIPOS_DOACAO = [
        ("alimento", "Alimento"),
        ("roupa", "Roupa"),
        ("brinquedo", "Brinquedo"),
        ("servico", "Serviço"),
        ("outro", "Outro"),
    ]

    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE, related_name="doacoes")
    doador = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="doacoes")
    tipo = models.CharField(max_length=50, choices=TIPOS_DOACAO)
    descricao = models.TextField(blank=True, null=True)
    data_doacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.doador.username}"
