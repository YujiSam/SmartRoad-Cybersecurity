import sqlite3
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS cidadaos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf_hash TEXT UNIQUE NOT NULL,      -- HMAC do CPF (nunca o CPF em claro)
    cpf_final TEXT NOT NULL,            -- só os 2 últimos dígitos, p/ exibir mascarado
    senha_hash TEXT NOT NULL,           -- argon2
    perfil_mobilidade TEXT,             -- dado de saúde (sensível) -> cifrado
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS relatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cidadao_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,                 -- buraco | iluminacao | calcada | seguranca
    trecho TEXT NOT NULL,               -- id do trecho no grafo do bairro
    descricao TEXT NOT NULL,            -- SEMPRE sanitizada antes de salvar
    status TEXT DEFAULT 'aberto',
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db() -> None:
    with conectar() as c:
        c.executescript(SCHEMA)


@contextmanager
def conectar():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()
