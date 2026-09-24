# ADR-0001: Armazenar os fatos em SQLite (um arquivo local)

- Status: aceito (Breno, 2026-09-23)
- Data: 2026-09-23
- Relacionado: RF-01, RF-04, RF-08, RNF-04; R6

## Contexto
O produto é auto-hospedado, com custo zero e sem serviço do Breno. Os dados precisam sobreviver a reinícios, ser exportáveis e ser migráveis sem perda.

## Decisão
Usar SQLite (módulo `sqlite3` da biblioteca padrão), em um único arquivo no diretório de dados do usuário, com esquema versionado por `PRAGMA user_version` e backup automático do arquivo antes de cada migração.

## Alternativas consideradas
| Alternativa | Por que não |
| --- | --- |
| Arquivos Markdown (estilo Basic Memory) | Bom para leitura humana, mas substituição, apagar e migração ficam mais frágeis; e seria copiar o concorrente |
| Postgres | Exige instalar e operar um servidor; contra a instalação em um comando (RNF-06) |
| JSON em um arquivo | Simples, mas sem transações: uma queda no meio da escrita pode corromper tudo |

## Consequências
- Zero dependência extra e instalação simples.
- Transações protegem contra corrupção em queda.
- Uma pessoa só por banco (sem multiusuário), coerente com o escopo.
- Busca não usa o SQLite (ver ADR-0002), então o índice em memória precisa ser reconstruído ao iniciar; com milhares de fatos isso é barato, mas será medido (RNF-09).
