"""Traduz falha técnica -> alerta simples para o cidadão.

Regra de ouro: a LLM recebe SÓ metadados (tipo, local, gravidade). Nunca o CPF, a senha ou o texto
do relato. O envio passa por sink_llm, que bloqueia se algum PII escapar. Se a LLM falhar ou estiver
desligada (USAR_LLM=false), usa o texto fixo de fallback.py.
"""
import requests

from app import config
from modulo_pii.regras import PESO
from modulo_pii.risco import nivel
from modulo_pii.sinks import VazamentoBloqueado, sink_llm
from .fallback import alerta_fixo
from .prompts import PROMPT_ALERTA


def _gravidade(tipos: list[str]) -> str:
    return nivel(min(100, sum(PESO.get(t, 5) for t in tipos)))


def traduzir_alerta(evento: dict) -> dict:
    """evento = linha da auditoria. Retorna {'texto': str, 'fonte': 'llm'|'fallback'}."""
    tipos, bloqueado = evento.get("tipos", []), evento.get("bloqueado", False)
    meta = {
        "falha": "dado pessoal em saída insegura" + (" (bloqueado)" if bloqueado else ""),
        "tipos": ", ".join(tipos) or "nenhum",
        "onde": evento.get("destino", "desconhecido"),
        "gravidade": _gravidade(tipos),
    }
    fallback = {"texto": alerta_fixo(tipos, bloqueado), "fonte": "fallback"}
    if not (config.USAR_LLM and config.GEMINI_API_KEY and tipos):
        return fallback
    try:
        sink_llm(meta, origem="ia.tradutor")  # garante: só metadados saem
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent",
            headers={"x-goog-api-key": config.GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": PROMPT_ALERTA.format(**meta)}]}]},
            timeout=10,
        )
        r.raise_for_status()
        texto = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return {"texto": texto, "fonte": "llm"}
    except (VazamentoBloqueado, requests.RequestException, KeyError, IndexError, ValueError):
        return fallback
