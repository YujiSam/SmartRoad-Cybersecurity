from typing import Literal

from pydantic import BaseModel, Field, field_validator

from modulo_pii.validadores import cpf_valido


class CadastroIn(BaseModel):
    cpf: str
    senha: str = Field(min_length=8)
    perfil_mobilidade: Literal["nenhum", "cadeirante", "baixa_visao", "idoso", "carrinho_bebe"] = "nenhum"

    @field_validator("cpf")
    @classmethod
    def _cpf(cls, v):
        if not cpf_valido(v):
            raise ValueError("CPF inválido")
        return v


class LoginIn(BaseModel):
    cpf: str
    senha: str


class RelatoIn(BaseModel):
    tipo: Literal["buraco", "iluminacao", "calcada", "seguranca"]
    trecho: str
    descricao: str = Field(min_length=3, max_length=500)
