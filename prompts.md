# Registro de prompts — Dynamic Programming (Rua em Dia)

Uso de IA (Claude) como copiloto: revisão do trabalho contra os requisitos da disciplina, ajustes de documentação e dúvidas sobre as regras da GS. As decisões de projeto foram do grupo.

## Prompts usados

| # | Data | Ferramenta | Prompt (resumo) | O que foi aproveitado |
|---|---|---|---|---|
| 1 | 10/11/2026 | Claude | Enviei o PDF do desafio, a ideia da GS (Rua em Dia) e o ZIP da disciplina e pedi para avaliar se o trabalho atende aos requisitos de Dynamic Programming. | Lista de lacunas: faltavam a Ficha da CitizenTech no README, o `prompts.md`, os nomes completos e a correção das instruções de execução. |
| 2 | 10/11/2026 | Claude | Informei os dados do grupo (nomes completos, entrevistado, bairros) e pedi ajuda para fechar a Ficha. | README revisado com a Ficha da CitizenTech e o `prompts.md`. |
| 3 | 10–11/11/2026 | Claude | Perguntei se a GS exige dados reais e entrevistas com pessoas reais, e o que falta para concluir a disciplina. | Esclarecimento das regras do briefing (dados simulados ou públicos com fonte; entrevista como parte da pesquisa da equipe). |
| 4 | 11/11/2026 | Claude | Perguntei o que é o `prompts.md` e se os dados do SP156 eram necessários. | Decisão de incluir poucos pedidos reais, com a fonte e o método documentados. |
| 5 | 11/11/2026 | Claude | Escolhi o indicador "redução percentual do tempo de deslocamento em relação à ordem original" e pedi para incluí-lo. | Trecho de código que calcula o indicador e dois testes novos, que revisei junto com o resultado. |

> Se houve outros prompts (por exemplo, para escrever ou depurar o código-base do algoritmo), acrescentem aqui antes de enviar. Registrem apenas o que realmente foi feito.

## O que foi decidido e verificado pelo grupo

- **Decisões do grupo:** o problema (buracos em ruas de São Paulo), o entrevistado (Antônio, que mora numa rua com buracos), os bairros (São Rafael e Jardim Guatemi), o indicador de impacto e a quantidade de pedidos reais usados.
- **Verificações:** execução dos testes automatizados (`python -m unittest -v`) e comparação do resultado do algoritmo com uma busca por força bruta em instâncias pequenas.
- **Dados:** a IA não forneceu dados reais. Os pedidos do SP156 devem ser extraídos pelo grupo da base oficial, com a fonte indicada no README.
