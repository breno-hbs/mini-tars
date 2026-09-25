# mini-tars

[![CI](https://github.com/breno-hbs/mini-tars/actions/workflows/ci.yml/badge.svg)](https://github.com/breno-hbs/mini-tars/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mini-tars)](https://pypi.org/project/mini-tars/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Servidor de memória (MCP) auto-hospedado, em Python, para assistentes de IA guardarem e recuperarem fatos sobre seus projetos entre sessões.

**Status:** fase 4 (entregar) concluída. Publicado no [PyPI](https://pypi.org/project/mini-tars/). Projeto de aprendizado, sem garantia e sem promessa de suporte — outras pessoas podem usar, por sua conta e risco.

- Nenhum dado sai da sua máquina: sem telemetria, sem conta, sem chamada de rede de saída.
- Escuta só em 127.0.0.1 por padrão (veja "Modo HTTP" abaixo).
- Requer Python 3.11 ou mais novo.

## Instalação

Com [pipx](https://pipx.pypa.io/) — um comando, sem misturar com outros projetos Python da sua máquina:

```bash
pipx install mini-tars
```

Sem `pipx` instalado: `python -m pip install --user pipx` primeiro (ou veja as instruções do pipx para o seu sistema). Sem `pipx` de jeito nenhum, um `pip install mini-tars` normal também funciona, de preferência dentro de um ambiente virtual (`python -m venv .venv`).

Para instalar a partir do código-fonte deste repositório em vez do PyPI (por exemplo, para testar uma mudança ainda não publicada), troque `mini-tars` por `.` nos comandos acima, executando a partir da raiz do repositório.

Confira que instalou:

```bash
mini-tars --version
```

## Uso com um assistente de IA (Claude Code)

```bash
claude mcp add mini-tars -- mini-tars serve
```

Isso inicia o mini-tars por stdio (o padrão, sem porta de rede) sempre que o Claude Code precisar. As ferramentas disponíveis são `remember`, `search`, `forget` e `list_recent`; o texto de cada fato vem marcado como dado do usuário, não como instrução (veja `01-definir/arquitetura.md`, seção de segurança).

## Onde ficam os dados

Por padrão, num arquivo de banco no diretório de dados do seu usuário (`~/.local/share/mini-tars/memory.db` no Linux, equivalente no Windows e no macOS). Para usar outro caminho:

```bash
export MINI_TARS_DB=/caminho/que/eu/quiser/memory.db   # ou --db na linha de comando
```

**Apagar um fato (`forget`) remove o texto do banco de verdade**, mas os arquivos `.bak-vN` que o programa cria antes de migrar o banco para uma versão nova mantêm uma cópia antiga. Apague-os também se quiser eliminar o fato de vez.

## Backup: exportar e importar

```bash
mini-tars export backup.json
mini-tars import backup.json --db banco-novo.db
```

Importar exige um banco vazio (os ids originais são preservados, o que evita colisão). Um arquivo de versão de esquema desconhecida, ou fora do formato esperado, falha com uma mensagem clara, sem tocar no banco de destino.

## Modo HTTP (opcional)

```bash
mini-tars serve --http
```

Escuta em `127.0.0.1:8765` por padrão, sem exigir token. Escutar em outra interface (`--host 0.0.0.0`, por exemplo) exige a variável `MINI_TARS_TOKEN`, e o servidor recusa iniciar sem ela.

## Desinstalar

```bash
pipx uninstall mini-tars
```

Isso não apaga os dados guardados. Para remover tudo, apague também o arquivo do banco (veja "Onde ficam os dados" acima) e os arquivos `.bak-vN` ao lado dele.

## Como o projeto foi pensado

- Visão, requisitos e arquitetura: `01-definir/visao.md`, `01-definir/requisitos.md`, `01-definir/arquitetura.md`.
- Decisões, uma a uma, com alternativas consideradas: `docs/adr/`.
- Histórico de decisões e o estado atual do trabalho: `docs/decisions.md`, `docs/handoff.md`.
- Como medimos a qualidade da busca, de forma reproduzível: `evals/README.md`.

## Licença

MIT — veja `LICENSE`.
