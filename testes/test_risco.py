from modulo_pii.risco import nivel, resumo, risco_cidadao


def ev(tipos, destino, bloqueado):
    return {"tipos": tipos, "destino": destino, "bloqueado": bloqueado}


def test_sem_eventos_risco_zero():
    assert risco_cidadao([]) == 0


def test_bloqueado_pesa_menos_que_vazado():
    assert risco_cidadao([ev(["CPF"], "log", True)]) < risco_cidadao([ev(["CPF"], "log", False)])


def test_teto_100():
    assert risco_cidadao([ev(["SENHA"], "api", False)] * 10) == 100


def test_niveis():
    assert [nivel(s) for s in (0, 30, 60, 90)] == ["Baixo", "Médio", "Alto", "Crítico"]


def test_resumo():
    r = resumo([ev(["CPF"], "log", True), ev([], "api", False), ev(["SENHA"], "api", False)])
    assert r["bloqueados"] == 1 and r["vazados"] == 1 and r["por_tipo"] == {"CPF": 1, "SENHA": 1}
