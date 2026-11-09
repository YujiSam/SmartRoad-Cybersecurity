"""Sanitizers: transformam dado sensível em algo seguro de sair do sistema."""
import hashlib
import hmac
import logging
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
    pepper = os.getenv("PEPPER_CPF")
    if not pepper:
        _avisar_pepper_padrao()
        pepper = PEPPER_DEV
    return hmac.new(pepper.encode(), so_digitos(cpf).encode(), hashlib.sha256).hexdigest()


PEPPER_DEV = "dev-pepper-troque-em-producao"
_avisado = False


def _avisar_pepper_padrao() -> None:
    """Sem PEPPER_CPF no ambiente o hash usa um pepper PÚBLICO (só serve para desenvolvimento)."""
    global _avisado
    if not _avisado:
        _avisado = True
        logging.getLogger("smartroad").warning(
            "PEPPER_CPF não definido: usando pepper de desenvolvimento (público). "
            "Defina PEPPER_CPF no .env para proteger os hashes de CPF."
        )
