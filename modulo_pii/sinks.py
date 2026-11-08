"""Sinks (saídas) seguros. Todo caminho de saída de dados passa por aqui.

Se o dado carregar rótulo de PII (taint) ou o detector achar PII no texto,
a saída é BLOQUEADA e o evento vai para a auditoria. Dado já sanitizado passa.
"""
import json
import logging
from pathlib import Path

from .auditoria import registrar_auditoria
from .detector import detectar_pii
from .taint import Tainted, tags_de

log = logging.getLogger("smartroad")


class VazamentoBloqueado(PermissionError):
    def __init__(self, destino: str, tipos):
        self.destino, self.tipos = destino, sorted(tipos)
        super().__init__(f"Vazamento bloqueado em '{destino}': {self.tipos}")


def _tipos_expostos(dado) -> set:
    tipos = set(tags_de(dado))
    if isinstance(dado, str) and not isinstance(dado, Tainted):
        tipos |= {a.tipo for a in detectar_pii(dado)}  # defesa em profundidade
    elif isinstance(dado, (dict, list, tuple)):
        tipos |= {a.tipo for a in detectar_pii(json.dumps(dado, ensure_ascii=False, default=str))}
    return tipos


def _checar(origem: str, destino: str, dado) -> None:
    tipos = _tipos_expostos(dado)
    if tipos:
        registrar_auditoria(origem, destino, list(tipos), bloqueado=True, detalhe="saída com PII bloqueada")
        raise VazamentoBloqueado(destino, tipos)
    registrar_auditoria(origem, destino, [], bloqueado=False, detalhe="saída limpa permitida")


def sink_log(mensagem, origem: str = "app", nivel=logging.INFO) -> None:
    _checar(origem, "log", mensagem)
    log.log(nivel, str(mensagem))


def sink_resposta(dado, origem: str = "api"):
    """Use antes de devolver qualquer corpo de resposta da API."""
    _checar(origem, "api", dado)
    return dado


def sink_arquivo(caminho: str, conteudo: str, origem: str = "app") -> None:
    _checar(origem, "arquivo", conteudo)
    Path(caminho).write_text(conteudo, encoding="utf-8")


def sink_llm(metadados: dict, origem: str = "ia") -> dict:
    """A LLM só pode receber metadados (tipo, local, gravidade): nunca o dado nem o texto."""
    _checar(origem, "llm", metadados)
    return metadados
