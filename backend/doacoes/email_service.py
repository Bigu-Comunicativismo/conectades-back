"""
Serviços de email relacionados às doações.
"""
import logging
from typing import Tuple

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

TOKEN_SALT_CONFIRMACAO = "confirmacao-doacao"
TOKEN_EXPIRACAO_SEGUNDOS = 60 * 60 * 24 * 7  # 7 dias


def _format_datetime(dt):
    if not dt:
        return "Não informado"
    return timezone.localtime(dt).strftime("%d/%m/%Y às %H:%M")


def gerar_link_confirmacao_doacao(doacao) -> str:
    """
    Gera link assinado para confirmação da doação pela beneficiária.
    """
    payload = {
        "doacao_id": doacao.id,
        "beneficiaria_id": doacao.campanha.beneficiaria_id,
    }
    token = signing.dumps(payload, salt=TOKEN_SALT_CONFIRMACAO)
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    return f"{site_url}/doacoes/confirmar/{token}/"


def enviar_notificacao_nova_doacao(doacao) -> Tuple[bool, str]:
    """
    Envia email para a beneficiária avisando sobre nova doação recebida.

    Args:
        doacao (Doacao): instância recém-criada.

    Returns:
        tuple (bool, str): sucesso e mensagem.
    """
    campanha = getattr(doacao, "campanha", None)
    beneficiaria = getattr(campanha, "beneficiaria", None) if campanha else None

    if beneficiaria is None:
        logger.info("Doação %s sem beneficiária vinculada. Nenhum email enviado.", doacao.id)
        return False, "Campanha sem beneficiária vinculada"

    if not beneficiaria.email:
        logger.warning(
            "Beneficiária %s não possui email cadastrado. Doação %s sem notificação.",
            beneficiaria.id,
            doacao.id,
        )
        return False, "Beneficiária sem email cadastrado"

    try:
        item = getattr(doacao, "item_campanha", None)
        item_nome = item.nome if item else "Doação livre para a campanha"
        quantidade = doacao.quantidade
        unidade = doacao.unidade or "unidade(s)"

        doadora = doacao.doador
        doadora_nome = doadora.nome_exibicao
        doadora_email = doadora.email or "Não informado"
        doadora_telefone = doadora.telefone or "Não informado"

        assunto = f"🎁 Nova doação recebida na campanha {campanha.titulo}"

        contexto = {
            "beneficiaria_nome": beneficiaria.nome_exibicao,
            "campanha_titulo": campanha.titulo,
            "item_nome": item_nome,
            "quantidade": quantidade,
            "unidade": unidade,
            "doadora_nome": doadora_nome,
            "doadora_email": doadora_email,
            "doadora_telefone": doadora_telefone,
            "data_doacao": _format_datetime(doacao.data_doacao),
            "observacoes": doacao.observacoes or "Sem observações adicionais.",
            "link_confirmacao": gerar_link_confirmacao_doacao(doacao),
            "expiracao_dias": TOKEN_EXPIRACAO_SEGUNDOS // (60 * 60 * 24),
        }

        mensagem = render_to_string("emails/doacao_nova_beneficiaria.txt", contexto)

        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[beneficiaria.email],
            fail_silently=False,
        )

        logger.info(
            "Email de nova doação enviado para beneficiária %s (doação %s).",
            beneficiaria.id,
            doacao.id,
        )
        return True, f"Notificação enviada para {beneficiaria.email}"

    except Exception as exc:  # pragma: no cover - logar e seguir fluxo
        logger.exception(
            "Falha ao enviar email de nova doação %s para beneficiária %s: %s",
            doacao.id,
            getattr(beneficiaria, "id", None),
            exc,
        )
        return False, str(exc)

