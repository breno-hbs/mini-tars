# Handoff

Sobrescrito a cada etapa. Estado atual, não histórico (o histórico está em `decisions.md` e no Git).

**Data:** 2026-09-24
**Fase:** 4 (entregar) aprovada em 2026-09-24. Fases 0 a 3 concluídas.

## Feito
- Estrutura do projeto, `CLAUDE.md`, `CONTEXT.md`, `depth.md`.
- Decisões do Breno registradas: desenvolvedores como segmento, auto-hospedagem, entrevistas com usuários puladas.
- Pesquisa de concorrentes (H5) em `00-descobrir/competitors.md`: o Basic Memory já faz o essencial do mini-Tars.
- Rumo decidido: projeto de aprendizado (opção 1), registrado em `decisions.md`.
- `evals/`: README, `cases.example.json` (3 fatos), `cases.json` (30 fatos fictícios e 35 perguntas em rascunho, 6 sem resposta) e `run_baseline.py` (hit@1, hit@3, resultado por tipo e aviso de rascunho).
- Experimento 1 feito (`evals/experimento-01.md`, `queries-exp01.json`): falha parcial.
- Teste H1 feito com as perguntas do Breno: hit@3 72%, hit@1 41% (`decisions.md`). Arquivos: `evals/cases.json` (gold ajustado em 3 perguntas), `evals/cases.original-gold.json` (exatamente como enviado) e `evals/cases.rascunho-assistente.json` (rascunho antigo).
- Fase 3 aprovada (visão, requisitos, arquitetura, ADRs 0001-0005 aceitos). SDK do MCP verificado (ADR-0003).
- Fase 4: esqueleto (pyproject, LICENSE MIT, CI, `.claude/` com agentes e permissões) e fatias 1 a 3 prontas: `models`, `config`, `store`, `service`, `search`, `mcp_server`, `cli` (`serve` por stdio) e 92 testes. Comando: `python -m pytest -q`; medição: `python3 evals/run_pkg.py -v`.
- Experimento 2 feito (`evals/experimento-02.md`, `cases.grande.json` com 124 fatos, `cases.grande-idg.json` para a análise de sensibilidade): baseline hit@3 55% (ou 72% com desempate neutro), ruído em 3 de 6.
- `idea.md`, `assumptions.md`, `kill-criteria.md`, `decisions.md`, `risks.md` ajustados para a auto-hospedagem.

## Pendências herdadas da fase 1
- Confirmar os limites atuais dos planos gratuitos (GitHub Actions, Pages, PyPI) antes de depender deles.
- Entrevistas com colegas: puladas por decisão do Breno (registrado em `decisions.md`). H2 e H3 seguem não validadas.

## Próximo passo sugerido
3. ~~Exportar e importar~~ feito em 2026-09-24 (`mini-tars export <arquivo>`, `mini-tars import <arquivo>`).
Revisão independente do export/import feita e tratada. Falta: README/CI/instalação limpa (RNF-06/07).

Fatias que faltam (RF e RNF de `01-definir/requisitos.md`), em ordem, cada uma com teste e revisão do agente `revisor`:
1. ~~MCP por stdio~~ feito em 2026-09-24; revisão independente feita e tratada; no Windows do Breno passou nos 63 testes iniciais; falta conectar ao Claude Code de verdade (Breno faz em casa: `claude mcp add mini-tars -- <caminho>\.venv\Scripts\mini-tars.exe serve`).
2. ~~HTTP~~ feito em 2026-09-24, revisão independente feita e tratada (porta fora do intervalo virava traceback; corrigido).
3. **Exportar e importar** JSON com versão do esquema (RF-08) e logs sem conteúdo dos fatos (RNF-03).
4. README de instalação, teste de instalação limpa no CI e verificação de dependências (RNF-06, RNF-07); só então pensar em publicar (a publicação é do Breno).
Depois: estudo opcional de embeddings no computador do Breno, com conjunto de teste novo.

## Dúvidas abertas
- Colocar o Windows na matriz do CI (o bug de arquivo aberto só apareceu lá).
- `Service.remember` tem um parâmetro `date` que esconde `datetime.date` (funciona, mas confunde); renomear só se o Breno concordar.
- Pendência antiga: confirmar limites atuais dos planos gratuitos (GitHub Actions, Pages, PyPI) antes de depender deles.
