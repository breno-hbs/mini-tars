---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Avaliação de recuperação (fase 2, H1)

Objetivo: medir se uma busca simples por palavra-chave devolve o fato certo. Critério de parada K1: acerto menor que 70% no hit@3 obriga a testar uma alternativa (ou registrar o porquê de seguir).

## Formato
Um único arquivo `cases.json`:

```json
{
  "facts": [
    {"id": "f01", "date": "2026-03-02", "text": "Decidimos usar Postgres em vez de MySQL por causa do suporte a JSON."}
  ],
  "questions": [
    {"id": "q01", "q": "Qual banco de dados foi escolhido e por quê?", "gold": ["f01"]}
  ]
}
```

- `facts`: fatos curtos e datados sobre um projeto (o que a memória guardaria).
- `questions`: perguntas como você as faria a um assistente. `gold` lista os fatos que respondem.
- Meta da fase 2: cerca de 30 fatos e 30 perguntas. Cada pergunta pode ter `tipo` (direto, vocabulario, temporal, corrigido, sem-resposta) e `status` (`rascunho` ou `final`).

## Regras para o conjunto ser honesto
1. **Dados fictícios ou anonimizados.** Nada de dados reais de terceiros, credenciais ou segredos (regra do `CLAUDE.md`).
2. **Perguntas naturais, não copiadas.** Se a pergunta repete as palavras do fato, a busca por palavra-chave acerta fácil e o teste não diz nada. Reescreva com sinônimos e mudando a ordem.
3. **Inclua casos difíceis:** perguntas sobre datas ("o que decidimos em março?"), sobre um fato que foi corrigido depois (dois fatos, um obsoleto), e perguntas cujo termo-chave não aparece no fato.
4. **Pelo menos 5 perguntas sem resposta nos fatos** (`"gold": []`), para medir se o sistema devolve ruído com confiança. O script as reporta à parte.
5. **Escreva o conjunto antes de ver o resultado** e não o ajuste para aumentar a nota. Mudanças ficam registradas em `docs/decisions.md`.

## Arquivos
- `cases.json`: conjunto atual (30 fatos, 35 perguntas reescritas pelo Breno; gold ajustado em q03, q04, q09, com `gold_original` e `nota_gold`).
- `cases.original-gold.json`: exatamente como o Breno enviou.
- `cases.rascunho-assistente.json`: rascunho antigo das perguntas (não usar para medir).
- `cases.example.json`: 3 fatos, só para provar que o script roda.
- `experimento-01.md`, `queries-exp01.json`, `queries-exp01-sem-suspeitos.json`: experimento em que o assistente reescreve a consulta. Rodar com `python3 evals/run_baseline.py evals/cases.json evals/queries-exp01.json`.

- `experimento-02.md`, `cases.grande.json`, `cases.grande-idg.json`: corpus ampliado (124 fatos) com distratores; o `-idg` só troca os ids dos distratores para testar o efeito do desempate. Rodar com `python3 evals/run_baseline.py evals/cases.grande.json [evals/queries-exp01.json]`.

- `experimento-03.md`, `run_exp03.py`, `sinonimos.json`, `teste-reservado.json` (+ `teste-reservado.original-breno.json`): ajuste em dev e teste reservado (já usado). O script recusa o arquivo reservado sem `--final`.

## Como rodar
```
python3 evals/run_baseline.py evals/cases.json
```
Usa só a biblioteca padrão do Python. Imprime hit@1 e hit@3 (respondíveis) e a lista de perguntas que erraram, para você ler os erros.

## Limites
- **Corpus pequeno infla o hit@3.** Com 30 fatos, o top 3 já cobre 10% de tudo. Um sistema ruim ainda acerta bastante. Olhe o hit@1, os erros por tipo e repita com corpus maior (feito com 124 fatos no experimento 2: o hit@3 do baseline foi de 72% para entre 55% e 72%). O desempate entre pontuações iguais é por id, e isso mexe no resultado: ver `experimento-02.md`.
- **Perguntas escritas por quem escreveu os fatos tendem a repetir as mesmas palavras.** Por isso a regra 2.
O exemplo incluso (`cases.example.json`) tem só 3 fatos, para provar que o script roda. **Não é uma medição.** Repare que q01 e q02 repetem palavras do fato (fáceis) e q03 não repete nenhuma ("dono da qualidade do código" contra "cuidar dos testes automatizados"): a busca por palavra-chave erra q03, e esse tipo de erro é exatamente o que a H1 quer medir. O número que vale é o do seu conjunto de ~30.
