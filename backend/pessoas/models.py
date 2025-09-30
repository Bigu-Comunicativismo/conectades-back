from django.contrib.auth.models import AbstractUser
from django.db import models

class Pessoa(AbstractUser):
    TIPOS = [
        ("beneficiaria", "Beneficiária"),
        ("doadora", "Doadora"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS)
    nome = models.CharField(max_length=100, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    nome_alias = models.CharField(max_length=50, blank=True, null=True, help_text="Nome que será exibido publicamente")
    mini_bio = models.TextField(max_length=500, blank=True, null=True, help_text="Breve descrição sobre você")
    foto = models.ImageField(upload_to='fotos_pessoas/', blank=True, null=True)

    def __str__(self):
        display_name = self.nome_alias or self.nome or self.username
        return f"{display_name} ({self.tipo})"