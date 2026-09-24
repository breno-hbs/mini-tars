---
status: rascunho (números a confirmar pelo Breno)
atualizado: 2026-09-23
dono: Breno
---
# Critérios de parada

Definidos antes de investir. Formato: se [métrica] não atingir [valor] até [prazo], então [ação].
Contagem de prazo começa na data de aprovação deste arquivo. Mudar um critério depois de ver o resultado é sinal de apego, não de aprendizado, e deve ser registrado em `docs/decisions.md`.

| # | Se | Até | Então |
| --- | --- | --- | --- |
| K1 | A busca simples acertar menos de 70% das perguntas do teste da fase 2 | Fim da fase 2 | Testar uma alternativa (por exemplo, embeddings). Como é projeto de aprendizado, também é válido seguir e documentar o porquê da falha, desde que registrado em `decisions.md` |
| K2 | (Removido em 2026-09-23: entrevistas puladas por decisão do Breno. A demanda passa a ser testada só por K3) | n/a | n/a |
| K3 | Menos de 3 pessoas (além do Breno) usarem por pelo menos 3 sessões por semana | 6 semanas após o lançamento | Não é motivo para encerrar (projeto de aprendizado): manter só como portfólio, sem suporte ativo. Só reforça o corte de onboarding e documentação |
| K4 | O Breno gastar mais de 5 horas por semana em suporte e manutenção | Qualquer semana, 2 vezes seguidas | Reduzir escopo ou pausar novos usuários |
| K5 | Surgir qualquer custo recorrente para o Breno (meta: R$ 0 por mês) | Qualquer mês | Pausar o item que gera o custo ou migrar para alternativa gratuita |
| K6 | Vulnerabilidade de segurança relevante encontrada em versão já distribuída | Imediato | Corrigir, publicar aviso e orientar atualização; se não houver correção em 7 dias, retirar a versão |

Teto de custo confirmado pelo Breno: R$ 0. Stack gratuita: GitHub (repositório, Actions, Pages, registro de contêineres), PyPI e SQLite local.
