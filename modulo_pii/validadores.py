"""Validadores de documentos (dígito verificador do CPF)."""
import re


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def cpf_valido(cpf: str) -> bool:
    """True se o CPF tem 11 dígitos, não é sequência repetida e os dígitos verificadores batem."""
    n = so_digitos(cpf)
    if len(n) != 11 or n == n[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(n[j]) * (i + 1 - j) for j in range(i))
        if (soma * 10) % 11 % 10 != int(n[i]):
            return False
    return True
