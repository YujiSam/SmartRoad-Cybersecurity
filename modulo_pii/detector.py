"""Motor de parsing de PII: varre um texto e devolve os achados."""
import re
from dataclasses import dataclass, asdict

from .regras import REGRAS
from .validadores import cpf_valido


@dataclass
class Achado:
    tipo: str
    inicio: int
    fim: int
    trecho: str  # uso interno: NUNCA logar nem enviar a LLM

    def publico(self) -> dict:
        """Versão segura (sem o trecho) para log, dashboard e LLM."""
        d = asdict(self)
        d.pop("trecho")
        return d


def detectar_pii(texto: str) -> list[Achado]:
    achados: list[Achado] = []
    for tipo, (padrao, _desc) in REGRAS.items():
        for m in re.finditer(padrao, texto):
            if tipo == "CPF" and not cpf_valido(m.group()):
                continue  # evita falso positivo (ex.: número de protocolo)
            achados.append(Achado(tipo, m.start(), m.end(), m.group()))
    # remove sobreposição (ex.: telefone dentro de CPF): mantém o primeiro/mais longo
    achados.sort(key=lambda a: (a.inicio, -(a.fim - a.inicio)))
    limpos: list[Achado] = []
    for a in achados:
        if limpos and a.inicio < limpos[-1].fim:
            continue
        limpos.append(a)
    return limpos


def tem_pii(texto: str) -> bool:
    return bool(detectar_pii(texto))
