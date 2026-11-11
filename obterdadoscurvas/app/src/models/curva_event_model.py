import re
from dataclasses import dataclass
from datetime import datetime

TIPOS_VALIDOS = ("BASE", "COMPOSTA", "TRANSFER")


class EventoInvalido(Exception):
    pass


@dataclass
class CurvaEventModel:
    """Evento do tópico de curvas (guia de curvas, seção 5)."""
    codigo_curva: str
    nome_curva: str
    tipo_curva: str
    data_liberacao: str      # yyyymmdd: data usada para buscar os pontos
    data_inclusao: str

    @classmethod
    def from_event(cls, value: dict) -> "CurvaEventModel":
        for campo in ("codigo_curva", "nome_curva", "nome_tipo_curva", "data_liberacao", "data_inclusao"):
            if not str(value.get(campo) or "").strip():
                raise EventoInvalido(f"campo obrigatório ausente: {campo}")

        tipo = str(value["nome_tipo_curva"]).strip().upper()
        if tipo not in TIPOS_VALIDOS:
            raise EventoInvalido(f"nome_tipo_curva desconhecido: {tipo}")

        return cls(codigo_curva=str(value["codigo_curva"]).strip(),
                   nome_curva=str(value["nome_curva"]).strip(),
                   tipo_curva=tipo,
                   data_liberacao=_para_yyyymmdd(str(value["data_liberacao"]).strip()),
                   data_inclusao=str(value["data_inclusao"]).strip())


def _para_yyyymmdd(texto: str) -> str:
    if re.fullmatch(r"\d{8}", texto):
        return texto
    if re.match(r"\d{4}-\d{2}-\d{2}", texto):
        return datetime.strptime(texto[:10], "%Y-%m-%d").strftime("%Y%m%d")
    raise EventoInvalido(f"data_liberacao inválida: {texto}")
