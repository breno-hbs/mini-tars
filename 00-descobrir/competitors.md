---
status: rascunho
atualizado: 2026-09-23
dono: Breno
fontes: páginas dos repositórios no GitHub, abertas em 2026-09-23
---
# Concorrentes e alternativas (H5)

Dados lidos nas páginas dos repositórios em 2026-09-23. Números de estrelas e versões mudam; confirmar antes de citar. Onde a página não informou, está marcado "não informado" (não significa que não exista).

| Projeto | O que é | Licença | Estrelas | Armazenamento | MCP | Uso local |
| --- | --- | --- | --- | --- | --- | --- |
| [Basic Memory](https://github.com/basicmachines-co/basic-memory) | Memória em arquivos Markdown que humano e IA leem e escrevem; grafo de entidades, observações e relações | AGPL-3.0 | 3,6 mil | Markdown + SQLite (padrão) ou PostgreSQL | Sim (Claude Desktop, Claude Code, Cursor, VS Code, outros) | Sim; `uv tool install basic-memory` |
| [Graphiti (Zep)](https://github.com/getzep/graphiti) | Grafo de contexto temporal para agentes (fatos com janela de validade) | Apache-2.0 | 29 mil | Banco de grafos: Neo4j, FalkorDB, Neptune | Sim (servidor MCP incluído) | Sim, com Docker Compose; exige banco de grafos |
| [mem0](https://github.com/mem0ai/mem0) | Camada de memória para agentes de IA; busca híbrida (semântica, BM25, entidades) | Apache-2.0 | 65,9 mil | Vetorial (Qdrant citado); servidor com Docker Compose | Não informado na página | Sim, com Docker Compose; usa modelos da OpenAI por padrão |
| [Letta](https://github.com/letta-ai/letta) | Plataforma de agentes com estado e memória própria | Apache-2.0 | 24,7 mil | Não detalhado na página | Não informado claramente | Servidor local (`letta server`) e nuvem própria |
| [Tars](https://github.com/fonsecabc/tars) | Memória pessoal de usuário único, exposta ao Claude por MCP | MIT | 2 | PostgreSQL com pgvector | Sim (13 ferramentas) | Sim; Node.js, Docker |

Fonte adicional: README do Tars enviado pelo Breno (benchmark LOCOMO com modelos locais).

## O que isso diz sobre H5

**H5 ("uma memória própria oferece algo que as existentes não oferecem") não se sustenta como produto novo.** O concorrente mais próximo é o **Basic Memory**: Python, SQLite local, MCP, distribuição por PyPI, instalação em um comando, grafo de entidades e observações. É essencialmente o que o mini-Tars pretende ser, com 3,6 mil estrelas e mais de 1.700 commits.

Diferenças possíveis do mini-Tars, ainda não validadas:

- **Método de avaliação como parte do produto** (placar de recuperação reproduzível, como o benchmark do Tars). Nenhuma das páginas lidas destacou isso, mas não conferi a documentação interna de cada uma.
- **Escopo muito menor e mais simples de entender**, útil para aprender.
- **Licença permissiva** (MIT ou Apache) em vez de AGPL, relevante para quem não quer copyleft.

## Consequência para o projeto

Como as entrevistas foram puladas (H2, H3) e a H5 fica fraca, o projeto se sustenta hoje **como aprendizado e portfólio**, não como produto que compete no mercado. Isso muda a decisão sobre o esforço em onboarding, suporte e documentação para terceiros, que está proposto como "mínimo até haver sinal de uso" em `depth.md`.

Opções para o Breno decidir (registrar em `docs/decisions.md`):

1. **Manter o mini-Tars como projeto de aprendizado**, com foco em arquitetura, testes e avaliações, e divulgar sem promessa de suporte.
2. **Reposicionar em torno das avaliações:** um pequeno kit de avaliação de recuperação de memória que funcione com qualquer servidor MCP (inclusive Basic Memory). Diferencia do que existe e é bom material de portfólio, mas exige validar que alguém quer isso.
3. **Contribuir com o Basic Memory** em vez de criar outro, e usar o mini-Tars só como estudo privado. Aprende-se com código real e o portfólio mostra contribuição aceita.
4. **Parar aqui** e escolher outro projeto de teste do processo (o critério K1 e a regra de "matar cedo" existem para isso).

## Limites desta pesquisa

- Leitura feita só das páginas iniciais dos repositórios, resumidas por ferramenta automática. Detalhes (por exemplo, suporte a MCP no mem0 e no Letta, motores de armazenamento do Letta) não foram confirmados na documentação.
- Não foram avaliados serviços proprietários nem outros projetos de memória para MCP. Uma busca adicional por "MCP memory server" pode revelar mais alternativas.
- Não testei nenhum deles na prática; a comparação de qualidade de recuperação depende do teste da fase 2.
