# ADR-0002: Busca por palavra-chave própria, em memória, igual à das avaliações

- Status: aceito (Breno, 2026-09-23)
- Data: 2026-09-23
- Relacionado: RF-02, RF-05, RNF-05; H1, R1, R12; `evals/experimento-01.md` a `03.md`

## Contexto
A hipótese H1 foi testada com um algoritmo específico (pontuação por idf das palavras da consulta presentes no fato, normalização sem acento e com corte mínimo de plural, desempate por regra). Resultado: hit@3 de 72% no teste reservado (13/18), K1 passou por um acerto. Os experimentos também mostraram que o resultado depende de detalhes como o desempate.

## Decisão
Implementar em `search.py` exatamente o algoritmo medido em `evals/run_exp03.py` (opção `--tiebreak rule`, sem limiar, sem sinônimos), mantendo um índice em memória reconstruído a partir do SQLite ao iniciar e atualizado a cada escrita. O sinal `weak_match` é calculado a partir da pontuação relativa e **não filtra** resultados (o limiar que filtrava perdia acertos no experimento 3).

## Alternativas consideradas
| Alternativa | Por que não agora |
| --- | --- |
| SQLite FTS5 (BM25 pronto) | Provavelmente bom, mas o resultado seria diferente do medido; exigiria novo experimento com teste novo. Fica como candidato futuro |
| Embeddings locais | Não testados (sem acesso ao site dos modelos no ambiente de teste); aumentam a instalação. Candidato futuro, no computador do Breno |
| Sinônimos | +1 acerto no ajuste e a lista foi escrita depois de ver o teste: evidência fraca |
| Filtrar por limiar | Zerou o ruído no ajuste, mas com 0,3 o acerto no teste caiu de 72% para 44% |

## Consequências
- O comportamento do produto é reproduzível pelas avaliações do repositório (força para o portfólio).
- Vocabulário diferente continua sendo o ponto fraco conhecido (todos os erros restantes do teste).
- Qualquer mudança na busca precisa de conjunto de teste novo, porque o atual está esgotado.
- Duplicação evitada: o script de avaliações e o `search.py` devem compartilhar o código (a definir na implementação, sem copiar e colar).
