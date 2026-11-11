import os
from src.configs.logger_config import logger

# Nome do campo que o IM8 usa para marcar ponto interpolado. PROVISÓRIO: confirmar com uma resposta real da API.
CAMPO_INTERPOLADO_PADRAO = "indicador_interpolado"


def filtrar_pilares(resposta_im8):
    """Mantém só os pilares da curva: pontos que o IM8 NÃO marcou como interpolados (reunião de 10/11)."""
    campo = os.getenv("CAMPO_INTERPOLADO", CAMPO_INTERPOLADO_PADRAO)
    pontos = resposta_im8.get("pontos", []) if isinstance(resposta_im8, dict) else resposta_im8

    pilares = [p for p in pontos if str(p.get(campo) or "").strip().upper() in ("", "N", "FALSE", "0")]
    logger.info("Pilares filtrados.", total_pontos=len(pontos), total_pilares=len(pilares), campo_interpolado=campo)
    return pilares
