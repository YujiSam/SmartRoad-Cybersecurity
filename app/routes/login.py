from fastapi import APIRouter, HTTPException

from .. import auth
from ..database import conectar
from ..schemas import LoginIn
from modulo_pii.sanitizers import mascarar_cpf
from modulo_pii.sinks import sink_log, sink_resposta
from modulo_pii.taint import marcar

router = APIRouter(tags=["login"])


@router.post("/login")
def login(dados: LoginIn):
    cpf = marcar(dados.cpf, {"CPF"})  # SOURCE: o CPF é o usuário
    with conectar() as c:
        linha = c.execute("SELECT * FROM cidadaos WHERE cpf_hash=?", (auth.chave_cpf(cpf),)).fetchone()
    if not linha or not auth.senha_confere(dados.senha, linha["senha_hash"]):
        # log SEM o CPF cru: só a versão mascarada, via sink
        sink_log(f"Login falhou para {mascarar_cpf(cpf)}", origem="POST /login")
        raise HTTPException(401, "CPF ou senha incorretos")
    token = auth.criar_sessao(linha["id"])
    sink_log(f"Login ok para {mascarar_cpf(cpf)}", origem="POST /login")
    return sink_resposta({"token": token, "cpf": mascarar_cpf(cpf)}, origem="POST /login")
