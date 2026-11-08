# Registro de uso de IA (prompts.md)

**Ferramenta:** Claude (Anthropic), usado como copiloto de planejamento e geração de código-base.
**Regra da GS:** IA é copiloto. Aqui registramos os prompts usados e explicamos o que o código faz.

## 1. Prompts usados no desenvolvimento

| # | Prompt (resumo fiel) | O que a IA entregou | Ajustes feitos durante o desenvolvimento |
|---|---|---|---|
| 1 | Enviamos o PDF do briefing da GS e pedimos: "Preciso fazer a parte de Cybersecurity, queria um tutorial de como fazer e um checklist pra ver se está tudo pronto". | Resumo da disciplina (3 missões, rubrica de 10 pts), tutorial em passos e checklist final. | Nenhum (planejamento). |
| 2 | "O professor não mandou nada. Gostaria que coletasse o CPF com um login (usar o login no CPF) e quero saber como fica a estrutura de pastas." | Proposta de estrutura de pastas (`app/`, `modulo_pii/`, `ia/`, `dashboard/`...) e de como guardar o CPF (HMAC) e a senha (argon2). | Definimos FastAPI + SQLite + Streamlit. |
| 3 | Informamos os temas do grupo (rotas urbanas acessíveis + zeladoria colaborativa), pedimos FastAPI + Streamlit e "uma sugestão seria bem-vinda". | Conceito do projeto, ligação com o tema (perfil de mobilidade como dado de saúde, relato com CPF digitado no texto) e proposta de LLM plugável com fallback. | O grupo confirmou o nome **SmartRoad** e deixou a escolha do provedor para a IA (Gemini). |
| 4 | "O nome já é SmartRoad e pode ser da sua escolha o provedor." (gerar o projeto) | Projeto completo: `modulo_pii/`, `app/`, `ia/`, `dashboard/`, `testes/`, `scripts/`, `dados/`. | Ver seção 2. |
| 5 | Pedimos o projeto no GitHub com commits organizados, informamos integrantes/RMs, cidade e bairro (São Paulo, Paulista) e o e-mail do commit. | Histórico git em commits por etapa, README com a Ficha da CitizenTech e roteiro de prints (`evidencias/ROTEIRO_PRINTS.md`). | Troca do e-mail dos commits; definição do bairro. |
| 6 | Pedimos o registro de prompts neste arquivo. | Este documento. | |

### 1.1 Decisões e direção que vieram do grupo (autor: Gustavo)

A IA gerou código, mas estas escolhas de produto e de engenharia foram do grupo:

- **Tema:** combinar *rotas urbanas acessíveis* com *zeladoria colaborativa*, justificando que os temas se completam (o relato alimenta a nota do trecho).
- **Requisito de login por CPF:** foi pedido pelo grupo e é o que cria o desafio real de segurança do projeto (CPF como identificador sem guardá-lo em claro).
- **Stack:** FastAPI + SQLite + Streamlit.
- **Nome e localização:** SmartRoad, São Paulo – Paulista.
- **Qualidade do repositório:** exigiu histórico git organizado por etapa e a Ficha da CitizenTech no README.
- **Transparência:** pediu o registro de uso de IA neste arquivo.

### 1.2 Reformulação posterior do prompt principal (retrospectiva)

> **Atenção:** o texto abaixo **não** é o prompt original enviado. É como o grupo formularia o pedido #4 hoje, aplicando boas práticas de engenharia de prompt. O original está na tabela acima.

```
PAPEL: engenheiro(a) de segurança de aplicações Python.
CONTEXTO: GS FIAP 2026.2, disciplina Cybersecurity. Solução SmartRoad (rotas acessíveis +
  zeladoria). Entrega: motor de parsing de PII, Taint Analysis, tradução de alertas via LLM,
  dashboard de Risco Cidadão. Dados apenas simulados (LGPD).
TAREFA: gerar o esqueleto FastAPI + SQLite + Streamlit com login por CPF.
RESTRIÇÕES: CPF nunca em claro (banco, log, resposta, LLM); LLM só recebe metadados; fallback
  sem internet; cada módulo com testes pytest; sem dependências além de requirements.txt.
SAÍDA: árvore de pastas, código, testes, README com a Ficha e cenários de demonstração.
CRITÉRIO DE ACEITE: pytest verde; nenhum CPF cru em db/logs; 4+ cenários bloqueado/permitido.
```

### 1.3 Reformulações dos demais pedidos (retrospectiva, não são os originais)

**Pedido #1 (planejamento da entrega):**
```
PAPEL: tutor(a) técnico(a) de Engenharia de Software.
CONTEXTO: briefing GS FIAP 2026.2 anexo (slides 28-29, Cybersecurity, 10 pts).
TAREFA: extrair as 3 missões, entregas e rubrica; montar plano de execução até 19/11, 23h55.
SAÍDA: tabela de critérios x pontos, passo a passo e checklist de conclusão verificável.
```

**Pedido #2 (arquitetura e CPF como login):**
```
CONTEXTO: não há projeto-base. Preciso de um protótipo com login por CPF para demonstrar PII e taint.
TAREFA: propor árvore de pastas e política de armazenamento (CPF, senha, dado de saúde).
RESTRIÇÕES: CPF nunca em claro; justificar cada escolha criptográfica; stack Python.
SAÍDA: árvore comentada, tabela dado x técnica x motivo, diagrama de fluxo em texto.
```

**Pedido #3 (alinhamento ao tema do grupo):**
```
CONTEXTO: temas do grupo: rotas urbanas acessíveis + zeladoria colaborativa; stack FastAPI + Streamlit.
TAREFA: sugerir como o tema alimenta a entrega de Cybersecurity (dados sensíveis reais do domínio)
  e uma estratégia de LLM sem dependência de provedor.
SAÍDA: conceito em 1 frase, mapa dado do app x tipo de PII, e riscos de cada decisão.
```

