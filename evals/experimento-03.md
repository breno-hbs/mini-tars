---
status: concluido
atualizado: 2026-09-23
dono: Breno
---
# Experimento 3: ajustar a busca sem inflar a nota

Escrito ANTES de mexer na busca. Desvios entram na seção "Desvios" no fim.

## Pergunta
Quais mudanças simples na busca melhoram o acerto de forma que se sustente em perguntas que não foram usadas para ajustar?

## Dados
- **Ajuste (dev):** corpus `evals/cases.grande.json` (124 fatos) com as 35 perguntas já conhecidas (29 com resposta, 6 sem). Tudo pode ser olhado e usado para decidir.
- **Teste (reservado):** `evals/teste-reservado.json`, 23 perguntas (18 com resposta, 5 sem), mesmo corpus. Congelado em 2026-09-23; sha256 (16 primeiros caracteres): `419767f92c1a71f3`. Não pode ser lido para decidir nada, nem rodado, até o passo final.
- O script novo se recusa a rodar o arquivo de teste sem a opção `--final`.
- Nota: as perguntas de teste foram reescritas pelo Breno depois de ver o corpus e os resultados do experimento 2. O gold de t21 foi ajustado antes de medir (nota no arquivo). t22 é ambígua e conta como ruído se aparecer no top 3.

## Candidatos (um de cada vez, nesta ordem)
1. **Desempate por regra**, sem depender do id: pontuação igual desempata por (a) mais palavras da consulta presentes, depois (b) data mais recente, depois (c) id. Isso remove o artefato do experimento 2 e vira o **novo baseline** (medido no dev).
2. **Limiar de pontuação:** só devolver resultado cuja pontuação seja pelo menos uma fração F da pontuação máxima possível da consulta (soma dos idf das palavras dela). F escolhido no dev entre 0,2, 0,3, 0,4 e 0,5 (só esses valores).
3. **Sinônimos:** lista curta e geral de equivalências do português cotidiano (por exemplo banco/dados, app/aplicativo/sistema, imagem/foto), escrita e congelada antes de rodar, com no máximo 30 pares, sem olhar caso a caso os erros do dev pergunta por pergunta. Cada par precisa fazer sentido fora deste projeto.
4. **Embeddings locais:** só se der para instalar um modelo pequeno neste ambiente ou no computador do Breno. Se não der, registrar "não testado" e o motivo; não substituir por outra coisa.

Cada candidato é medido sozinho sobre o vencedor do passo anterior. Vence o candidato que sobe hit@3 do dev em pelo menos 2 perguntas sem aumentar o ruído nas 6 sem resposta; empate ou ganho menor: manter o mais simples (o anterior). Toda configuração testada entra na tabela de resultados, inclusive as que falharam.

## Passo final (uma vez só)
Rodar no teste reservado, com `--final`, exatamente duas configurações: o baseline original (script do experimento 2, desempate por id) e a configuração vencedora. Não ajustar nada depois de ver esse resultado; se algo estiver errado, registrar como desvio e não repetir o teste para "melhorar".

## Como ler
- Critério (K1): hit@3 da configuração vencedora no teste reservado ≥ 70%. Ruído nas 5 sem resposta: reportar; meta de no máximo 2 de 5.
- Com 18 perguntas com resposta, 1 acerto vale 5,6 pontos; diferença de 1 a 2 acertos não é conclusão.
- Esperado: o resultado do dev será mais alto que o do teste. A diferença mede o quanto o ajuste foi "decorado".
- Se o vencedor não passa no teste: registrar, decidir entre aceitar o limite ou testar outra abordagem em um novo experimento com perguntas de teste novas.

## Limites
Corpus fictício gerado por IA, perguntas escritas por poucas pessoas, 18 perguntas de teste. O resultado indica tendência, não garantia de uso real.

