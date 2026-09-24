---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Visão do produto

## Em uma frase
Um servidor de memória, auto-hospedado e feito em Python, que deixa um assistente de IA guardar e recuperar fatos sobre os seus projetos entre sessões, com recuperação medida por avaliações que qualquer pessoa consegue reproduzir.

## Problema e público
Ver `00-descobrir/idea.md`. Desenvolvedores que usam assistentes de IA em vários projetos perdem decisões, preferências e estado do projeto entre sessões. Primeiro usuário: o Breno.

## Objetivo do projeto (ordem de importância)
1. **Aprender e montar portfólio**: Python e FastAPI, MCP, testes, avaliações e arquitetura com decisões registradas (decisão de 2026-09-23).
2. **Ser útil ao Breno** no dia a dia, como memória dos próprios projetos.
3. **Outros desenvolvedores usarem**, sem promessa de suporte (K3 mede isso).

## O que torna este projeto diferente
Não é a funcionalidade: o Basic Memory já cobre o espaço (`competitors.md`). O que é próprio, e o que o README deve mostrar:
- **Avaliações reproduzíveis**: o repositório traz o conjunto de fatos e perguntas, o script e os protocolos pré-registrados (`evals/`). Qualquer pessoa roda e confere os números.
- **Decisões registradas** (`docs/decisions.md` e ADRs em `docs/adr/`), incluindo o que deu errado.
- **Correções explícitas**: um fato pode substituir outro, e a busca devolve o atual (RF-03).

## Princípios
1. **Local primeiro.** Os dados ficam na máquina do usuário. Sem telemetria, sem conta, sem serviço do Breno.
2. **Dizer "não sei" é melhor que inventar.** A busca sinaliza resultado fraco em vez de apresentar ruído como certeza (R12).
3. **Conteúdo recuperado é dado, nunca instrução** (R3).
4. **Simples e medido antes de sofisticado.** Nenhuma técnica de busca entra sem passar pelas avaliações (lição dos experimentos 1 a 3).
5. **Seguro por padrão.** Escuta só em 127.0.0.1; qualquer outra interface exige token (R2).

## Escopo do MVP
Dentro: guardar, buscar, substituir e apagar fatos; exportar e importar; servidor MCP por stdio e por HTTP local; avaliações e testes no CI.
Fora (por ora): embeddings e busca semântica, painel web, versão hospedada, sincronização entre máquinas, várias pessoas no mesmo servidor, importação automática de notas.
Detalhes e critérios de aceite em `requisitos.md`.

## Como saberemos que funcionou
| Objetivo | Medida | Meta |
| --- | --- | --- |
| Aprender | ADRs escritos, testes e avaliações no CI, servidor rodando com um cliente MCP real | MVP funcionando de ponta a ponta |
| Recuperação (H1, K1) | hit@3 no conjunto de ajuste (`evals/cases.grande.json`) | não cair abaixo de 66% (19/29); K1 mantém o mínimo de 70% em conjunto de teste novo |
| Uso próprio | O Breno usa o mini-Tars em pelo menos um projeto real por 4 semanas | sim ou não, registrado no `handoff.md` |
| Uso por outros (K3) | Colegas ativos além do Breno, 3 sessões por semana | menos de 3 em 6 semanas: manter como portfólio |
| Custo (K5) | Custo recorrente | R$ 0 |

## Restrições
- Custo recorrente zero (K5): nada de domínio, hospedagem ou serviço pago.
- Tempo do Breno limitado (K4, R7): escopo pequeno.
- Sem dados reais de ninguém em testes, fixtures ou logs (`CLAUDE.md`).
- Fuso America/Sao_Paulo (`CLAUDE.md`).

## Perguntas em aberto para o Breno
Ver o fim de `arquitetura.md` (seção "Decisões que dependem do Breno"): nome do pacote, licença e versão mínima do Python.
