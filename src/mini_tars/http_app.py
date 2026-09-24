"""Modo HTTP: FastAPI com o app MCP montado (RF-09, RNF-01, R13; ADR-0003, ADR-0005).

Escuta em 127.0.0.1 por padrão. Escutar em outra interface exige um token
(variável MINI_TARS_TOKEN) e o servidor recusa iniciar sem ele. `Host` e `Origin`
são validados pelo próprio SDK do MCP (`TransportSecuritySettings`), contra
páginas de outros sites chamando o servidor local pelo navegador.
"""
import hmac

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mcp.server.transport_security import TransportSecuritySettings

from .config import LOCAL_HOSTS, Config
from .mcp_server import build_server
from .service import Service


class ConfigError(Exception):
    """Configuração insegura para o modo HTTP; o servidor não deve iniciar."""


def _security_settings(config: Config) -> TransportSecuritySettings:
    """`allowed_hosts`/`allowed_origins`: só o endereço configurado, na porta configurada."""
    hosts = {f"{h}:{config.port}" for h in LOCAL_HOSTS} | {f"{config.host}:{config.port}"}
    origins = {f"{esquema}://{h}" for h in hosts for esquema in ("http", "https")}
    return TransportSecuritySettings(allowed_hosts=sorted(hosts), allowed_origins=sorted(origins))


def build_http_app(service: Service, config: Config) -> FastAPI:
    """Constrói o app HTTP. Levanta `ConfigError` se a configuração for insegura (RNF-01)."""
    if not config.is_local_host and not config.token:
        raise ConfigError(
            "Escutar em outra interface que não seja local exige um token "
            "(variável de ambiente MINI_TARS_TOKEN)."
        )

    mcp = build_server(service)
    mcp_app = mcp.streamable_http_app(transport_security=_security_settings(config), host=config.host)

    app = FastAPI(lifespan=mcp_app.router.lifespan_context)

    @app.get("/saude")
    def saude() -> dict:
        return {"ok": True}

    if not config.is_local_host:
        token = config.token

        @app.middleware("http")
        async def _exigir_token(request: Request, call_next):
            if request.url.path.startswith("/mcp"):
                esperado = f"Bearer {token}"
                recebido = request.headers.get("authorization", "")
                if not hmac.compare_digest(recebido, esperado):
                    return JSONResponse({"error": "token ausente ou inválido"}, status_code=401)
            return await call_next(request)

    app.mount("/", mcp_app)
    return app
