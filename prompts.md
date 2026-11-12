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
| 6 | 11/11/2026 | Outra ferramenta de IA | Pedi para localizar 3 pedidos reais de tapa-buraco do SP156 nos bairros São Rafael e Jardim Iguatemi, usando somente dados existentes no arquivo e avisando se não conseguisse acessar a base. | Os 3 pedidos (IDs 8115, 16653 e 33092 do arquivo do 2º semestre de 2014). Conferi que existem na base oficial. |
| 7 | 12/11/2026 | Claude | Enviei os pedidos e as faixas de tempo de deslocamento e pedi para montar a instância no formato do programa. | `dados_sp156.json`, novo teste automatizado e seção de dados no README, com a origem das informações e as suposições declaradas. |

> Se houve outros prompts (por exemplo, para escrever ou depurar o código-base do algoritmo), acrescentem aqui antes de enviar. Registrem apenas o que realmente foi feito.

## O que foi decidido e verificado pelo grupo

- **Decisões do grupo:** o problema (buracos em ruas de São Paulo), o entrevistado (Antônio, que mora numa rua com buracos), os bairros (São Rafael e Jardim Iguatemi), o indicador de impacto e a quantidade de pedidos reais usados.
- **Verificações:** execução dos testes automatizados (`python -m unittest -v`) e comparação do resultado do algoritmo com uma busca por força bruta em instâncias pequenas.
- **Dados:** os 3 pedidos do SP156 vêm da base oficial da Prefeitura e foram conferidos pelo grupo no arquivo original. Os tempos de deslocamento foram consultados no Google Maps pelo grupo; o ponto médio das faixas, a simetria entre ida e volta e os 10 minutos de vistoria são suposições do grupo, declaradas no README.
