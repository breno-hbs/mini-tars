---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Requisitos do MVP

Prioridade: **M** (precisa estar no MVP), **S** (deveria; entra se o tempo permitir), **C** (poderia; depois). Cada requisito tem critério de aceite que um teste ou uma avaliação consegue verificar, e uma origem (hipótese, risco ou decisão), para rastrear.

## Funcionais
| ID | Requisito | Prior. | Critério de aceite | Origem |
| --- | --- | --- | --- | --- |
| RF-01 | **Guardar fato** (`remember`): texto (até 2.000 caracteres), data do fato (padrão: hoje em America/Sao_Paulo) e projeto opcional | M | Devolve o id; o fato existe após reiniciar o servidor; texto vazio ou acima do limite é recusado com mensagem clara | idea.md |
| RF-02 | **Buscar** (`search`): consulta em linguagem natural devolve até 3 fatos (configurável até 10) ordenados por relevância, com id, texto, data, pontuação e sinal de resultado fraco | M | Usa a busca base dos experimentos (palavra-chave, desempate por regra); no conjunto de ajuste `evals/cases.grande.json`, hit@3 ≥ 66% (19 de 29) | H1, R1, experimento 3 |
| RF-03 | **Substituir fato** (`remember` com `supersedes`): marca o fato antigo como substituído; a busca padrão ignora os substituídos, e `include_superseded` traz também o histórico | M | Nos casos f16→f17 (preço) e f05→f18 (donos dos testes), a busca padrão devolve só o atual e com `include_superseded` devolve também o antigo. Atenção: a pergunta temporal q06 ("em março, quem olhava os testes?") tem como resposta o fato antigo f05, então só funciona no modo histórico; as avaliações precisam registrar o modo de cada pergunta, e o hit@3 dos dois modos é medido e registrado. Limite: substituir um fato esconde tudo o que ele dizia (f05 também dizia quem cuidava da infraestrutura); por isso a regra de escrita é **uma afirmação por fato** | M | tipos "corrigido" (50%) e "temporal" |
| RF-04 | **Apagar fato** (`forget`): remoção definitiva por id | M | Após apagar, o fato não aparece em busca, exportação nem no arquivo do banco; apagar id inexistente devolve erro claro. **Limite documentado:** os arquivos de backup criados antes de uma migração (`.bak-vN`) mantêm o conteúdo antigo; o usuário deve apagá-los se quiser eliminar o fato de vez (README) | depth.md (dados) |
| RF-05 | **Sinal de resultado fraco** (`weak_match`) no resultado da busca, sem filtrar | S | Definido a partir da pontuação relativa da consulta; medido nas avaliações e registrado. Meta (revista em 2026-09-23 depois de medir; ver decisions.md): as perguntas sem resposta do ajuste voltam vazias ou sinalizadas em pelo menos 5 de 6, e no máximo 1 em cada 5 primeiros resultados corretos é sinalizado por engano | R12; experimento 3 (filtro perdia acertos, sinal não) |
| RF-06 | **Projeto** como espaço de nomes: `project` opcional em `remember`, `search` e `list_recent` | S | Busca com `project` só devolve fatos daquele projeto; a pontuação (idf) é calculada só dentro do projeto | idea.md |
| RF-07 | **Listar recentes** (`list_recent`): últimos N fatos ativos | S | Ordem por data do fato, depois por criação | uso diário |
| RF-08 | **Exportar e importar** por linha de comando, em JSON com versão do esquema | M | Exportar e importar em banco vazio reproduz o mesmo conteúdo (incluindo substituições); importar arquivo de versão desconhecida falha com aviso | R6, depth.md (backup) |
| RF-09 | **Iniciar o servidor**: `mini-tars serve` (stdio por padrão) e `mini-tars serve --http` (HTTP local) | M | Um cliente MCP real lista as ferramentas e chama `remember` e `search` nos dois modos | idea.md |
| RF-10 | **Configuração**: caminho do banco padrão no diretório de dados do usuário, alterável por variável de ambiente ou opção | M | Nenhum caminho fixo do computador do Breno no código; nenhum segredo em arquivo do repositório | CLAUDE.md |

