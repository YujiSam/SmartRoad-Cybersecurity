"""ROTAS DE DEMONSTRAÇÃO. Existem só para mostrar o Taint Analysis bloqueando vazamentos.

Cada rota tenta de propósito vazar um dado sensível. O bloqueio é o comportamento esperado.
NÃO fazem parte da funcionalidade do SmartRoad e devem ser desligadas em produção.
"""
from fastapi import APIRouter

from modulo_pii.sanitizers import mascarar_cpf
from modulo_pii.sinks import sink_log, sink_resposta
from modulo_pii.taint import marcar

router = APIRouter(prefix="/demo", tags=["demo-vazamento"])

CPF_FICTICIO = "529.982.247-25"  # CPF válido, fictício (gerado para teste)


@router.get("/vaza-cpf-no-log")
def vaza_cpf_log():
    """Cenário 1: CPF cru vai para o log -> BLOQUEADO."""
    cpf = marcar(CPF_FICTICIO, {"CPF"})
    sink_log(f"Usuário logado: {cpf}", origem="GET /demo/vaza-cpf-no-log")
    return {"ok": True}


@router.get("/cpf-mascarado-no-log")
def cpf_mascarado_log():
    """Cenário 2: CPF mascarado no log -> PERMITIDO."""
    cpf = marcar(CPF_FICTICIO, {"CPF"})
    sink_log(f"Usuário logado: {mascarar_cpf(cpf)}", origem="GET /demo/cpf-mascarado-no-log")
    return {"ok": True, "cpf": mascarar_cpf(cpf)}


@router.get("/vaza-senha-na-resposta")
def vaza_senha():
    """Cenário 3: senha na resposta da API -> BLOQUEADO."""
    senha = marcar("senha: MinhaSenha123", {"SENHA"})
    return sink_resposta({"debug": senha}, origem="GET /demo/vaza-senha-na-resposta")


@router.get("/vaza-sem-sink")
def vaza_sem_sink():
    """Cenário 4: rota 'esqueceu' o sink e devolve o CPF -> o MIDDLEWARE bloqueia."""
    return {"cpf_do_usuario": CPF_FICTICIO}
