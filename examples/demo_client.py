"""Demonstração: fala com o servidor mini-tars por stdio, como um assistente faria.

Uso (no venv do projeto):  python examples/demo_client.py
Usa um banco temporário e só fatos inventados; não toca no seu banco de uso.
"""
import json
import sys
import tempfile
from pathlib import Path

import anyio
from mcp import Client, StdioServerParameters


def dados(result):
    """O resultado vem como JSON no texto (e, em alguns casos, também estruturado)."""
    if result.structured_content is not None:
        return result.structured_content
    return json.loads(result.content[0].text)


def show(titulo, result):
    print(f"\n== {titulo}")
    if result.is_error:
        print("ERRO:", result.content[0].text)
    else:
        print(json.dumps(dados(result), ensure_ascii=False, indent=2))


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "demo.db"
        params = StdioServerParameters(command=sys.executable,
                                       args=["-m", "mini_tars.cli", "serve", "--db", str(db)])
        async with Client(params) as c:
            print("Ferramentas:", [t.name for t in (await c.list_tools()).tools])
            a = dados(await c.call_tool("remember", {"text": "O plano custa R$ 79 por mês"}))["id"]
            show("guardou o fato antigo", await c.call_tool("list_recent", {}))
            b = dados(await c.call_tool("remember", {"text": "O plano custa R$ 89 por mês", "supersedes": a}))["id"]
            show("busca padrão: só o preço novo", await c.call_tool("search", {"query": "preço do plano"}))
            show("busca com histórico: os dois", await c.call_tool("search", {"query": "plano custa", "include_superseded": True}))
            show("erro esperado: texto vazio", await c.call_tool("remember", {"text": "  "}))
            show("apagou o fato novo", await c.call_tool("forget", {"id": b}))
        print("\nFim. O banco temporário foi apagado.")


anyio.run(main)
