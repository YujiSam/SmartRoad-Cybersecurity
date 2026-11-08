"""Log de auditoria (JSON Lines). Nunca grava o dado sensível, só metadados."""
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

ARQUIVO = Path(os.getenv("AUDITORIA_PATH", Path(__file__).resolve().parent.parent / "logs" / "auditoria.jsonl"))
_lock = threading.Lock()


def registrar_auditoria(origem: str, destino: str, tipos: list[str], bloqueado: bool, detalhe: str = "") -> dict:
    evento = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origem": origem,
        "destino": destino,
        "tipos": sorted(set(tipos)),
        "bloqueado": bloqueado,
        "detalhe": detalhe,
    }
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    with _lock, ARQUIVO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    return evento


def ler_eventos() -> list[dict]:
    if not ARQUIVO.exists():
        return []
    eventos = []
    for linha in ARQUIVO.read_text(encoding="utf-8").splitlines():
        try:
            eventos.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return eventos
