"""Textos fixos usados quando a LLM está desligada, sem chave ou fora do ar."""

RISCO = {
    "CPF": "Seu CPF poderia ser usado por golpistas para abrir contas ou fazer compras em seu nome.",
    "SENHA": "Sua senha poderia dar acesso à sua conta a outras pessoas.",
    "SAUDE": "Sua informação de saúde ou mobilidade é privada e não deve ser vista por terceiros.",
    "EMAIL": "Seu e-mail poderia receber golpes e mensagens falsas.",
    "TELEFONE": "Seu telefone poderia ser usado para golpes por ligação ou mensagem.",
}


def alerta_fixo(tipos: list[str], bloqueado: bool) -> str:
    if not tipos:
        return "Nenhum dado pessoal foi exposto."
    riscos = " ".join(RISCO.get(t, "Um dado pessoal seu estava exposto.") for t in tipos)
    acao = ("O sistema bloqueou o vazamento antes de chegar a alguém. Você não precisa fazer nada."
            if bloqueado else
            "Troque suas senhas e fique atento a mensagens suspeitas.")
    return f"Detectamos dado pessoal em um lugar inseguro. {riscos} {acao}"
