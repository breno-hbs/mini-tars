---
status: concluido
atualizado: 2026-09-23
dono: Breno
---
# Experimento 2: corpus ampliado com fatos distratores

Escrito ANTES de gerar os fatos. Não alterar depois de ver os resultados; desvios entram numa seção "Desvios" no fim.

## Pergunta
Os números do teste H1 (baseline hit@3 72%, hit@1 41%; experimento 1 hit@3 83%, hit@1 55%, ruído 5 de 6) se sustentam quando o corpus passa de 30 para cerca de 150 fatos?

## Hipótese (registrada antes de medir)
Os números caem. Com 30 fatos o top 3 cobre 10% do corpus; com 150 cobre 2%. Espero queda de hit@3 e de hit@1 tanto no baseline quanto no experimento 1. Se não cair, o corpus pequeno não era o problema principal.

## Como os distratores são gerados
1. Um agente recebe SÓ os 30 fatos existentes (f01 a f30) e a descrição do projeto fictício (app de agendamento para clínica veterinária, março a setembro de 2026). Ele NÃO vê as 35 perguntas nem o gold.
2. Pede-se cerca de 120 fatos novos, curtos, datados, no mesmo estilo, cobrindo assuntos do mesmo projeto (decisões, prazos, pessoas fictícias, infraestrutura, clientes, bugs, reuniões).
3. Regras para o agente: não repetir, não corrigir e não atualizar nenhum fato existente; nenhum dado real; ids d001, d002, ...
4. Uma única geração. Sem regenerar para "melhorar" o resultado.
5. Vocabulário: distratores podem reutilizar palavras dos fatos existentes (isso é o objetivo: competir na busca). Não são filtrados por isso.

## Filtro (única forma de remover um distrator)
Remover um distrator somente se ele responder, total ou parcialmente, a uma das 35 perguntas (o gold ficaria incompleto). Como conferir: buscar por palavras-chave de cada pergunta, ler os candidatos, decidir. Cada remoção é registrada abaixo com o id, a pergunta afetada e o motivo. Nenhum distrator é removido por "atrapalhar" nem por motivo de nota.

## Medições
- Rodar `run_baseline.py` no corpus grande (`evals/cases.grande.json`, 30 fatos originais + distratores aprovados, mesmas 35 perguntas e mesmo gold).
- Rodar com `queries-exp01.json` (mesmas consultas reescritas, sem reescrever de novo).
- Comparar com os resultados de 30 fatos: hit@1, hit@3, por tipo, ruído nas 6 sem resposta.
- Sem ajuste de limiar, stopwords ou algoritmo neste experimento. O script não muda.

## Como ler
- hit@3 baseline abaixo de 70%: K1 disparado no corpus maior; registrar e decidir entre alternativas.
- Queda pequena (até 5 pontos): números razoavelmente estáveis.
- Queda grande: o resultado com 30 fatos era otimista; o próximo passo (dividir ajuste e teste) passa a ser mais importante.
- Com 29 perguntas, um acerto vale 3,4 pontos; diferenças menores que 2 acertos não são conclusão.
- Ruído nas 6 sem resposta: reportar o número, sem meta de aprovação (o limiar ainda não existe).

## Limites
Distratores gerados por IA tendem a ser mais uniformes e mais "limpos" do que a memória real. O resultado continua sendo uma estimativa otimista do uso real.

## Filtro aplicado
Gerados 120 distratores (d001 a d120), uma única geração. Removidos 26 que respondiam, total ou em parte, a alguma das 35 perguntas; ficaram 94 (corpus final: 30 + 94 = 124 fatos, em `evals/cases.grande.json`). Removidos, com a pergunta afetada e o motivo:

- d007 (pergunta q34): suporte por e-mail: responde se usamos e-mail para mensagens
- d020 (pergunta q01): diz onde ficam as fotos (bucket, não o banco): responde em parte onde os dados ficam
- d024 (pergunta q10): regra de senha do login: responde em parte como as pessoas entram
- d025 (pergunta q34): e-mail transacional por SMTP: responde que usamos e-mail
- d030 (pergunta q19): teste de carga: API aguentou sem erros; responde em parte a saúde da API
- d036 (pergunta q28): diz quem cobre o plantão de infraestrutura
- d039 (pergunta q12): 'primeiro dia após a publicação' em 07/05: dá a data aproximada da v1
- d041 (pergunta q34): reenvio de convite por e-mail: responde que usamos e-mail
- d048 (pergunta q34): custo de e-mail no mês: responde que usamos e-mail
- d070 (pergunta q30): custo de anúncios pagos em junho: responde quanto foi gasto em marketing
- d071 (pergunta q27): número de clínicas usando o sistema no fim do semestre: responde em parte quantas clínicas
- d072 (pergunta q34/q09): lembrete por e-mail caía no spam: responde que usamos e-mail e como são os lembretes
- d073 (pergunta q05): diz quem escreveu testes automatizados: responde em parte quem cuida dos testes
- d074 (pergunta q04): contrato anual com desconto: responde em parte sobre cobrança
- d077 (pergunta q34): servidor de e-mail de teste: responde que usamos e-mail
- d084 (pergunta q10/q34): confirmação de e-mail antes do primeiro acesso: responde login e uso de e-mail
- d085 (pergunta q10/q34): link de confirmação por e-mail: responde login e uso de e-mail
- d088 (pergunta q09): fila de trabalhos reduziu falhas de lembrete: responde em parte como os lembretes são feitos
- d090 (pergunta q04): teste gratuito de 30 dias: responde em parte se será cobrado
- d095 (pergunta q03): cita 'depois da versão 1.1': responde em parte qual é a versão
- d096 (pergunta q09): validação de números de WhatsApp: responde em parte como os lembretes são enviados
- d098 (pergunta q09): contrato do provedor de WhatsApp e volume de mensagens: responde como os lembretes são enviados
- d102 (pergunta q13): bug de fuso de horário na visão mensal: responde em parte se o horário está certo
- d110 (pergunta q19): relatório abre em menos de 2 segundos: número de desempenho, responde em parte a saúde da API
- d115 (pergunta q02): diz que o backend usa Python: responde qual linguagem
- d120 (pergunta q29): plano de gravar vídeos de treinamento: responde em parte o que priorizar