## 2. Problemas encontrados e corrigidos (com testes)

| Problema | Causa | Correção |
|---|---|---|
| Teste de propagação do taint falhou com f-string | f-strings do Python devolvem `str` comum e **perdem o rótulo** do `Tainted` | Documentado como limitação; os sinks rodam o detector de PII também (defesa em profundidade) e há um teste que prova isso |
| `"texto %s" % cpf` perdia o rótulo | O `%` era resolvido pela `str` da esquerda | Implementado `__rmod__` em `Tainted` |

Resultado final: 34 testes passando e 0 ocorrências de CPF em texto puro no banco e nos logs.

## 3. Prompt usado em produção (tradução do alerta)

Arquivo `ia/prompts.py`. A LLM recebe **somente** `{falha, tipos, onde, gravidade}`. Nunca recebe o CPF, a senha nem o texto do relato, e isso é garantido por `sink_llm`. Se a LLM falhar ou estiver desligada (`USAR_LLM=false`), `ia/fallback.py` devolve um texto fixo.

## 4. Explicação do código (arquivo por arquivo)

### modulo_pii/ (a entrega principal)
| Arquivo | O que faz |
|---|---|
| `validadores.py` | `cpf_valido()`: remove a pontuação, rejeita sequências repetidas (111.111.111-11) e confere os 2 dígitos verificadores (módulo 11). Evita falso positivo. |
| `regras.py` | Dicionário `REGRAS` com uma regex por tipo de PII (CPF, SENHA, SAUDE, EMAIL, TELEFONE) e `PESO`, a gravidade de cada tipo para o risco. |
| `detector.py` | `detectar_pii(texto)`: aplica as regexes, valida o CPF, descarta sobreposições e devolve `Achado`s. `Achado.publico()` remove o trecho para nunca ser logado. |
| `taint.py` | `Tainted(str)`: uma string que carrega `tags` dos tipos de PII. Propaga o rótulo em `+`, `%`, `.format`, `upper/lower/strip/replace` e fatiamento. `marcar()` e `marcar_auto()` são as **sources**. |
| `sanitizers.py` | Transformam PII em algo seguro: `mascarar_cpf` (`***.***.***-25`), `sanitizar_texto` (troca todo PII por máscara) e `hash_cpf` (HMAC-SHA256 com pepper). |
| `sinks.py` | As **saídas** (`sink_log`, `sink_resposta`, `sink_arquivo`, `sink_llm`). Antes de sair, checam o rótulo e rodam o detector. Se houver PII, lançam `VazamentoBloqueado` e auditam. |
| `auditoria.py` | Grava cada evento em JSON Lines (`logs/auditoria.jsonl`) com hora, origem, destino, tipos e se foi bloqueado. **Nunca** grava o dado sensível. |
| `risco.py` | Calcula o Risco Cidadão (0 a 100): peso do tipo × fator do destino. Bloqueado conta 10%, vazado conta 100%. Define o nível (Baixo, Médio, Alto, Crítico). |
| `middleware.py` | Última barreira da API: inspeciona toda resposta JSON e, se tiver PII, troca por um erro 500 seguro. |

### app/ (o protótipo SmartRoad)
| Arquivo | O que faz |
|---|---|
| `main.py` | Cria a API FastAPI, liga o middleware, trata `VazamentoBloqueado` e registra as rotas. |
| `config.py`, `database.py` | Lê o `.env` e cria as tabelas SQLite `cidadaos` e `relatos`. |
| `schemas.py` | Validação de entrada (Pydantic). Rejeita CPF inválido no cadastro. |
| `auth.py` | Senha com argon2, CPF como HMAC, perfil de mobilidade cifrado com Fernet e sessões por token. |
| `routes/cadastro.py`, `routes/login.py` | Cadastro e login por CPF. Marcam o CPF como tainted e só devolvem a versão mascarada. |
| `routes/relatos.py` | Recebe relatos. Se o texto livre tiver PII, publica a versão mascarada e avisa o cidadão. |
| `routes/rotas.py`, `grafo.py` | Grafo simulado de 10 pontos. Relatos abertos reduzem a nota do trecho e o Dijkstra escolhe a rota mais acessível. |
| `routes/demo_vazamento.py` | Rotas que tentam vazar **de propósito**, só para demonstrar o bloqueio. |

### ia/, dashboard/, scripts/, testes/
| Arquivo | O que faz |
|---|---|
| `ia/tradutor.py` | Monta metadados, passa por `sink_llm`, chama o Gemini e, se algo falhar, usa o fallback. |
| `dashboard/painel.py` | Streamlit com o indicador, os bloqueios, o gráfico por tipo, o último alerta traduzido e a trilha de auditoria. |
| `scripts/cenarios_demo.py` | Roda os 5 cenários e gera `evidencias/`. |
| `testes/` | 34 testes: CPF, detector (positivos, negativos e falsos positivos), taint, risco e fluxo completo da API. |

## 5. Revisão do grupo (preencher após ler o código)

Marquem só o que cada um realmente fez:

- [ ] Todos leram `modulo_pii/` e sabem explicar source → propagação → sanitizer → sink
- [ ] Rodamos `pytest testes -q` na nossa máquina e passou
- [ ] Rodamos `python scripts/cenarios_demo.py` e entendemos cada cenário
- [ ] Sabemos explicar por que o CPF é guardado como HMAC e a senha como argon2
- [ ] Sabemos explicar a limitação das f-strings e por que os sinks também rodam o detector
- [ ] Alteramos/adaptamos algo por conta própria (descrever abaixo)

**Alterações do grupo:** _(preencher)_