## Resultados
Passos 1 a 4 medidos só no conjunto de ajuste (corpus de 124 fatos, 35 perguntas, 29 com resposta e 6 sem). O conjunto reservado NÃO foi rodado. Script: \`evals/run_exp03.py\`; lista de sinônimos: \`evals/sinonimos.json\`.

| # | Configuração (dev) | hit@3 | hit@1 | ruído (de 6) | Decisão |
| --- | --- | --- | --- | --- | --- |
| 0 | Script do exp. 2, desempate por id | 55% (16) | 34% (10) | 3 | referência |
| 1 | **Desempate por regra** (mais palavras, depois data mais recente) | **66% (19)** | **45% (13)** | 3 | **aceito (+3 acertos)**; novo baseline |
| 2a | 1 + limiar 0,2 | 66% (19) | 45% (13) | 3 | sem efeito |
| 2b | 1 + limiar 0,3 | 55% (16) | 45% (13) | 0 | não aceito pela regra (perde 3 acertos); zera o ruído |
| 2c | 1 + limiar 0,4 | 28% (8) | 24% (7) | 0 | não aceito |
| 2d | 1 + limiar 0,5 | 14% (4) | 14% (4) | 0 | não aceito |
| 3a | 1 + sinônimos | 69% (20) | 55% (16) | 3 | não aceito pela regra (+1 acerto no top 3; +3 no top 1) |
| 3b | 1 + sinônimos + limiar 0,3 | 59% (17) | 48% (14) | 0 | não aceito |
| 4 | Embeddings locais | não testado | | | o ambiente não alcança o site dos modelos (erro 403); precisa rodar no computador do Breno |

Leitura:
- O ganho mais claro veio de trocar o desempate por id por uma regra de propósito: +3 acertos. Isso confirma que o resultado do experimento 2 era em boa parte artefato de empate.
- O limiar é uma troca direta: com 0,3 o ruído vai de 3 para 0 de 6, mas se perdem 3 acertos de 29. Nenhum valor tem os dois ganhos. Como a regra do protocolo só conta ganho de acertos, o limiar não vence, mas a decisão de aceitar a troca é do Breno (precisão contra cobertura) e deve ser tomada ANTES do passo final.
- Sinônimos: +1 acerto no top 3 (abaixo do mínimo de 2), mas +3 no top 1. O efeito é pequeno e a lista foi escrita depois de o assistente ter visto as perguntas de teste (ver Desvios), então qualquer ganho no teste seria otimista.
- Configuração vencedora pela regra: passo 1 (desempate por regra), 66% de hit@3 no dev.


### Passo final: conjunto reservado, rodado uma vez (2026-09-23)
23 perguntas (18 com resposta, 5 sem), corpus de 124 fatos.

| Configuração | hit@3 | hit@1 | ruído (de 5) |
| --- | --- | --- | --- |
| Script original (desempate por id) | 67% (12/18) | 50% (9) | 4 |
| **Vencedora: desempate por regra** | **72% (13/18)** | 44% (8) | 4 |
| Vencedora + limiar 0,3 | 44% (8/18) | 39% (7) | 2 |

- **K1 (hit@3 ≥ 70%): passou, por uma pergunta.** 13 de 18 é 72%; 12 de 18 seria 67%. A margem é de um acerto (5,6 pontos), então não é conclusão firme.
- No dev a vencedora deu 66% e no teste 72%: o teste não ficou abaixo do ajuste, ao contrário do esperado. Com 18 perguntas isso é variação normal e não prova que o ajuste generalizou; o ganho do desempate por regra sobre o original foi +1 acerto no teste (+3 no dev).
- Ruído: 4 de 5 perguntas sem resposta trazem um fato irrelevante (meta era no máximo 2), incluindo t22, que era ambígua. Não passou.
- Limiar 0,3: reduz o ruído a 2 de 5, mas perde 5 acertos de 18 (72% para 44%). Troca ruim nesta forma: o limiar relativo é grosseiro demais.
- Ainda erram: t04, t05, t11, t14, t21. Todos de vocabulário diferente ("revisando" contra "revisão de código", "arrumar" contra "corrigir", "segurança" contra "invasão", "autenticação" contra "login"); é o que a lista de sinônimos tentaria cobrir, e ela não foi usada no final.
- O teste reservado está usado. Qualquer nova rodada de ajuste precisa de perguntas de teste novas.

## Desvios
- **O assistente viu as perguntas do conjunto reservado** (escreveu os rascunhos e leu as reescritas do Breno) antes de escrever a lista de sinônimos. Vários grupos (imagem/foto, aplicativo/produto, valor/custo, responsável/cuida, erro/bug/arrumar, cadastro/registro) coincidem com o vocabulário do teste. Não dá para separar o quanto isso influenciou. Se os sinônimos forem usados no passo final, o resultado do teste é otimista para eles; um teste limpo exigiria perguntas novas (experimento 4).
- **Correção no limiar:** a primeira versão do script calculava a pontuação máxima possível só com as palavras que existem no corpus; o protocolo diz "todas as palavras da consulta". Corrigi para seguir o protocolo. Com a versão errada, os limiares de 0,2 a 0,4 não mudavam nada (66%, ruído 3) e 0,5 dava 59%; a tabela usa a versão corrigida.
- **Passo final com 3 configurações, não 2** (decidido antes de rodar, a pedido do Breno de que o assistente escolhesse): script original (desempate por id), vencedora (desempate por regra) e vencedora + limiar 0,3. As três são reportadas; nenhuma é escolhida depois de ver o teste. A leitura do critério K1 usa a vencedora sem limiar; o limiar é reportado como troca (ruído contra acertos).
- **Lacuna no critério de aceitação:** ele só conta hit@3, então um limiar que reduz o ruído nunca pode vencer. Não mudei a regra; deixei a decisão para o Breno antes do passo final.
