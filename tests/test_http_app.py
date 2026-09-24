"""Testes de segurança do modo HTTP (RNF-01, R13, ADR-0005). Só dados fictícios."""
import json

import pytest
from starlette.testclient import TestClient

from mini_tars.config import Config
from mini_tars.http_app import ConfigError, build_http_app
from mini_tars.service import Service
from mini_tars.store import Store


def make(tmp_path, **kwargs):
    svc = Service(Store(tmp_path / "m.db"))
    config = Config(db_path=tmp_path / "m.db", **kwargs)
    return svc, config


def test_recusa_iniciar_fora_do_local_sem_token(tmp_path):
    svc, config = make(tmp_path, host="0.0.0.0", port=8765, token=None)
    with pytest.raises(ConfigError):
        build_http_app(svc, config)


def test_local_funciona_sem_token(tmp_path):
    svc, config = make(tmp_path, host="127.0.0.1", port=8765, token=None)
    app = build_http_app(svc, config)
    with TestClient(app) as c:
        assert c.get("/saude").json() == {"ok": True}
        r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                   headers={"accept": "application/json, text/event-stream"})
        assert r.status_code != 401  # sem exigência de token no modo local


def test_fora_do_local_com_token_exige_cabecalho_de_autorizacao(tmp_path):
    svc, config = make(tmp_path, host="0.0.0.0", port=8765, token="segredo-de-teste")
    app = build_http_app(svc, config)
    with TestClient(app, base_url="http://0.0.0.0:8765") as c:
        sem_token = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                           headers={"accept": "application/json, text/event-stream", "host": "0.0.0.0:8765"})
        assert sem_token.status_code == 401

        token_errado = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                              headers={"accept": "application/json, text/event-stream", "host": "0.0.0.0:8765",
                                       "authorization": "Bearer errado"})
        assert token_errado.status_code == 401

        com_token = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                           headers={"accept": "application/json, text/event-stream", "host": "0.0.0.0:8765",
                                    "authorization": "Bearer segredo-de-teste"})
        assert com_token.status_code != 401

        # /saude não é ferramenta MCP e não exige token neste desenho; documentado, não escondido
        assert c.get("/saude", headers={"host": "0.0.0.0:8765"}).status_code == 200


def test_host_desconhecido_e_recusado(tmp_path):
    """Proteção contra DNS rebinding: só o Host configurado é aceito (R13)."""
    svc, config = make(tmp_path, host="127.0.0.1", port=8765, token=None)
    app = build_http_app(svc, config)
    with TestClient(app, base_url="http://127.0.0.1:8765") as c:
        r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                   headers={"accept": "application/json, text/event-stream", "host": "evil.example.com:8765"})
        assert r.status_code == 421


def test_origin_de_outro_site_e_recusada(tmp_path):
    """Página aberta no navegador em outro site não consegue chamar o servidor local (R13)."""
    svc, config = make(tmp_path, host="127.0.0.1", port=8765, token=None)
    app = build_http_app(svc, config)
    with TestClient(app, base_url="http://127.0.0.1:8765") as c:
        r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                   headers={"accept": "application/json, text/event-stream", "host": "127.0.0.1:8765",
                            "origin": "https://site-malicioso.example"})
        assert r.status_code == 403


def _porta_livre() -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_host_e_origin_protegidos_tambem_fora_do_local(tmp_path):
    """Fora do localhost o SDK não aplica proteção sozinho; é `_security_settings` que aplica (R13)."""
    svc, config = make(tmp_path, host="0.0.0.0", port=8765, token="segredo-de-teste")
    app = build_http_app(svc, config)
    with TestClient(app, base_url="http://0.0.0.0:8765") as c:
        cabecalhos = {"accept": "application/json, text/event-stream", "host": "0.0.0.0:8765",
                      "authorization": "Bearer segredo-de-teste"}
        r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                   headers={**cabecalhos, "host": "evil.example.com:8765"})
        assert r.status_code == 421
        r = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                   headers={**cabecalhos, "origin": "https://site-malicioso.example"})
        assert r.status_code == 403


def test_host_roteavel_de_verdade_e_aceito_e_outro_e_recusado(tmp_path):
    """`config.host` não precisa ser 127.0.0.1/0.0.0.0: também funciona com um IP real da rede."""
    svc, config = make(tmp_path, host="192.168.1.10", port=8765, token="segredo-de-teste")
    app = build_http_app(svc, config)
    with TestClient(app, base_url="http://192.168.1.10:8765") as c:
        cabecalhos = {"accept": "application/json, text/event-stream", "host": "192.168.1.10:8765",
                      "authorization": "Bearer segredo-de-teste"}
        ok = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"}, headers=cabecalhos)
        assert ok.status_code != 421
        outro = c.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       headers={**cabecalhos, "host": "192.168.1.99:8765"})
        assert outro.status_code == 421


def test_ferramentas_funcionam_de_ponta_a_ponta_por_http(tmp_path):
    """Um cliente MCP real fala com o app HTTP montado no FastAPI (RF-09)."""
    port = _porta_livre()
    svc, config = make(tmp_path, host="127.0.0.1", port=port, token=None)
    app = build_http_app(svc, config)
    import threading

    import uvicorn

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    import time
    for _ in range(100):
        if getattr(server, "started", False):
            break
        time.sleep(0.05)

    import anyio
    from mcp import Client

    def dados(result):
        if result.structured_content is not None:
            return result.structured_content
        return json.loads(result.content[0].text)

    async def main():
        async with Client(f"http://127.0.0.1:{port}/mcp") as c:
            names = {t.name for t in (await c.list_tools()).tools}
            assert names == {"remember", "search", "forget", "list_recent"}
            r = await c.call_tool("remember", {"text": "fato fictício por http"})
            fid = dados(r)["id"]
            s = await c.call_tool("search", {"query": "fato fictício http"})
            assert dados(s)["results"][0]["id"] == fid

    try:
        anyio.run(main)
    finally:
        server.should_exit = True
        thread.join(timeout=5)
