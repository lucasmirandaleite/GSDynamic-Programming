# Rua em Dia — Dynamic Programming (Global Solution FIAP 2026.2)

## Integrantes

| Nome completo | RM |
|---|---|
| Lucas Miranda Leite | 570948 |
| Antônio Lino Júnior | 571090 |

## Ficha da CitizenTech

| Campo | Resposta |
|---|---|
| Nome da CitizenTech | Rua em Dia |
| Cidade e bairro | São Paulo / São Rafael e Jardim Guatemi |
| Cidadão beneficiado | Moradores e motoristas de ruas com buracos. Entrevistado: Antônio Lino Júnior, integrante do grupo, morador de uma rua com buracos. |
| Problema, em uma frase | Buracos nas ruas atrapalham quem circula de carro, e o morador tem dificuldade de acompanhar os pedidos de reparo já registrados. |
| Como funciona | Organiza e apresenta pedidos de tapa-buraco registrados no SP156 e mostra como uma equipe de manutenção poderia ordenar uma rota de vistoria entre vários pontos. É um protótipo limitado às entregas das disciplinas, não uma plataforma completa. |
| O que cada parte faz | **Dynamic Programming:** calcula a ordem de vistoria de menor tempo estimado (este repositório). **[PREENCHER: demais disciplinas]** |
| Link do repositório | **[PREENCHER]** |
| Indicador de impacto | Redução percentual do tempo de deslocamento do roteiro otimizado em relação à ordem original em que os pedidos foram informados. |
| ODS conectados | ODS 3 (Saúde e bem-estar) e ODS 11 (Cidades e comunidades sustentáveis) |

## Descrição da funcionalidade

O módulo `otimizar_rota.py` calcula a menor ordem de deslocamento para uma equipe sair de uma base, visitar todos os pontos de pedidos de tapa-buraco escolhidos para um roteiro e retornar à base. Para cada local, a entrada fornece uma estimativa do tempo de deslocamento entre pares de locais e o tempo reservado à vistoria. A saída mostra a sequência otimizada, os tempos de deslocamento e de vistoria, o total estimado, se a soma cabe no limite de um turno e a redução percentual do deslocamento em relação à ordem original dos pedidos (o indicador de impacto). Na demonstração essa redução é 0%, porque a ordem original já é a ótima.

A funcionalidade não diagnostica a condição do pavimento, não comprova que um buraco existe e não escolhe quais solicitações a Prefeitura deve reparar. Os pedidos do SP156 representam solicitações feitas por cidadãos, não todos os buracos da cidade.

## Dados

- `dados_demo.json`: quatro locais e tempos **inteiramente ilustrativos**. Servem para executar e testar o algoritmo e não representam ruas, medições ou pedidos reais.
- **[PREENCHER ou remover esta linha]** `dados_sp156.json`: pedidos reais de tapa-buraco selecionados no SP156 (fonte: https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156, consultado em **[data]**), com tempos de deslocamento estimados por **[método/fonte]**.

Estrutura do JSON:

- `base`: origem e destino final.
- `pedidos`: identificadores das paradas.
- `locais`: a base primeiro, depois os pedidos, na mesma ordem de `pedidos`.
- `tempo_deslocamento_minutos`: matriz quadrada de tempos direcionais, com zero na diagonal e `null` para trecho indisponível.
- `tempo_vistoria_minutos`: tempo de cada parada.
- `limite_turno_minutos`: duração do turno.

## Técnica de Programação Dinâmica

O problema é modelado como um grafo ponderado: a base e cada pedido são vértices, e cada trecho disponível é uma aresta com peso igual ao tempo estimado de deslocamento. O código implementa **Held–Karp** (caixeiro-viajante) com **memoização**.

```text
DP(S, i) = min( tempo(i, j) + DP(S ∪ {j}, j) )   para cada pedido j fora de S
DP(todos, i) = tempo(i, base)
```

`S` é o conjunto de pedidos já visitados (bitmask) e `i` é o local atual. A memoização guarda o resultado de cada estado `(S, i)`, evitando recalcular subproblemas. A rota é reconstruída a partir das próximas paradas escolhidas.

**Complexidade:** tempo `O(n² · 2ⁿ)` e espaço `O(n · 2ⁿ)`, onde `n` é o número de pedidos. Por isso o limite é de 15 pedidos por roteiro; áreas maiores devem ser divididas em roteiros menores.

Medição em matrizes aleatórias sintéticas (Python 3.12, valores variam conforme a máquina):

| Pedidos | Estados memorizados | Tempo |
|---|---|---|
| 10 | 5.121 | ~0,01 s |
| 12 | 24.577 | ~0,06 s |
| 14 | 114.689 | ~0,36 s |
| 15 | 245.761 | ~1,0 s |

O resultado foi conferido contra uma busca por força bruta em 300 instâncias com até 7 pedidos, incluindo trechos indisponíveis, sem divergências.

## Como executar

Requer Python 3.10 ou superior, sem bibliotecas externas. A partir da pasta onde os arquivos foram extraídos:

```bash
python otimizar_rota.py
python -m unittest -v
```

Com outro arquivo de dados:

```bash
python otimizar_rota.py caminho/para/instancia.json
```

`test_otimizar_rota.py` (8 testes) cobre: rota mínima visitando todos os pedidos e voltando à base; cálculo da redução em relação à ordem original, inclusive quando essa ordem é impossível; soma de deslocamento e vistoria; turno insuficiente; ausência de rota quando os trechos estão indisponíveis; matriz malformada; e roteiro sem pedidos.

## Limitações

O algoritmo visita todos os pedidos informados. Ele não prioriza por urgência, não prevê o tempo de reparo e não substitui decisões técnicas da Prefeitura. Os dados de demonstração são fictícios.

## Uso de IA

Os prompts utilizados estão registrados em `prompts.md`.
