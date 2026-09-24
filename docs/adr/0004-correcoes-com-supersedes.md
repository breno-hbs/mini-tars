# ADR-0004: Correções por substituição explícita (`supersedes`), sem apagar o antigo

- Status: aceito (Breno, 2026-09-23)
- Data: 2026-09-23
- Relacionado: RF-03; tipos "corrigido" e "temporal" das avaliações

## Contexto
Nas avaliações, perguntas sobre fatos corrigidos (preço R$ 79 → R$ 89, dono dos testes) acertavam só 50%: a busca devolve o fato antigo junto do novo. Perguntas temporais ("em março...") precisam, ao contrário, do fato antigo.

## Decisão
Ao guardar um fato novo, é possível informar `supersedes` com o id do fato que ele substitui. O antigo fica no banco com `superseded_by` preenchido. A busca padrão ignora fatos substituídos; `include_superseded` os traz de volta (histórico). Apagar (`forget`) continua sendo remoção definitiva, e é outra ação.

## Alternativas consideradas
| Alternativa | Por que não |
| --- | --- |
| Apagar o fato antigo ao corrigir | Perde o histórico e quebra perguntas temporais |
| Deixar o assistente decidir entre os dois | Não confiável; é o problema medido |
| Escolher o mais recente por data automaticamente | Fatos diferentes com o mesmo assunto seriam confundidos; a substituição precisa ser uma decisão explícita |

## Consequências
- Substituir esconde tudo o que o fato antigo dizia. Regra de escrita: uma afirmação por fato (exemplo: f05 dizia duas coisas, quem cuida dos testes e quem cuida da infraestrutura).
- As avaliações precisam registrar em qual modo cada pergunta é feita (padrão ou histórico) e medir os dois.
- Apagar (`forget`) um fato que substituía outro **reativa** o antigo (`ON DELETE SET NULL`); coberto por teste.
- Uma cadeia de substituições (A→B→C) é permitida; a busca padrão devolve só o último.
