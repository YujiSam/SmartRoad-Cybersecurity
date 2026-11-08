"""Gera CPFs VÁLIDOS (dígito verificador correto), porém fictícios, para testes e demo."""
import random


def _dv(base: list[int]) -> int:
    soma = sum(d * p for d, p in zip(base, range(len(base) + 1, 1, -1)))
    r = (soma * 10) % 11
    return 0 if r == 10 else r


def gerar_cpf() -> str:
    base = [random.randint(0, 9) for _ in range(9)]
    base.append(_dv(base))
    base.append(_dv(base))
    n = "".join(map(str, base))
    return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"


if __name__ == "__main__":
    for _ in range(5):
        print(gerar_cpf())
