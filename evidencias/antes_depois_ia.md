# Antes e depois: tradução do alerta

## Antes (log técnico de auditoria)
```json
{'ts': '2026-11-08T00:20:42+00:00', 'origem': 'GET /demo/vaza-cpf-no-log', 'destino': 'log', 'tipos': ['CPF'], 'bloqueado': True, 'detalhe': 'saída com PII bloqueada'}
```

## Depois (alerta ao cidadão, fonte: fallback)
> Detectamos dado pessoal em um lugar inseguro. Seu CPF poderia ser usado por golpistas para abrir contas ou fazer compras em seu nome. O sistema bloqueou o vazamento antes de chegar a alguém. Você não precisa fazer nada.
