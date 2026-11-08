from fastapi import APIRouter, HTTPException

from ..database import conectar
from ..grafo import NOS, TRECHOS, melhor_rota, nota_trecho
from modulo_pii.sinks import sink_resposta

router = APIRouter(tags=["rotas"])


@router.get("/rota")
def rota(origem: str, destino: str):
    if origem not in NOS or destino not in NOS:
        raise HTTPException(422, f"Pontos válidos: {NOS}")
    with conectar() as c:
        abertos = [dict(r) for r in c.execute("SELECT tipo, trecho FROM relatos WHERE status='aberto'")]
    notas = {t: nota_trecho(t, abertos) for t in TRECHOS}
    resultado = melhor_rota(origem, destino, notas)
    return sink_resposta(resultado or {"erro": "sem rota"}, origem="GET /rota")