Conferidos e mantidos por julgamento (não respondem, só aproximam o assunto): d016 e d035 (citam Pydantic/FastAPI, sem dizer a linguagem), d014/d063/d082/d097 (ferramentas de monitoramento e teste de invasão, sem dizer a saúde da API), d037 (congelamento de código às 18h, não é horário de deploy), d068/d043/d109 (limiares de clínicas, não a meta), d104/d113 (backlog e feedback, não prioridade), d055 (clínica que usa planilhas, sem chamar de concorrente). O filtro foi feito por uma única pessoa (o assistente), sem segunda revisão; é a parte mais frágil do experimento.

## Resultados
Consultas reescritas = as mesmas de `queries-exp01.json` (não foram reescritas de novo). Hit@3 e hit@1 sobre 29 perguntas com resposta; ruído sobre 6 sem resposta.

| Corpus / consulta | hit@3 | hit@1 | vocabulário hit@3 | ruído (de 6) |
| --- | --- | --- | --- | --- |
| 30 fatos, palavra-chave pura (referência) | 72% (21) | 41% (12) | 50% | 0 |
| 30 fatos, consulta reescrita (exp. 1) | 83% (24) | 55% (16) | 71% | 5 |
| **124 fatos, palavra-chave pura (leitura pré-registrada)** | **55% (16)** | **34% (10)** | 36% | 3 |
| **124 fatos, consulta reescrita** | **69% (20)** | **41% (12)** | 50% | 6 |
| 124 fatos, ids neutros, palavra-chave pura (sensibilidade) | 72% (21) | 45% (13) | 50% | 3 |
| 124 fatos, ids neutros, consulta reescrita (sensibilidade) | 72% (21) | 45% (13) | 57% | 6 |

O que isso mostra:
- Pela regra pré-registrada, o baseline caiu de 72% para 55% no hit@3 e K1 (mínimo de 70%) **dispararia** no corpus maior. A consulta reescrita ficou em 69%, também abaixo de 70%.
- **Mas há um artefato meu.** O desempate de pontuações iguais é pelo id em ordem alfabética, e os distratores têm ids "d###", que vêm antes de "f##". Em empates, o distrator sempre ganha do fato original, o que penaliza o corpus original. A variante com ids neutros (distratores renomeados para "g###" só nesta comparação) tem os desempates a favor dos originais e dá 72% e 72%. A verdade fica entre os dois; o intervalo 55% a 72% é a estimativa honesta. Isso mostra também que a pontuação atual empata muito (é grosseira) e que a regra de desempate precisa ser decidida de propósito (por exemplo, por recência ou por mais palavras em comum), não por acaso.
- A vantagem da consulta reescrita ficou incerta: +14 pontos na leitura pré-registrada, 0 com ids neutros. O ganho de 83% contra 72% no corpus de 30 fatos não se confirmou como robusto.
- O ruído nas perguntas sem resposta continua alto: 3 de 6 no baseline (0 com 30 fatos) e 6 de 6 com consulta reescrita. Corpus maior traz mais fatos com uma palavra em comum, então o problema piora com o tamanho. Isso reforça a necessidade de limiar de pontuação (R12).
- Perguntas de vocabulário diferente continuam sendo o ponto mais fraco (36% a 57%).
- Com 29 perguntas, 1 acerto = 3,4 pontos: a diferença entre 55% e 72% é de 5 acertos, real, mas todos os números aqui têm margem grande.

## Desvios
- A variante de ids neutros não estava no protocolo. Foi criada antes de ver os resultados (o arquivo foi gerado no mesmo comando que rodou as medições), mas depois de escrever este protocolo, por isso conta como desvio. A leitura pré-registrada continua sendo a com ids "d###"; a outra é reportada como análise de sensibilidade.
- O filtro de distratores foi feito por uma pessoa só (o assistente), sem revisão do Breno.
