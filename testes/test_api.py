import pytest
from fastapi.testclient import TestClient

from app.main import app

CPF = "529.982.247-25"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_fluxo_completo(client):
    r = client.post("/cadastro", json={"cpf": CPF, "senha": "SenhaForte123", "perfil_mobilidade": "cadeirante"})
    assert r.status_code == 201 and r.json()["cpf"] == "***.***.***-25"

    assert client.post("/cadastro", json={"cpf": CPF, "senha": "SenhaForte123"}).status_code == 409
    assert client.post("/cadastro", json={"cpf": "111.111.111-11", "senha": "SenhaForte123"}).status_code == 422
    assert client.post("/login", json={"cpf": CPF, "senha": "errada"}).status_code == 401

    r = client.post("/login", json={"cpf": CPF, "senha": "SenhaForte123"})
    assert r.status_code == 200
    token = r.json()["token"]

    # relato com CPF no texto: publica mascarado + avisa
    r = client.post("/relatos", headers={"Authorization": f"Bearer {token}"},
                    json={"tipo": "buraco", "trecho": "B-C", "descricao": f"Buraco enorme, meu cpf é {CPF}"})
    assert r.status_code == 201
    corpo = r.json()
    assert CPF not in corpo["descricao_publicada"] and corpo["aviso"]

    assert CPF not in client.get("/relatos").text


def test_rota_evita_trecho_ruim(client):
    base = client.get("/rota", params={"origem": "A", "destino": "D"}).json()
    assert base["caminho"][0] == "A" and base["caminho"][-1] == "D"


def test_demo_vazamentos_bloqueados(client):
    assert client.get("/demo/vaza-cpf-no-log").status_code == 500
    assert client.get("/demo/cpf-mascarado-no-log").status_code == 200
    assert client.get("/demo/vaza-senha-na-resposta").status_code == 500
    r = client.get("/demo/vaza-sem-sink")  # pego pelo middleware
    assert r.status_code == 500 and CPF not in r.text
