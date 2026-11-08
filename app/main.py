from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import config
from .database import init_db
from .routes import cadastro, demo_vazamento, login, relatos, rotas
from modulo_pii.middleware import TaintMiddleware
from modulo_pii.sinks import VazamentoBloqueado


@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(
    title="SmartRoad API",
    description="Rotas urbanas acessíveis + zeladoria colaborativa, com proteção de PII (Cybersecurity GS 2026.2).",
    lifespan=lifespan,
)
app.add_middleware(TaintMiddleware)


@app.exception_handler(VazamentoBloqueado)
async def _vazamento(_req, exc: VazamentoBloqueado):
    return JSONResponse(status_code=500, content={
        "erro": "Vazamento de dado pessoal bloqueado.", "destino": exc.destino, "tipos": exc.tipos})


for r in (cadastro.router, login.router, relatos.router, rotas.router, demo_vazamento.router):
    app.include_router(r)


@app.get("/")
def raiz():
    return {"projeto": "SmartRoad", "docs": "/docs"}
