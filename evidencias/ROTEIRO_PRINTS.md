# Roteiro de prints e vídeo (siga na ordem)

Preparação: `pip install -r requirements.txt`, terminal em tela cheia, fonte grande.

## PRINT 1: testes passando
Comando: `pytest testes -q`
Tire o print quando aparecer `35 passed`.
Salvar: `evidencias/prints_taint/01_testes.png`

## PRINT 2: cenários de Taint Analysis
Comando: `python scripts/cenarios_demo.py`
Tire o print quando o terminal terminar e mostrar a linha final `Risco Cidadão: ... Evidências gravadas`.
O print deve mostrar os 5 cenários com ✅ (bloqueado e permitido).
Salvar: `evidencias/prints_taint/02_cenarios.png`

## PRINT 3: log de auditoria sem dado sensível
Comando: `head -n 8 evidencias/taint_auditoria.log` (Windows: `Get-Content evidencias\taint_auditoria.log -Head 8`)
Tire o print com as linhas `"bloqueado": true` visíveis e nenhum CPF cru.
Salvar: `evidencias/prints_taint/03_auditoria.png`

## PRINT 4: dashboard (só depois do print 2!)
Comando: `streamlit run dashboard/painel.py`
Tire o print quando o painel mostrar o indicador Risco Cidadão, os gráficos por tipo e o "Último alerta".
Salvar: `evidencias/dashboard_print.png`

## VÍDEO do dashboard (com atividade)
1. Painel aberto, indicador baixo.
2. Em outro terminal: `uvicorn app.main:app` e abra `http://127.0.0.1:8000/docs`.
3. Execute `/demo/vaza-cpf-no-log` e `/demo/vaza-senha-na-resposta` no Swagger (dá 500, é o esperado).
4. Volte ao painel, clique em **Atualizar** e mostre o indicador e o alerta mudando.
Salvar o vídeo (ou link do YouTube não listado) em `evidencias/`.
