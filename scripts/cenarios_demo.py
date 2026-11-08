"""Roda os cenários do Taint Analysis e gera evidências + eventos para o dashboard.

Uso (com a API NÃO precisando estar de pé):  python scripts/cenarios_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app
from ia.tradutor import traduzir_alerta
from modulo_pii.auditoria import ARQUIVO, ler_eventos
from modulo_pii.risco import resumo

EVID = Path(__file__).resolve().parent.parent / "evidencias"
CPF = "529.982.247-25"


def linha(titulo, resp, esperado):
    ok = "✅" if resp.status_code == esperado else "❌"
    print(f"{ok} {titulo:<58} HTTP {resp.status_code} (esperado {esperado})")
    return resp


def main():
    ARQUIVO.unlink(missing_ok=True)
    with TestClient(app) as c:
        print("\n=== Cenários de Taint Analysis ===")
        linha("1) CPF cru -> LOG                       (BLOQUEADO)", c.get("/demo/vaza-cpf-no-log"), 500)
        linha("2) CPF mascarado -> LOG                 (PERMITIDO)", c.get("/demo/cpf-mascarado-no-log"), 200)
        linha("3) Senha -> RESPOSTA da API             (BLOQUEADO)", c.get("/demo/vaza-senha-na-resposta"), 500)
        linha("4) Rota sem sink -> middleware          (BLOQUEADO)", c.get("/demo/vaza-sem-sink"), 500)

        print("\n=== Fluxo real do SmartRoad ===")
        c.post("/cadastro", json={"cpf": CPF, "senha": "SenhaForte123", "perfil_mobilidade": "cadeirante"})
        tk = c.post("/login", json={"cpf": CPF, "senha": "SenhaForte123"}).json().get("token", "")
        c.post("/login", json={"cpf": CPF, "senha": "errada"})
        h = {"Authorization": f"Bearer {tk}"}
        r = linha("5) Relato com CPF no texto -> publicado MASCARADO", c.post(
            "/relatos", headers=h, json={"tipo": "buraco", "trecho": "B-C",
                                         "descricao": f"Buraco grande, sou cadeirante. Meu cpf é {CPF}"}), 201)
        print("   publicado:", r.json().get("descricao_publicada"))
        print("   aviso    :", r.json().get("aviso"))
        c.post("/relatos", headers=h, json={"tipo": "calcada", "trecho": "A-B", "descricao": "Calçada quebrada"})
        rota = c.get("/rota", params={"origem": "A", "destino": "D"}).json()
        print("   rota A->D evitando trechos ruins:", " -> ".join(rota["caminho"]), f"(nota média {rota['nota_media']})")

    eventos = ler_eventos()
    r = resumo(eventos)
    print(f"\n=== Risco Cidadão: {r['score']}/100 ({r['nivel']}) · bloqueados {r['bloqueados']} · vazados {r['vazados']} ===")

    EVID.mkdir(exist_ok=True)
    (EVID / "taint_auditoria.log").write_text(ARQUIVO.read_text(encoding="utf-8"), encoding="utf-8")

    pii = [e for e in eventos if e["tipos"]]
    exemplo = pii[0]
    alerta = traduzir_alerta(exemplo)
    (EVID / "antes_depois_ia.md").write_text(
        "# Antes e depois: tradução do alerta\n\n"
        "## Antes (log técnico de auditoria)\n```json\n"
        f"{exemplo}\n```\n\n"
        f"## Depois (alerta ao cidadão, fonte: {alerta['fonte']})\n> {alerta['texto']}\n", encoding="utf-8")
    print("Evidências gravadas em evidencias/")


if __name__ == "__main__":
    main()
