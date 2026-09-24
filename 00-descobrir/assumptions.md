---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Hipóteses e riscos de aprendizado

Ordenadas da mais arriscada para a menos. "Como testar" é o experimento mais barato que dá evidência.

| # | Hipótese | Se for falsa | Como testar | Status |
| --- | --- | --- | --- | --- |
| H1 | Uma busca simples por palavra-chave recupera o fato certo na maioria dos casos | O projeto precisa de embeddings ou de outro método, e o escopo cresce | 30 fatos e 30 perguntas, medir acerto (ver `idea.md`) | Sustentada só em parte (2026-09-23): palavra-chave pura hit@3 72%, hit@1 41%, vocabulário 50%. Com o assistente reescrevendo a consulta: hit@3 83%, hit@1 55%, mas 5 de 6 perguntas sem resposta trazem ruído. Experimento 2 (124 fatos): hit@3 entre 55% e 72% (baseline) e entre 69% e 72% (reescrita), ruído 3 a 6 de 6; ganho da reescrita não confirmado como robusto. Experimento 3 (teste reservado, 18 perguntas): hit@3 72% (13/18) com desempate por regra, K1 passou por um acerto; ruído 4 de 5. Ver `decisions.md` e `evals/experimento-0{1,2,3}.md` |
| H2 | Desenvolvedores têm esse problema com força suficiente para instalar algo novo | Fica só como projeto pessoal e de portfólio | Entrevistas puladas por decisão do Breno; só o uso real após o lançamento (K3) testa | Não validada (risco aceito) |
| H3 | Desenvolvedores aceitam auto-hospedar (Docker ou Python local) em vez de usar um serviço pronto | Precisa de instalação de um comando ou de uma versão hospedada, que muda custo, legal e suporte | Teste de instalação limpa no CI; depois do lançamento, observar issues de instalação | Não validada (risco aceito) |
| H4 | O Breno consegue manter o projeto e o suporte com o tempo que tem para estudo | Reduzir escopo ou o número de usuários | Registrar horas reais por semana nas 6 primeiras semanas | Não testada |
| H5 | Uma memória própria oferece algo que alternativas existentes não oferecem | Melhor usar uma existente e focar o aprendizado em outra coisa | Pesquisa de concorrentes na fase 1 (fontes verificadas, estado atual) | Refutada como produto novo: o Basic Memory já cobre o mesmo espaço (ver `competitors.md`) |

Regra: uma hipótese só muda de status com evidência registrada em `docs/decisions.md`.
