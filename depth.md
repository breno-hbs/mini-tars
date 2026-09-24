---
status: rascunho
atualizado: 2026-09-23
dono: Breno
---
# Profundidade por item

Decisões base: **projeto de aprendizado** (decisão de 2026-09-23), **outros desenvolvedores podem usar sem promessa de suporte** e **cada um auto-hospeda**. Isso reduz legal e operação (o Breno não guarda dados de ninguém), mas mantém alto o rigor de segurança do software distribuído, de instalação e de documentação.
Regra: Pulado (uma linha de motivo), Mínimo (um parágrafo) ou Completo (documento inteiro).
Se o produto passar a ter versão hospedada ou telemetria, legal, dados, observabilidade e backup sobem para completo.

| Item | Nível | Motivo |
| --- | --- | --- |
| Ideia e pesquisa | Completo | Fase de teste do processo; alimenta todas as decisões |
| Validação barata | Completo, só o teste de recuperação | Hipótese de recuperação é o maior risco (H1). Entrevistas com usuários puladas por decisão do Breno |
| Critérios de parada | Completo | Evita projeto zumbi |
| Modelo de negócio | Pulado | Sem receita e custo recorrente zero (K5) |
| Visão e requisitos | Completo | Base para os agentes |
| Design e identidade | Mínimo | Produto é um servidor e uma CLI; basta nome, tom de voz e documentação clara |
| Arquitetura e ADRs | Completo | Principal objetivo de aprendizado |
| Dados | Mínimo | Esquema, retenção e exclusão documentados; os dados ficam na máquina do usuário |
| Legal e privacidade | Mínimo | Licença de código aberto, aviso "sem garantia" e declaração clara de que nenhum dado sai da máquina do usuário. Confirmar com fonte oficial ou profissional se algo mudar |
| Segurança | Completo | Servidor local sem autenticação exposto por engano é o risco central; dependências, injeção de prompt e instalação segura |
| Avaliações (evals) | Completo | Coração do projeto |
| Estratégia de testes | Completo | Requisito de qualidade |
| Infraestrutura e distribuição | Mínimo | Empacotamento (PyPI ou Docker), CI no GitHub Actions, documentação no GitHub Pages, versionamento. Tudo em planos gratuitos |
| Observabilidade | Pulado | Sem telemetria por padrão; logs locais sem conteúdo da memória |
| Backup e recuperação | Mínimo | Comando de exportação e importação documentado; backup é responsabilidade do usuário |
| Onboarding e documentação de uso | Mínimo até haver sinal de uso | Sem validação de demanda, um README claro com instalação em um comando basta; subir para completo se K3 for atingido |
| Suporte e feedback | Mínimo | Issues no repositório, sem prazo de resposta prometido |
| Go-to-market | Pulado por ora | Primeiro validar com poucos convidados |
| Acessibilidade | Pulado | Sem interface visual no MVP |
| Encerramento | Pulado | Dados ficam com o usuário; basta documentar a exportação |

Revisar esta tabela a cada retrospectiva.
