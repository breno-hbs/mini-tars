---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Ideia

## Problema (sem citar a solução)
Quem trabalha com assistentes de IA em vários projetos perde contexto entre sessões. Decisões, preferências e o estado de cada projeto precisam ser repetidos. Quando ficam em arquivos soltos, eles se desatualizam e se contradizem, e o assistente age com informação velha.

## Para quem
Desenvolvedores que usam assistentes de IA (Claude Code e similares) em vários projetos. Primeiro usuário: o próprio Breno.

## Modelo de distribuição
Auto-hospedado: cada pessoa roda o servidor na própria máquina (ou no próprio servidor), com os próprios dados. O Breno não opera nem armazena dados de ninguém.

## Por que agora
O MCP virou um padrão para conectar ferramentas a assistentes de IA, e projetos como o Tars mostram que uma memória pessoal desse tipo é viável.

## Objetivo do projeto
Principal (decisão de 2026-09-23): **aprender e montar portfólio** com Python e FastAPI, MCP, testes e avaliações, e arquitetura com decisões registradas. Não é um produto que compete com o Basic Memory (ver `competitors.md`).
Secundário: se outros desenvolvedores usarem, ótimo; isso é medido só por K3, sem promessa de suporte.

## Hipótese mais arriscada
A recuperação traz o fato certo, e não ruído, com uma busca simples. Se isso falhar, o resto do sistema não importa.

## Validação barata (fase 2)
Antes de construir o servidor:
1. Escrever cerca de 30 fatos sobre um projeto do Breno e 30 perguntas com a resposta esperada.
2. Medir quantas vezes uma busca simples por palavra-chave devolve o fato certo.
3. Entrevistas com usuários: puladas por decisão do Breno (ver `docs/decisions.md`). A demanda de outros desenvolvedores só será testada pelo uso real, após o lançamento (K3).

## Fora de escopo por ora
Busca semântica com embeddings, versão hospedada, aplicativo móvel, painel web, cobrança.
