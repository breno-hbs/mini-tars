# ADR-0003: Servidor MCP por stdio (padrão) e HTTP local (opcional)

- Status: aceito (Breno, 2026-09-23); verificação técnica concluída em 2026-09-23 (ver abaixo)
- Data: 2026-09-23
- Relacionado: RF-09, RNF-01; R2

## Contexto
Clientes de assistentes de IA costumam iniciar servidores MCP locais como processos filhos e falar por stdio. Um modo HTTP é útil para testes e para clientes que se conectam por rede. O objetivo de aprendizado inclui FastAPI.

## Decisão
- `mini-tars serve` fala MCP por **stdio** (padrão: sem porta aberta, sem risco de rede).
- `mini-tars serve --http` sobe o transporte HTTP do MCP, montado em uma aplicação FastAPI, escutando em **127.0.0.1**. Escutar em outra interface exige token e é recusado sem ele.
- Usar o SDK Python oficial do MCP em vez de implementar o protocolo à mão.

## Verificação técnica (2026-09-23)
Fontes: README do repositório oficial `modelcontextprotocol/python-sdk` (lido no dia) e o código do pacote `mcp` 2.2.0 instalado em ambiente isolado. Não li o site de documentação completo.
- A linha estável atual do SDK é a **v2** (`pip install mcp` instala a 2.x). A API mudou em relação a tutoriais antigos: o servidor é `mcp.server.MCPServer` (não `FastMCP`) e o cliente é `mcp.Client`. Exige Python 3.10 ou superior. Fixar `mcp>=2,<3`.
- **stdio** funciona: um `Client` com `StdioServerParameters` listou e chamou uma ferramenta.
- **Streamable HTTP** funciona: `MCPServer.streamable_http_app(host="127.0.0.1")` devolve um app Starlette; servido com uvicorn, o `Client("http://127.0.0.1:PORT/mcp")` chamou a ferramenta.
- **Montagem no FastAPI** funciona com `FastAPI(lifespan=mcp_app.router.lifespan_context)` e `app.mount("/", mcp_app)`; uma rota própria do FastAPI (`/saude`) coexistiu com o endpoint `/mcp`. Sem passar o `lifespan`, a montagem falha em versões antigas (issue conhecida); manter isso num teste.
- **Proteção contra origem cruzada e DNS rebinding já vem no SDK** quando o host é local: `Origin` externa recebeu 403 e `Host` externo recebeu 421; `Origin` local passou (200). Configura-se por `TransportSecuritySettings(allowed_hosts, allowed_origins)`. Isso cobre boa parte do R13; falta testar no nosso próprio app e o caso de escutar em outra interface.
- **Token (RNF-01)**: o SDK tem parâmetros de autenticação, mas não os usei; a proposta é um middleware ASGI simples que exige `Authorization: Bearer <token>` quando o host não for local. A ser implementado e testado na fatia do modo HTTP.
- Comportamento com muitos clientes: o app tem limite de sessões e de tamanho de corpo por padrão; anotar os valores padrão ao implementar.
O código descartável do teste não foi mantido no repositório.

## Alternativas consideradas
| Alternativa | Por que não |
| --- | --- |
| Só HTTP | Abre uma porta sempre, sem necessidade para o uso local principal |
| Só stdio | Simples, mas tira o FastAPI do projeto e dificulta teste de segurança de rede |
| Implementar o protocolo sem SDK | Mais aprendizado de protocolo, porém mais código para manter e mais chance de erro |

## Consequências
- O caminho comum (stdio) tem superfície de ataque de rede zero.
- O modo HTTP exige controles próprios (RNF-01, R13 sobre origens).
