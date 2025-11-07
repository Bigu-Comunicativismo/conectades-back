import logging
from django.core import signing
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .email_service import TOKEN_SALT_CONFIRMACAO, TOKEN_EXPIRACAO_SEGUNDOS
from .models import Doacao

logger = logging.getLogger(__name__)

TEMPLATE_CONFIRMACAO = "doacoes/confirmacao_doacao.html"


def _template_path_exists(template_name: str) -> bool:
    """
    Checa se template custom existe. Evita erro silencioso se template não for encontrado.
    """
    try:
        from django.template.loader import get_template

        get_template(template_name)
        return True
    except Exception:
        return False


def confirmar_doacao_via_link(request, token: str):
    contexto = {
        "status": "erro",
        "titulo": "Token inválido",
        "mensagem": "Não foi possível validar seu link de confirmação. Solicite uma nova confirmação.",
    }

    try:
        dados = signing.loads(
            token,
            salt=TOKEN_SALT_CONFIRMACAO,
            max_age=TOKEN_EXPIRACAO_SEGUNDOS,
        )
        doacao_id = dados.get("doacao_id")
        beneficiaria_id = dados.get("beneficiaria_id")
    except signing.SignatureExpired:
        contexto["titulo"] = "Link expirado"
        contexto["mensagem"] = (
            "Este link de confirmação expirou. Peça uma nova confirmação à organizadora."
        )
        logger.warning("Token de confirmação expirado.")
        return _render_confirmacao(request, contexto)
    except signing.BadSignature:
        logger.warning("Token de confirmação inválido.")
        return _render_confirmacao(request, contexto)

    try:
        doacao = Doacao.objects.select_related("campanha", "doador").get(id=doacao_id)
    except Doacao.DoesNotExist:
        logger.error("Doação %s não encontrada ao confirmar via link.", doacao_id)
        contexto["mensagem"] = "Doação não encontrada. Verifique se o link está correto."
        return _render_confirmacao(request, contexto)

    if doacao.campanha.beneficiaria_id != beneficiaria_id:
        logger.error(
            "Tentativa de confirmar doação %s com beneficiária divergente (token %s).",
            doacao_id,
            beneficiaria_id,
        )
        contexto["mensagem"] = "Este link não corresponde à beneficiária da doação."
        return _render_confirmacao(request, contexto)

    if doacao.status in ("confirmada", "entregue"):
        contexto.update(
            {
                "status": "sucesso",
                "titulo": "Doação já confirmada",
                "mensagem": "Esta doação já foi confirmada anteriormente. Obrigada! 💜",
            }
        )
        return _render_confirmacao(request, contexto)

    doacao.status = "confirmada"
    if not doacao.data_entrega:
        doacao.data_entrega = timezone.now()
    doacao.save(update_fields=["status", "data_entrega"])

    logger.info("Doação %s confirmada via link pela beneficiária.", doacao_id)

    contexto.update(
        {
            "status": "sucesso",
            "titulo": "Doação confirmada com sucesso! 🎉",
            "mensagem": (
                f"A doação de {doacao.quantidade} {doacao.unidade} para a campanha "
                f'"{doacao.campanha.titulo}" foi confirmada.'
            ),
            "doadora_nome": doacao.doador.nome_exibicao,
            "campanha_titulo": doacao.campanha.titulo,
        }
    )
    return _render_confirmacao(request, contexto)


def _render_confirmacao(request, contexto):
    if _template_path_exists(TEMPLATE_CONFIRMACAO):
        return render(request, TEMPLATE_CONFIRMACAO, contexto)
    # fallback simples se template não estiver disponível
    status = contexto.get("status", "erro")
    titulo = contexto.get("titulo", "Confirmação")
    mensagem = contexto.get("mensagem", "")
    return HttpResponse(f"<h1>{titulo}</h1><p>{mensagem}</p>", status=200 if status == "sucesso" else 400)

