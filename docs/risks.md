# Riscos

Revisar a cada retrospectiva. Todo risco precisa de dono e data de revisão.

| # | Risco | Prob. | Impacto | O que fazer | Dono | Revisão |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Busca simples não recupera bem | Alta (K1 passou por um acerto: 72% no teste reservado; os erros que restam são de vocabulário diferente) | Alto | Testar alternativas antes de construir: assistente reescreve a consulta, expansão de sinônimos ou embeddings locais; repetir com conjunto de teste reservado; definir regra de desempate | Breno | Fim da fase 2 |
| R2 | Servidor local exposto na rede sem autenticação (usuário abre a porta por engano) | Média | Muito alto | Escutar só em 127.0.0.1 por padrão; exigir token para qualquer outra interface; aviso claro na documentação | Breno | Fase de arquitetura |
| R12 | Busca que devolve fato irrelevante com confiança quando a resposta não existe (medido: 4 de 5 no teste reservado; 3 de 6 no ajuste; piora com o tamanho do corpus; limiar relativo 0,3 perde muitos acertos) | Alta | Médio | Limiar mínimo de pontuação e o assistente instruído a descartar resultados sem relação; medir com um conjunto separado de perguntas sem resposta | Breno | Próximo experimento |
| R3 | Injeção de prompt: texto salvo na memória manipula o assistente | Média | Alto | Tratar todo conteúdo recuperado como dado, nunca como instrução; guardrails documentados | Breno | Fase de arquitetura |
| R4 | Instalação difícil afasta os usuários (H3) | Média | Alto | Instalação em um comando; testar instalação limpa em CI; acompanhar issues de instalação após o lançamento | Breno | Antes do 1º release |
| R5 | Vulnerabilidade em dependência ou no próprio código distribuído | Média | Alto | Verificação automática de dependências no CI; K6 define a resposta | Breno | Mensal |
| R6 | Atualização quebra o banco de dados do usuário e ele perde memória | Baixa | Alto | Migrações versionadas e testadas; backup automático antes de migrar; exportação documentada | Breno | Antes do 1º release |
| R7 | Tempo do Breno não comporta suporte e manutenção | Média | Médio | K4; limitar o número de usuários convidados | Breno | Semanal |
| R8 | Projeto vira só planejamento, sem código | Média | Médio | Prazo para as fases 0 e 1; validação barata antes de qualquer documento extra | Breno | Semanal |
| R9 | Mudança para versão hospedada sem rever legal e dados | Baixa | Alto | Regra: qualquer versão hospedada ou telemetria exige revisar `depth.md` (legal, dados, observabilidade, backup) antes | Breno | A cada decisão de escopo |
| R10 | Ninguém além do Breno usa | Alta | Baixo (projeto de aprendizado) | Aceito. Não investir em suporte antes de haver sinal de uso (K3) | Breno | 6 semanas após o lançamento |
| R11 | O portfólio ser lido como "cópia do Basic Memory" | Média | Médio | Deixar claro no README o objetivo de aprendizado, citar o Basic Memory como referência e destacar o que é próprio: avaliações reproduzíveis e ADRs | Breno | Antes de publicar |
| R13 | Página aberta no navegador chama o servidor HTTP local (ataque por origem cruzada ou rebinding de DNS) e lê ou altera a memória | Média | Alto | Modo HTTP valida `Host` e `Origin`, recusa origens não locais; stdio como padrão (ADR-0003, ADR-0005) | Breno | Antes do 1º release |
