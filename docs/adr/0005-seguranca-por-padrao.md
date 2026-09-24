# ADR-0005: Seguro por padrão: escuta local, token fora do local, conteúdo como dado, sem telemetria

- Status: aceito (Breno, 2026-09-23)
- Data: 2026-09-23
- Relacionado: RNF-01, RNF-02, RNF-03; R2, R3, R13; `CLAUDE.md`

## Contexto
Um servidor de memória guarda informação de projetos e será lido por um assistente que pode executar ações. Outras pessoas vão instalar sem o Breno por perto.

## Decisão
1. Padrão local: stdio, ou HTTP em 127.0.0.1. Escutar em outra interface exige token e o servidor recusa iniciar sem ele.
2. No modo HTTP, validar `Host` e `Origin` para que páginas abertas no navegador não consigam chamar o servidor local (R13).
3. O texto dos fatos sai sempre dentro de um campo de dados, com aviso de que é conteúdo do usuário e não instrução. O servidor não afirma controlar o assistente.
4. Sem telemetria, sem chamadas de rede de saída, logs sem o texto dos fatos.
5. O token vem de variável de ambiente ou arquivo fora do repositório; nunca é impresso em log. O agente de desenvolvimento nunca lê nem edita credenciais (`CLAUDE.md`).

## Alternativas consideradas
| Alternativa | Por que não |
| --- | --- |
| Autenticação por usuário | Fora do escopo: uma pessoa por banco |
| Confiar só na rede local | Falha quando o usuário abre a porta por engano (R2) |
| Filtrar o conteúdo dos fatos por padrões de injeção | Lista sempre incompleta e dá falsa segurança; preferimos marcar como dado e documentar o limite |

## Consequências
- O risco de injeção de prompt reduz, mas não desaparece: depende do cliente e do assistente. A documentação deve dizer isso claramente.
- Mais testes de segurança obrigatórios no CI.
