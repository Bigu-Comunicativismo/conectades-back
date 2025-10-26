"""
Serializers para Solicitações de Beneficiária
"""
from rest_framework import serializers
from .models import SolicitacaoBeneficiaria


class SolicitacaoRespostaSerializer(serializers.Serializer):
    """Serializer para aceitar/recusar solicitação"""
    mensagem = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Mensagem da beneficiária ao aceitar ou recusar a solicitação"
    )

