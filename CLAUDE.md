# mini-Tars

Servidor de memória (MCP) para assistentes de IA, feito em Python com FastAPI.
Status do projeto: fase 4 (entregar) aprovada em 2026-09-24. MVP completo (todos os requisitos M).

## Como navegar
Leia primeiro `CONTEXT.md` (índice). Estado atual em `docs/handoff.md`. Decisões em `docs/decisions.md`.

## Regras permanentes
- Nunca ler nem editar `.env`, chaves ou qualquer credencial.
- Nunca fazer deploy, nem publicar nada: só o Breno faz.
- Toda mudança de comportamento precisa de teste ou de caso em `evals/`.
- Fuso horário sempre America/Sao_Paulo, nunca o padrão do servidor.
- Dado que não puder ser interpretado com confiança: perguntar, nunca gravar.
- Outras pessoas vão usar (auto-hospedado): nenhum dado real de ninguém em testes, fixtures ou logs; o servidor escuta só em 127.0.0.1 por padrão.
- Se a especificação estiver ambígua, registrar a dúvida em `docs/handoff.md` em vez de adivinhar.
- Se o Breno não conseguir explicar um diff, o diff não é aceito.

## Fluxo
Especificação em `01-definir/` -> construtor implementa -> revisor (contexto separado, só leitura) revisa -> Breno aprova.

## Comandos
- Testes: `python -m pytest -q`
- Medir a busca: `python evals/run_pkg.py -v`
- Servidor MCP (stdio): `mini-tars serve` (banco em `MINI_TARS_DB` ou `--db`)
- Servidor MCP (HTTP local): `mini-tars serve --http` (token fora do local em `MINI_TARS_TOKEN`)
- Exportar/importar: `mini-tars export saida.json` / `mini-tars import saida.json` (import exige banco vazio)
