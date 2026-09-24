---
status: pré-registrado (escrito antes de rodar)
data: 2026-09-23
dono: Breno
---
# Experimento 1: o assistente reescreve a consulta antes de buscar

## Hipótese
Se um modelo de linguagem transformar a pergunta em uma consulta com sinônimos e termos prováveis, a busca por palavra-chave passa a acertar as perguntas de vocabulário diferente, sem o servidor precisar de embeddings.

## Ponto de partida (baseline, 2026-09-23, `evals/cases.json`)
- hit@3: 72% (21/29) | hit@1: 41% (12/29)
- hit@3 em perguntas de vocabulário diferente: 50% (7/14)
- Ruído nas 6 perguntas sem resposta: 0 de 6

## Protocolo
1. Um agente **cego** recebe só o texto das 35 perguntas e uma frase de contexto ("time que desenvolve um app de agendamento para clínicas veterinárias"). Ele **não vê os fatos nem o `gold`**.
2. Para cada pergunta ele devolve uma consulta de 6 a 10 termos (palavras-chave, sinônimos e termos técnicos prováveis) em português.
3. **Uma única tentativa.** Se o prompt for alterado depois de ver o resultado, isso vira o experimento 2, e o 1 continua registrado como foi.
4. As mesmas 35 perguntas, os mesmos fatos, o mesmo motor de busca e as mesmas palavras vazias do baseline. Só muda o texto da consulta.
5. **Checagem de vazamento:** procurar nas consultas termos que só existem nos fatos e que o agente não teria como adivinhar (nomes próprios das pessoas, "Pagar.me", "UTC"). Se aparecerem, o experimento é anulado.

## Critérios de sucesso (definidos antes de ver o resultado)
- **Sucesso:** hit@3 geral **≥ 80%** e hit@3 em vocabulário diferente **≥ 70%**.
- **Trava de ruído:** no máximo **2 de 6** perguntas sem resposta podem trazer algum fato. Se passar disso, o ganho custa respostas confiantes sobre coisas que não se sabe, e o resultado conta como **falha parcial** mesmo que os acertos subam.
- **Também reportar:** hit@1 e a lista de erros.

## Limites conhecidos
- Corpus de 30 fatos: o top 3 cobre 10% de tudo, então qualquer número está inflado.
- Consultas mais longas casam com mais fatos, o que ajuda os acertos e piora o ruído. A trava existe por isso.
- Não é possível provar tecnicamente que o agente cego não leu os arquivos do projeto. A instrução é explícita e a checagem de vazamento cobre os casos mais óbvios.
- O agente que reescreve é um modelo diferente do que usaria o servidor no dia a dia; o resultado indica a ideia, não o desempenho real.

---

# Resultado (2026-09-23)

Consultas geradas por um agente cego (relatório do sistema: **0 usos de ferramentas**, então ele não leu os arquivos do projeto). Uma única tentativa, arquivo `queries-exp01.json`.

| | Baseline | Experimento 1 (como veio) | Variante sem "UTC" e "postgres" |
| --- | --- | --- | --- |
| hit@1 | 41% (12/29) | 55% (16/29) | 55% (16/29) |
| hit@3 | 72% (21/29) | **83%** (24/29) | 79% (23/29) |
| hit@3, vocabulário diferente | 50% (7/14) | **71%** (10/14) | 64% (9/14) |
| Perguntas sem resposta com ruído | 0 de 6 | **5 de 6** | 5 de 6 |

## Veredito pelos critérios pré-registrados
- **Acerto (hit@3 geral ≥ 80% e vocabulário ≥ 70%):** passou **como veio** (83% e 71%), **mas não passa na variante** (79% e 64%).
- **Trava de ruído (máximo 2 de 6):** **falhou nas duas versões** (5 de 6).
- **Conclusão: falha parcial.** A reescrita ajuda (hit@1 sobe 14 pontos e vocabulário sobe 14 a 21), mas faz a busca devolver um fato para quase toda pergunta sem resposta.

## Checagem de vazamento: sinal disparado, tratado assim
- Dois termos apareceram nas consultas: "UTC" (q13) e "postgres" (q01). "UTC" estava na minha lista de sinais, o que pelo protocolo anularia o experimento.
- Contra a anulação: o agente não usou ferramentas, e os dois termos são palpites comuns do domínio (UTC para fuso horário, Postgres para banco de dados).
- Decisão: **não anular, mas reportar a variante sem os dois termos.** Isso foi um desvio do protocolo escrito, decidido depois de ver o resultado, e por isso está aqui explícito.
- O resultado é sensível a **um único palpite:** sem "postgres", q01 deixa de acertar, e é isso que leva o hit@3 de 83% para 79%. Com 29 perguntas, um acerto vale 3,4 pontos, então a diferença entre "passou" e "não passou" está dentro do ruído.

## O que o experimento mostra e não mostra
- Mostra: reescrever a consulta melhora o alcance da busca por palavra-chave sem embeddings.
- Mostra: o ganho tem um custo em precisão, porque consultas com muitos termos casam com quase qualquer fato.
- Não mostra: o efeito num corpus grande, com outro modelo, ou com o modelo do dia a dia. Também não mede se o assistente, ao ler os fatos devolvidos, ignoraria os irrelevantes (o que reduziria o dano do ruído, mas não foi testado).
