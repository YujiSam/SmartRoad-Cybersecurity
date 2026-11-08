import sqlite3

from fastapi import APIRouter, HTTPException

from .. import auth
from ..database import conectar
from ..schemas import CadastroIn
from modulo_pii.sinks import sink_resposta
from modulo_pii.taint import marcar
from modulo_pii.sanitizers import mascarar_cpf

router = APIRouter(tags=["cadastro"])


@router.post("/cadastro", status_code=201)
def cadastrar(dados: CadastroIn):
    # SOURCES: tudo que o cidadão digitou é sensível
    cpf = marcar(dados.cpf, {"CPF"})
    perfil = marcar(dados.perfil_mobilidade, {"SAUDE"}) if dados.perfil_mobilidade != "nenhum" else dados.perfil_mobilidade
    try:
        with conectar() as c:
            c.execute(
                "INSERT INTO cidadaos (cpf_hash, cpf_final, senha_hash, perfil_mobilidade) VALUES (?,?,?,?)",
                (auth.chave_cpf(cpf), auth.cpf_final(cpf), auth.hash_senha(dados.senha),
                 auth.cifrar(str(perfil))),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(409, "CPF já cadastrado")
    # resposta só com versão mascarada (sanitizer)
    return sink_resposta({"mensagem": "Cadastro realizado", "cpf": mascarar_cpf(cpf)}, origem="POST /cadastro")
