"""Taint Analysis: rastreia dado sensível da entrada (source) até a saída (sink).

Source  : marcar(valor, tipos)  -> devolve um Tainted
Propaga : concatenação (+), formatação (% e .format), upper/lower/strip/replace, slicing
LIMITAÇÃO: f-strings devolvem str comum e PERDEM o rótulo (comportamento do Python).
           Por isso todo sink também roda o detector de PII (defesa em profundidade).
Sanitiza: modulo_pii.sanitizers (mascarar_cpf, sanitizar_texto...) devolve str comum (limpa)
Sink    : modulo_pii.sinks verifica o rótulo e bloqueia
"""


class Tainted(str):
    """String que carrega rótulos (tags) dos tipos de PII que contém."""

    tags: frozenset

    def __new__(cls, valor="", tags=()):
        obj = super().__new__(cls, valor)
        obj.tags = frozenset(tags)
        return obj

    # --- propagação: qualquer operação que misture ou derive mantém o rótulo ---
    def __add__(self, outro):
        return Tainted(str.__add__(self, str(outro)), self.tags | tags_de(outro))

    def __radd__(self, outro):
        return Tainted(str(outro) + str(self), self.tags | tags_de(outro))

    def __mod__(self, args):
        return Tainted(str.__mod__(self, args), self.tags | tags_de(args))

    def __rmod__(self, modelo):
        # "texto %s" % tainted  -> o Python tenta o __rmod__ da subclasse primeiro
        return Tainted(str(modelo) % str(self), self.tags | tags_de(modelo))

    def __getitem__(self, i):
        return Tainted(str.__getitem__(self, i), self.tags)

    def format(self, *a, **k):
        t = set(self.tags)
        for v in list(a) + list(k.values()):
            t |= tags_de(v)
        return Tainted(str.format(self, *a, **k), t)

    def __format__(self, spec):
        return Tainted(str.__format__(self, spec), self.tags)

    def _derivar(nome):
        def metodo(self, *a, **k):
            return Tainted(getattr(str, nome)(self, *a, **k), self.tags)
        metodo.__name__ = nome
        return metodo

    upper = _derivar("upper")
    lower = _derivar("lower")
    strip = _derivar("strip")
    replace = _derivar("replace")
    title = _derivar("title")

    def __repr__(self):
        return f"Tainted({str.__repr__(self)}, tags={sorted(self.tags)})"


def tags_de(valor) -> frozenset:
    """Tags de um valor qualquer (inclusive dict/list/tuple com Tainted dentro)."""
    if isinstance(valor, Tainted):
        return valor.tags
    if isinstance(valor, dict):
        t = frozenset()
        for k, v in valor.items():
            t |= tags_de(k) | tags_de(v)
        return t
    if isinstance(valor, (list, tuple, set, frozenset)):
        t = frozenset()
        for v in valor:
            t |= tags_de(v)
        return t
    return frozenset()


def marcar(valor: str, tipos) -> Tainted:
    """SOURCE: declara que 'valor' contém dado sensível dos 'tipos' informados."""
    return Tainted(valor, tipos)


def marcar_auto(texto: str) -> str:
    """SOURCE automático: roda o detector e marca o texto se houver PII."""
    from .detector import detectar_pii

    tipos = {a.tipo for a in detectar_pii(texto)}
    return Tainted(texto, tipos) if tipos else texto
