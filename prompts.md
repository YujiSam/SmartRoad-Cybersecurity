# Registro de prompts de IA (exigido nos combinados da GS)

> Regra da GS: IA é copiloto. Registre aqui cada prompt usado no desenvolvimento e **saiba explicar cada linha do código**.

## Desenvolvimento

| # | Prompt (resumo) | Para quê | O que revisamos/alteramos |
|---|---|---|---|
| 1 | Como estruturar a entrega de Cybersecurity (PII, Taint, IA, dashboard) a partir dos slides da GS | Planejamento | _(preencher)_ |
| 2 | Estrutura de projeto FastAPI + Streamlit com login por CPF para o SmartRoad | Arquitetura | _(preencher)_ |
| 3 | Geração do esqueleto de `modulo_pii`, `app`, `ia` e `dashboard` | Código-base | Testamos tudo (34 testes) e ajustamos o `Tainted` (f-string perde a tag; adicionamos `__rmod__` e defesa em profundidade) |

## Prompt usado em produção (tradução do alerta)

Arquivo `ia/prompts.py`. A LLM recebe **somente** `{falha, tipos, onde, gravidade}`:
nunca o CPF, a senha nem o texto do relato (garantido por `sink_llm`).

## Para o grupo preencher

Adicione aqui novos prompts que vocês usarem e explique, linha a linha, o que o código gerado faz.
