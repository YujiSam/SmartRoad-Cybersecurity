from fastapi import APIRouter, Header, HTTPException

from .. import auth
from ..database import conectar
from ..grafo import TRECHOS
from ..schemas import RelatoIn
from modulo_pii.auditoria import registrar_auditoria
from modulo_pii.sanitizers import sanitizar_texto
from modulo_pii.sinks import sink_resposta
from modulo_pii.taint import marcar_auto

router = APIRouter(tags=["relatos"])


@router.post("/relatos", status_code=201)
def criar_relato(dados: RelatoIn, authorization: str = Header(default="")):
    cid = auth.cidadao_da_sessao(authorization.removeprefix("Bearer ").strip())
    if cid is None:
        raise HTTPException(401, "Faça login")
    if dados.trecho not in TRECHOS:
        raise HTTPException(422, "Trecho inexistente")

    # SOURCE automático: se o texto livre tiver PII, vira Tainted
    texto = marcar_auto(dados.descricao)
    descricao_segura, achados = sanitizar_texto(dados.descricao)
    aviso = None
    if achados:
        tipos = [a.tipo for a in achados]
        registrar_auditoria("POST /relatos", "banco", tipos, bloqueado=True,
                            detalhe="texto cru bloqueado; versão mascarada publicada")
        aviso = "Seu relato continha dado pessoal. Removemos antes de publicar."

    with conectar() as c:
        cur = c.execute(
            "INSERT INTO relatos (cidadao_id, tipo, trecho, descricao) VALUES (?,?,?,?)",
            (cid, dados.tipo, dados.trecho, descricao_segura),
        )
    return sink_resposta(
        {"id": cur.lastrowid, "descricao_publicada": descricao_segura, "aviso": aviso},
        origem="POST /relatos",
    )


@router.get("/relatos")
def listar_relatos():
    with conectar() as c:
        linhas = c.execute("SELECT id, tipo, trecho, descricao, status FROM relatos ORDER BY id DESC").fetchall()
    return sink_resposta([dict(l) for l in linhas], origem="GET /relatos")
