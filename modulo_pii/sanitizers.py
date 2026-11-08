"""Sanitizers: transformam dado sensível em algo seguro de sair do sistema."""
import hashlib
import hmac
import os

from .detector import detectar_pii
from .validadores import so_digitos


def mascarar_cpf(cpf: str) -> str:
    n = so_digitos(cpf)
    return f"***.***.***-{n[-2:]}" if len(n) == 11 else "***"


def mascarar_generico(valor: str, tipo: str = "") -> str:
    if tipo == "CPF":
        return mascarar_cpf(valor)
    if tipo == "SENHA":
        return "[SENHA REMOVIDA]"
    if tipo == "EMAIL":
        return "[EMAIL REMOVIDO]"
    if tipo == "SAUDE":
        return "[DADO DE SAÚDE REMOVIDO]"
    if tipo == "TELEFONE":
        return "[TELEFONE REMOVIDO]"
    return "[REMOVIDO]"


def sanitizar_texto(texto: str) -> tuple[str, list]:
    """Troca todo PII do texto por máscaras. Retorna (texto_limpo, achados)."""
    achados = detectar_pii(texto)
    limpo, cursor = [], 0
    for a in achados:
        limpo.append(texto[cursor:a.inicio])
        limpo.append(mascarar_generico(a.trecho, a.tipo))
        cursor = a.fim
    limpo.append(texto[cursor:])
    return "".join(limpo), achados


def hash_cpf(cpf: str) -> str:
    """HMAC-SHA256 com 'pepper' do ambiente: permite buscar usuário sem guardar o CPF em claro."""
    pepper = os.getenv("PEPPER_CPF", "dev-pepper-troque-em-producao").encode()
    return hmac.new(pepper, so_digitos(cpf).encode(), hashlib.sha256).hexdigest()
