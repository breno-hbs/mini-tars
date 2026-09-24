---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Arquitetura do MVP

Decisões individuais, com alternativas e consequências, ficam em `docs/adr/`. Este arquivo mostra o conjunto. Os ADRs 0001 a 0005 foram aceitos pelo Breno em 2026-09-23.

## Visão geral
```
 Assistente de IA (Claude Code etc.)  <-- cliente MCP
        |                 |
   stdio (padrão)     HTTP em 127.0.0.1 (opcional, token fora do local)
        |                 |
        +------ mini-tars (processo Python) ------+
                 |
        Camada MCP (ferramentas)   remember | search | forget | list_recent
                 |
        Serviço (regras): validação, datas, substituição, sinal de resultado fraco
             |                          |
     Busca (índice em memória)     Armazenamento (SQLite)
     palavra-chave, desempate        um arquivo no diretório de dados do usuário
     por regra (evals/)              migrações versionadas, backup antes de migrar

 CLI: mini-tars serve | export | import | --version   (usa o mesmo Serviço)
```
Nenhuma chamada de rede de saída. Nenhum serviço do Breno.

## Componentes e responsabilidades
| Módulo (`src/mini_tars/`) | Responsabilidade | Depende de |
| --- | --- | --- |
| `models.py` | Tipos: Fato, Resultado, erros do domínio | nada |
| `config.py` | Caminho dos dados, porta, token, limites; lê variáveis de ambiente | nada |
| `store.py` | SQLite: criar, ler, substituir, apagar, migrar, backup antes de migrar | `models` |
| `search.py` | Normalização, índice, pontuação, desempate por regra, sinal de resultado fraco. **Mesmo algoritmo de `evals/run_exp03.py`** | `models` |
| `service.py` | Regras de negócio: valida entradas, aplica datas em America/Sao_Paulo, substituição, mantém o índice em sincronia com o banco | `store`, `search` |
| `mcp_server.py` | Declara as ferramentas MCP e converte para chamadas do serviço; rotula texto de fato como dado | `service` |
| `http_app.py` | Modo HTTP (FastAPI ou Starlette), token e escuta local | `mcp_server`, `config` |
| `cli.py` | Comandos `serve`, `export`, `import` | `service`, `http_app` |

Regra de dependência: de cima para baixo na tabela; `search.py` e `store.py` não se conhecem (é o `service.py` que os liga). Isso permite testar a busca sem banco e trocá-la (por exemplo, por embeddings) sem tocar no armazenamento.

## Modelo de dados
```sql
CREATE TABLE facts (
  id            INTEGER PRIMARY KEY,
  text          TEXT    NOT NULL CHECK (length(text) BETWEEN 1 AND 2000),
  fact_date     TEXT    NOT NULL,          -- AAAA-MM-DD, data local (America/Sao_Paulo)
  project       TEXT,                      -- opcional
  created_at    TEXT    NOT NULL,          -- UTC, ISO 8601
  superseded_by INTEGER REFERENCES facts(id)  -- preenchido quando outro fato substitui este
);
CREATE INDEX idx_facts_project ON facts(project);
-- versão do esquema: PRAGMA user_version
```
Regra de escrita: **uma afirmação por fato** (ver limite de RF-03 nos requisitos). Nada de campos livres extras no MVP.

## Contratos das ferramentas MCP
Todos os resultados incluem o texto do fato dentro de um campo `data`, com um aviso curto de que é conteúdo guardado pelo usuário e não instrução (RNF-02).

| Ferramenta | Entrada | Saída |
| --- | --- | --- |
| `remember` | `text` (obrigatório), `date` (opcional, AAAA-MM-DD), `project` (opcional), `supersedes` (opcional, id) | `{id}` ou erro |
| `search` | `query` (obrigatório), `limit` (1 a 10, padrão 3), `project` (opcional), `include_superseded` (padrão falso) | lista de `{id, data: {text, date, project}, score, weak_match, superseded_by?}` |
| `forget` | `id` | `{deleted: true}` ou erro |
| `list_recent` | `limit` (padrão 10), `project` (opcional) | lista de fatos ativos |

Erros têm mensagem em português clara e código estável (`empty_text`, `text_too_long`, `unknown_id`, `invalid_date`).

## Segurança (modelo de ameaças resumido)
| Ameaça | Risco | Controle |
| --- | --- | --- |
| Porta aberta para a rede sem autenticação | R2 | Escuta em 127.0.0.1; outra interface só com token; recusa iniciar sem token (RNF-01) |
| Texto guardado que tenta comandar o assistente | R3 | Saída marcada como dado, aviso na documentação; limite honesto: o servidor não controla o assistente (RNF-02) |
| Dependência vulnerável | R5 | Poucas dependências, verificação no CI, versões fixadas (RNF-07) |
| Perda de dados ao atualizar | R6 | Migração com backup antes; exportar e importar (RF-08, RNF-04) |
| Vazamento por log | R3/R2 | Logs sem o texto dos fatos (RNF-03) |
| Página de outro site chamando o servidor local pelo navegador | novo, a tratar no modo HTTP | Validar cabeçalho `Origin` e `Host`; recusar origens que não sejam locais |

O último item foi identificado agora e ainda não está em `risks.md`: entra como R13 (ver `docs/risks.md`).

## Estratégia de testes
| Nível | O que cobre | Ferramenta |
| --- | --- | --- |
| Unitário | `search.py` (normalização, desempate, sinal fraco), `service.py` (validação, datas, substituição) | pytest |
| Armazenamento | `store.py` com SQLite em arquivo temporário; migração de banco antigo | pytest |
| Contrato MCP | Cliente MCP de teste chama as ferramentas nos dois modos e confere formato e erros | pytest |
| Segurança | Bind sem token falha; cabeçalhos de origem; texto de injeção devolvido como dado; logs sem conteúdo | pytest |
| Avaliações | `evals/` como regressão: hit@3 no ajuste ≥ 19 de 29; modos padrão e histórico registrados | script de `evals/` chamado no CI |
| Instalação limpa | Instala o pacote construído e roda uma busca | job do CI |

Fixtures: só os dados fictícios de `evals/`.

## Distribuição e CI (nível Mínimo, planos gratuitos a confirmar)
Pacote Python publicado no PyPI; imagem Docker opcional. CI no GitHub Actions: testes, avaliações, instalação limpa e verificação de dependências. **A publicação é sempre feita pelo Breno** (`CLAUDE.md`). Limites dos planos gratuitos ainda precisam ser confirmados na fonte oficial antes de depender deles.

## Passo zero da construção: verificação técnica (feita em 2026-09-23)
Confirmado no SDK Python do MCP (linha 2.x, `MCPServer`, `mcp>=2,<3`): stdio, HTTP e montagem no FastAPI funcionam; a proteção de `Host` e `Origin` já vem no SDK. Detalhes e ressalvas no ADR-0003.

## Decisões do Breno (resolvidas em 2026-09-23)
1. **Nome do pacote e do comando**: `mini-tars` (conferir se o nome está livre no PyPI antes de publicar).
2. **Licença**: MIT.
3. **Versão mínima do Python**: 3.11.
4. **ADRs 0001 a 0005**: aprovados.
