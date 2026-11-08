import pytest

from modulo_pii.validadores import cpf_valido


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725"])
def test_cpf_valido(cpf):
    assert cpf_valido(cpf)


@pytest.mark.parametrize("cpf", ["529.982.247-24", "111.111.111-11", "123", "", "abc.def.ghi-jk", "000.000.000-00"])
def test_cpf_invalido(cpf):
    assert not cpf_valido(cpf)
