"""Autenticação por CPF. O CPF nunca é guardado em claro nem escrito em log."""
import logging
import os
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet

from modulo_pii.sanitizers import hash_cpf
from modulo_pii.validadores import so_digitos

_ph = PasswordHasher()
_SESSOES: dict[str, int] = {}  # token -> cidadao_id (protótipo; em produção, JWT/Redis)
_chave_dev = None


def _fernet() -> Fernet:
    chave = os.getenv("CHAVE_FERNET")
    if not chave:
        # chave efêmera de desenvolvimento: dados cifrados NÃO sobrevivem a um reinício
        global _chave_dev
        if _chave_dev is None:
            _chave_dev = Fernet.generate_key()
            logging.getLogger("smartroad").warning(
                "CHAVE_FERNET não definida: usando chave temporária. "
                "Defina CHAVE_FERNET no .env para conseguir decifrar o perfil de mobilidade após reiniciar."
            )
        chave = _chave_dev.decode()
    return Fernet(chave.encode())


def cifrar(texto: str) -> str:
    return _fernet().encrypt(texto.encode()).decode()


def decifrar(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()


def hash_senha(senha: str) -> str:
    return _ph.hash(senha)


def senha_confere(senha: str, senha_hash: str) -> bool:
    try:
        return _ph.verify(senha_hash, senha)
    except VerifyMismatchError:
        return False


def chave_cpf(cpf: str) -> str:
    return hash_cpf(cpf)


def cpf_final(cpf: str) -> str:
    return so_digitos(cpf)[-2:]


def criar_sessao(cidadao_id: int) -> str:
    token = secrets.token_urlsafe(24)
    _SESSOES[token] = cidadao_id
    return token


def cidadao_da_sessao(token: str) -> int | None:
    return _SESSOES.get(token)
