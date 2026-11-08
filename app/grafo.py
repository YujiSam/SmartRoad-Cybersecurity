"""Grafo SIMULADO de um bairro (10 pontos). Cada trecho tem nota de acessibilidade 0-100.

Dados fictícios para a demo. A nota cai conforme há relatos abertos no trecho.
"""
import heapq

NOS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
# (origem, destino, metros)
TRECHOS = {
    "A-B": ("A", "B", 200), "B-C": ("B", "C", 150), "C-D": ("C", "D", 250),
    "A-E": ("A", "E", 180), "E-F": ("E", "F", 220), "F-D": ("F", "D", 200),
    "B-F": ("B", "F", 300), "D-G": ("D", "G", 160), "G-H": ("G", "H", 140),
    "F-I": ("F", "I", 210), "I-J": ("I", "J", 170), "H-J": ("H", "J", 190),
}
PENALIDADE = {"buraco": 25, "calcada": 30, "iluminacao": 15, "seguranca": 20}


def nota_trecho(trecho: str, relatos_abertos: list[dict]) -> int:
    nota = 100
    for r in relatos_abertos:
        if r["trecho"] == trecho:
            nota -= PENALIDADE.get(r["tipo"], 10)
    return max(0, nota)


def melhor_rota(origem: str, destino: str, notas: dict[str, int]) -> dict | None:
    """Dijkstra com custo = metros x (1 + (100-nota)/50): trechos ruins 'ficam mais longos'."""
    adj: dict[str, list] = {n: [] for n in NOS}
    for tid, (a, b, m) in TRECHOS.items():
        custo = m * (1 + (100 - notas.get(tid, 100)) / 50)
        adj[a].append((b, custo, tid))
        adj[b].append((a, custo, tid))
    fila, vistos = [(0.0, origem, [], [])], set()
    while fila:
        custo, no, caminho, trechos = heapq.heappop(fila)
        if no in vistos:
            continue
        vistos.add(no)
        caminho, trechos = caminho + [no], trechos
        if no == destino:
            return {"caminho": caminho, "trechos": trechos,
                    "nota_media": round(sum(notas.get(t, 100) for t in trechos) / max(1, len(trechos)))}
        for viz, c, tid in adj[no]:
            if viz not in vistos:
                heapq.heappush(fila, (custo + c, viz, caminho, trechos + [tid]))
    return None
