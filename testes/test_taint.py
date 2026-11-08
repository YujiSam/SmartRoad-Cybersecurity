import pytest

from modulo_pii.sanitizers import mascarar_cpf
from modulo_pii.sinks import VazamentoBloqueado, sink_log, sink_llm, sink_resposta
from modulo_pii.taint import Tainted, marcar, tags_de

CPF = "529.982.247-25"


def test_taint_propaga_na_concatenacao_e_fstring():
    cpf = marcar(CPF, {"CPF"})
    assert tags_de("Usuário: " + cpf) == {"CPF"}
    assert tags_de("%s ok" % cpf) == {"CPF"}
    assert tags_de(cpf.replace(".", "")) == {"CPF"}
    assert tags_de(cpf[:3]) == {"CPF"}


def test_limitacao_fstring_perde_rotulo_mas_sink_pega_pelo_detector():
    """f-string devolve str comum (limitação do Python): o rótulo se perde,
    mas o sink roda o detector como defesa em profundidade e bloqueia mesmo assim."""
    cpf = marcar(CPF, {"CPF"})
    assert tags_de(f"Usuário: {cpf}") == frozenset()
    with pytest.raises(VazamentoBloqueado):
        sink_log(f"Usuário: {cpf}")


def test_cpf_cru_no_log_e_bloqueado():
    with pytest.raises(VazamentoBloqueado):
        sink_log(f"login {marcar(CPF, {'CPF'})}")


def test_cpf_mascarado_no_log_e_permitido():
    sink_log(f"login {mascarar_cpf(marcar(CPF, {'CPF'}))}")


def test_senha_na_resposta_bloqueada():
    with pytest.raises(VazamentoBloqueado):
        sink_resposta({"x": marcar("qualquer", {"SENHA"})})


def test_defesa_em_profundidade_pega_pii_sem_rotulo():
    with pytest.raises(VazamentoBloqueado):
        sink_resposta({"cpf": CPF})  # ninguém marcou, o detector pega


def test_llm_so_recebe_metadados():
    sink_llm({"tipos": "CPF", "onde": "log", "gravidade": "Médio"})
    with pytest.raises(VazamentoBloqueado):
        sink_llm({"texto": f"o cpf é {CPF}"})
