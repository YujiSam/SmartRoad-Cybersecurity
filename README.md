# SmartRoad · Cybersecurity (GS 2026.2 · FIAP · Engenharia de Software 3º ano)

## Ficha da CitizenTech

| Campo | Preencher |
|---|---|
| Nome da CitizenTech | **SmartRoad** |
| Cidade e bairro | São Paulo – Paulista |
| Cidadão beneficiado | Pessoas com deficiência, idosos e quem anda com carrinho de bebê |
| Problema, em uma frase | "Não sei se o caminho até meu destino é seguro e acessível, e os problemas da calçada não chegam a quem pode resolver." |
| Como funciona | Moradores reportam buracos, calçadas quebradas, iluminação e segurança. Os relatos reduzem a nota dos trechos, e a rota sugerida evita os piores. |
| O que cada parte faz | Esta entrega protege os dados pessoais (CPF, senha, perfil de mobilidade) em toda a solução: detecta PII, rastreia o dado (taint), bloqueia vazamentos, traduz alertas via IA e mostra o Risco Cidadão. |
| Link do repositório | _(preencher)_ |
| Indicador de impacto | Relatos resolvidos · Risco Cidadão (0–100) · vazamentos bloqueados |
| ODS conectados | **10** (reduzir desigualdades), **11** (cidades sustentáveis), **3** (saúde e bem-estar) |

**Integrantes**

| Integrante | RM |
|---|---|
| Gustavo Yuji Osugi | 555034 |
| Gustavo Viega | 555885 |
| Kaio Drago Lima Souza | 556095 |
| Vitor Rivas Cardoso | 556404 |
| Otavio Santos de Lima Ferrão | 556452 |

> Dados 100% **simulados**: nenhum dado pessoal real é usado (ver `dados/README.md`).

## O que foi entregue (3 missões + dashboard)

| Entrega | Onde está |
|---|---|
| 01 Mapeamento de PII (CPF, saúde, senha, e-mail, telefone) | `modulo_pii/regras.py`, `validadores.py`, `detector.py` |
| 02 Taint Analysis (source → propagação → sanitizer → sink) | `modulo_pii/taint.py`, `sanitizers.py`, `sinks.py`, `middleware.py` |
| 03 Tradução via IA (só metadados) com fallback | `ia/tradutor.py`, `prompts.py`, `fallback.py` |
| Dashboard Risco Cidadão | `dashboard/painel.py`, `modulo_pii/risco.py` |
| Auditoria (JSON Lines, sem dado sensível) | `modulo_pii/auditoria.py` → `logs/auditoria.jsonl` |
| Evidências | `evidencias/` |

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # opcional; funciona sem editar

pytest testes -q                                       # 34 testes
python scripts/cenarios_demo.py                        # roda os 5 cenários e gera evidências
uvicorn app.main:app --reload                          # API em http://127.0.0.1:8000/docs
streamlit run dashboard/painel.py                      # dashboard em http://localhost:8501
```

Para ligar a IA: no `.env`, `USAR_LLM=true` e `GEMINI_API_KEY=...`. Sem isso (ou se a API falhar), o sistema usa textos fixos.

## Como o CPF é protegido (CPF é o login)

| Dado | Armazenamento | Motivo |
|---|---|---|
| CPF (busca no login) | `HMAC-SHA256(PEPPER, cpf)` | encontrar o usuário sem guardar o CPF |
| CPF (exibição) | só os 2 últimos dígitos | mostrar `***.***.***-25` |
| Senha | `argon2id` | nunca em claro, nunca em log |
| Perfil de mobilidade (saúde) | cifrado com Fernet | dado sensível (LGPD) |
| Texto livre do relato | sanitizado **antes** de salvar | o morador pode digitar o CPF sem perceber |

## Taint Analysis: como funciona

```
Cidadão digita CPF/senha ──► SOURCE: marcar() / marcar_auto()  → valor vira Tainted (carrega a tag)
        │ propagação: +, %, .format, upper/lower/strip/replace, fatiamento
        ▼
SANITIZER: mascarar_cpf() / sanitizar_texto()  → str limpa
        ▼
SINK: sink_log · sink_resposta · sink_arquivo · sink_llm
        ├─ com PII/tag  → BLOQUEIA (VazamentoBloqueado) + registra em auditoria
        └─ limpo        → permite + registra em auditoria
Última linha de defesa: TaintMiddleware inspeciona toda resposta JSON da API.
```

**Limitação conhecida:** f-strings do Python devolvem `str` comum e perdem a tag. Por isso todo sink
também roda o detector de PII (defesa em profundidade). Isso está coberto em
`testes/test_taint.py::test_limitacao_fstring...`.

## Cenários de demonstração (rotas `/demo/*`, só para a demo)

| # | Cenário | Resultado esperado |
|---|---|---|
| 1 | CPF cru vai para o log | **Bloqueado** |
| 2 | CPF mascarado vai para o log | **Permitido** |
| 3 | Senha na resposta da API | **Bloqueado** |
| 4 | Rota "esqueceu" o sink e devolve CPF | **Bloqueado pelo middleware** |
| 5 | Relato com CPF no texto | Publicado **mascarado** + aviso ao cidadão |

## Estrutura

```
cybersecurity/
├── app/            # API FastAPI (cadastro, login por CPF, relatos, rotas, demo)
├── modulo_pii/     # <<< entrega principal: PII, taint, sinks, auditoria, risco
├── ia/             # tradutor LLM + fallback
├── dashboard/      # Streamlit
├── dados/          # dados simulados
├── testes/         # 34 testes (pytest)
├── scripts/        # cenarios_demo.py
└── evidencias/     # log de auditoria, antes/depois da IA, prints e vídeo
```

## Critérios do professor → onde comprovar

| Critério | Pts | Evidência |
|---|---|---|
| Robustez do motor de Parsing PII | 3,0 | `testes/test_cpf.py`, `test_detector.py` (positivos, negativos, bordas) |
| Eficácia do Taint Analysis | 3,0 | `testes/test_taint.py`, `evidencias/taint_auditoria.log`, `prints_taint/` |
| Inovação com IA na remediação | 2,0 | `evidencias/antes_depois_ia.md`, `ia/` |
| Dashboard Executivo (Risco Cidadão) | 2,0 | `evidencias/dashboard_print.png` e vídeo |
