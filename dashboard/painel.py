"""Dashboard Executivo: Risco Cidadão. Rode com: streamlit run dashboard/painel.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from ia.tradutor import traduzir_alerta
from modulo_pii.auditoria import ler_eventos
from modulo_pii.risco import resumo

st.set_page_config(page_title="SmartRoad · Risco Cidadão", page_icon="🛡️", layout="wide")
st.title("🛡️ SmartRoad · Risco Cidadão")
st.caption("Monitoramento de dados pessoais (PII) · Cybersecurity GS 2026.2 · dados simulados")

if st.button("🔄 Atualizar"):
    st.rerun()

eventos = ler_eventos()
r = resumo(eventos)

cores = {"Baixo": "🟢", "Médio": "🟡", "Alto": "🟠", "Crítico": "🔴"}
c1, c2, c3, c4 = st.columns(4)
c1.metric("Risco Cidadão", f"{r['score']}/100", f"{cores[r['nivel']]} {r['nivel']}", delta_color="off")
c2.metric("Vazamentos bloqueados", r["bloqueados"])
c3.metric("Vazamentos ocorridos", r["vazados"])
c4.metric("Eventos auditados", r["total_eventos"])
st.progress(r["score"] / 100)

esq, dir_ = st.columns(2)
with esq:
    st.subheader("PII detectada por tipo")
    if r["por_tipo"]:
        st.bar_chart(pd.Series(r["por_tipo"], name="ocorrências"))
    else:
        st.info("Nenhuma PII detectada ainda. Rode `python scripts/cenarios_demo.py`.")
with dir_:
    st.subheader("Último alerta (traduzido para o cidadão)")
    com_pii = [e for e in eventos if e.get("tipos")]
    if com_pii:
        ultimo = com_pii[-1]
        alerta = traduzir_alerta(ultimo)
        st.warning(alerta["texto"])
        st.caption(f"Origem do texto: {'IA' if alerta['fonte'] == 'llm' else 'texto fixo (fallback)'} · "
                   f"destino: {ultimo['destino']} · {'bloqueado' if ultimo['bloqueado'] else 'NÃO bloqueado'}")
    else:
        st.success("Sem alertas.")

st.subheader("Trilha de auditoria (sem dados sensíveis)")
if eventos:
    st.dataframe(pd.DataFrame(eventos[::-1]).head(50), use_container_width=True, hide_index=True)
