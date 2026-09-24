"""Linha de comando: `mini-tars serve` (stdio ou --http), `export`, `import`, `--version`."""
import argparse
import sqlite3
import sys
from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .config import Config
from .export_import import export_to_file, import_from_file
from .http_app import ConfigError, build_http_app
from .mcp_server import build_server
from .models import DomainError
from .service import Service
from .store import Store


def _version() -> str:
    try:
        return version("mini-tars")
    except PackageNotFoundError:
        return "0.0.1"


def make_service(config: Config) -> Service:
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    return Service(Store(config.db_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mini-tars", description="Memória de fatos para assistentes de IA (MCP).")
    parser.add_argument("--version", action="version", version=f"mini-tars {_version()}")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="inicia o servidor MCP")
    serve.add_argument("--db", help="caminho do banco (padrão: diretório de dados do usuário)")
    serve.add_argument("--http", action="store_true", help="usa HTTP local em vez de stdio (padrão: stdio)")
    serve.add_argument("--host", help="interface do modo HTTP (padrão: 127.0.0.1; RNF-01)")
    serve.add_argument("--port", type=int, help="porta do modo HTTP (padrão: 8765)")

    exportar = sub.add_parser("export", help="exporta os fatos para um arquivo JSON (RF-08)")
    exportar.add_argument("arquivo", help="caminho do arquivo de saída")
    exportar.add_argument("--db", help="caminho do banco (padrão: diretório de dados do usuário)")

    importar = sub.add_parser("import", help="importa fatos de um arquivo JSON, em banco vazio (RF-08)")
    importar.add_argument("arquivo", help="caminho do arquivo de entrada")
    importar.add_argument("--db", help="caminho do banco (padrão: diretório de dados do usuário)")

    args = parser.parse_args(argv)
    resultado = None

    try:
        config = Config.from_env()
        if getattr(args, "db", None) is not None:
            if not args.db.strip():
                raise ValueError("--db está vazio.")
            config = replace(config, db_path=Path(args.db).expanduser())

        if args.command == "serve":
            if args.host is not None:
                config = replace(config, host=args.host)
            if args.port is not None:
                config = replace(config, port=args.port)
            if not 0 <= config.port <= 65535:
                raise ValueError(f"Porta {config.port} fora do intervalo 0-65535.")
            service = make_service(config)
            if args.http:
                app = build_http_app(service, config)
        elif args.command == "export":
            resultado = export_to_file(make_service(config), Path(args.arquivo))
        elif args.command == "import":
            resultado = import_from_file(make_service(config), Path(args.arquivo))
    except (DomainError, ConfigError, OSError, sqlite3.Error, ValueError) as exc:
        # Mensagem curta e legível em vez de traceback; nunca inclui texto de fatos.
        message = exc.message if isinstance(exc, DomainError) else f"{type(exc).__name__}: {exc}"
        print(f"mini-tars: não foi possível concluir. {message}", file=sys.stderr)
        return 2

    if args.command == "export":
        print(f"mini-tars: {resultado} fato(s) exportado(s) para {args.arquivo}", file=sys.stderr)
        return 0
    if args.command == "import":
        print(f"mini-tars: {resultado} fato(s) importado(s) de {args.arquivo}", file=sys.stderr)
        return 0

    # Nada em stdout além do protocolo (stdio) ou das respostas HTTP; mensagens vão para stderr.
    if args.http:
        import uvicorn
        print(f"mini-tars: banco em {config.db_path}; HTTP em {config.host}:{config.port}", file=sys.stderr)
        try:
            uvicorn.run(app, host=config.host, port=config.port, log_level="warning")
        except (OSError, OverflowError, ValueError) as exc:
            # Porta fora de 0-65535, host inválido, porta já em uso etc.
            print(f"mini-tars: não foi possível iniciar. {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
    else:
        print(f"mini-tars: banco em {config.db_path}", file=sys.stderr)
        build_server(service).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