## Não funcionais
| ID | Requisito | Prior. | Critério de aceite | Origem |
| --- | --- | --- | --- | --- |
| RNF-01 | **Escuta local por padrão**: o modo HTTP escuta em 127.0.0.1; outra interface só com token configurado | M | Teste: iniciar com `0.0.0.0` sem token falha; com token, exige cabeçalho de autorização; sem token no modo local, funciona | R2, K6 |
| RNF-02 | **Conteúdo recuperado é dado**: a saída das ferramentas marca o texto dos fatos como dados não confiáveis, e a documentação explica o risco | M | Teste com fato que contém "ignore as instruções anteriores": é devolvido literalmente, dentro do campo de dados, sem ser tratado como comando. Limite: não garante que o assistente obedeça | R3 |
| RNF-03 | **Privacidade**: sem telemetria; logs sem o texto dos fatos | M | Teste procura texto de fato de teste nos logs; nenhuma chamada de rede de saída no servidor | depth.md, CLAUDE.md |
| RNF-04 | **Migrações versionadas** com backup automático antes de migrar | M | Teste migra um banco antigo e confere o conteúdo; falha na migração deixa o banco original intacto (a transação é desfeita) e o arquivo de backup permanece | R6 |
| RNF-05 | **Avaliações como regressão** no CI | M | O CI roda `evals/` e falha se o hit@3 no ajuste ficar abaixo de 19 de 29. Mudar a busca exige novo conjunto de teste (o atual está esgotado) | H1, R1 |
| RNF-06 | **Instalação em um comando** (por exemplo `pipx` ou `uv tool`), testada em ambiente limpo no CI | S | Job do CI instala do pacote construído e roda `mini-tars --version` e uma busca | R4, H3 |
| RNF-07 | **Dependências verificadas** automaticamente | S | Job do CI com verificação de vulnerabilidades conhecidas; falha em relevante | R5, K6 |
| RNF-08 | **Fuso e datas**: datas do fato em America/Sao_Paulo; carimbos internos em UTC | M | Teste em torno da meia-noite: fato criado às 23h30 locais recebe a data local | CLAUDE.md |
| RNF-09 | **Desempenho**: busca responde rápido com milhares de fatos | C | Medir com 5.000 fatos em um computador comum e registrar o p95; a meta será definida depois de medir (sem número sem evidência) | uso diário |
| RNF-10 | **Sem dado real** em testes, fixtures e exemplos | M | Revisão do reviewer; fixtures são os fatos fictícios de `evals/` | CLAUDE.md |

## Fora do escopo (decisão registrada)
Embeddings (só depois, com experimento novo e conjunto de teste novo), painel web, versão hospedada, sincronização, multiusuário, importação automática de notas, autenticação por usuário.

## Rastreabilidade
| Hipótese ou risco | Requisitos que tratam |
| --- | --- |
| H1 recuperação (R1) | RF-02, RF-03, RNF-05 |
| R12 ruído com confiança | RF-05, RNF-02 |
| R2 servidor exposto | RNF-01 |
| R3 injeção de prompt | RNF-02 |
| R4 instalação difícil (H3) | RNF-06 |
| R5 vulnerabilidades (K6) | RNF-07 |
| R6 migração perde dados | RF-08, RNF-04 |
| K5 custo zero | Restrição da visão; RNF-06 e RNF-07 usam só planos gratuitos |

## Critérios de pronto do MVP
Todos os requisitos M atendidos e verificados por teste ou avaliação; README com instalação em um comando e aviso "sem garantia" e "nenhum dado sai da sua máquina"; o Breno consegue explicar cada diff (`CLAUDE.md`).
