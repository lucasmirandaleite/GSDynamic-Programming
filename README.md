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
| Cidade e bairro | São Paulo / São Rafael e Jardim Iguatemi |
| Cidadão beneficiado | Moradores e motoristas de ruas com buracos. Entrevistado: Antônio Lino Júnior, integrante do grupo, morador de uma rua com buracos. |
| Problema, em uma frase | Buracos nas ruas atrapalham quem circula de carro, e o morador tem dificuldade de acompanhar os pedidos de reparo já registrados. |
| Como funciona | Organiza e apresenta pedidos de tapa-buraco registrados no SP156 e mostra como uma equipe de manutenção poderia ordenar uma rota de vistoria entre vários pontos. É um protótipo limitado às entregas das disciplinas, não uma plataforma completa. |
| O que cada parte faz | **Dynamic Programming:** calcula a ordem de vistoria de menor tempo estimado (este repositório). **Data Science:** analisa dados do SP156 sobre pedidos de tapa-buraco com regressão linear (tempo de atendimento) e logística (probabilidade de o pedido ser finalizado). **Network Architect Solutions:** projeta a rede da base de manutenção que usa o sistema. **AR-VR:** vídeo 3D que mostra o problema do buraco e a rota de vistoria. |
| Link do repositório | https://github.com/lucasmirandaleite/GSDynamic-Programming |
| Indicador de impacto | Redução percentual do tempo de deslocamento do roteiro otimizado em relação à ordem original em que os pedidos foram informados. |
| ODS conectados | ODS 3 (Saúde e bem-estar) e ODS 11 (Cidades e comunidades sustentáveis) |

## Descrição da funcionalidade

O módulo `otimizar_rota.py` calcula a menor ordem de deslocamento para uma equipe sair de uma base, visitar todos os pontos de pedidos de tapa-buraco escolhidos para um roteiro e retornar à base. Para cada local, a entrada fornece uma estimativa do tempo de deslocamento entre pares de locais e o tempo reservado à vistoria. A saída mostra a sequência otimizada, os tempos de deslocamento e de vistoria, o total estimado, se a soma cabe no limite de um turno e a redução percentual do deslocamento em relação à ordem original dos pedidos (o indicador de impacto). Na demonstração essa redução é 0%, porque a ordem original já é a ótima; na instância do SP156 é de cerca de 1,0%.

A funcionalidade não diagnostica a condição do pavimento, não comprova que um buraco existe e não escolhe quais solicitações a Prefeitura deve reparar. Os pedidos do SP156 representam solicitações feitas por cidadãos, não todos os buracos da cidade.

## Dados

- `dados_demo.json`: quatro locais e tempos **inteiramente ilustrativos**. Servem para executar e testar o algoritmo e não representam ruas, medições ou pedidos reais.
- `dados_sp156.json`: instância com **3 pedidos reais de tapa-buraco** do SP156, em Parque São Rafael, Jardim São Rafael e Jardim Iguatemi (São Paulo), e a Subprefeitura São Mateus como base.

### Origem da instância `dados_sp156.json`

**Pedidos.** Fonte: Dados do SP156, Prefeitura de São Paulo (https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156), arquivo do 2º semestre de 2014 (`arquivofinal2sem2014.xlsx.csv`), serviço "Tapa-buraco", consultado em 11/11/2026. O arquivo não tem protocolo, rua nem coordenadas; os identificadores abaixo são o `_id` do DataStore oficial, usados só para localizar as linhas. Os rótulos de bairro são os do arquivo.

| ID DataStore | Bairro (rótulo no arquivo) | Status | Abertura | Data do parecer |
|---|---|---|---|---|
| 8115 | Parque São Rafael | REALIZADA | 07/07/2014 | 13/10/2014 |
| 16653 | Jardim São Rafael | REALIZADA | 13/07/2014 | 08/08/2014 |
| 33092 | Jardim Iguatemi | REALIZADA | 23/07/2014 | 13/10/2014 |

São solicitações antigas de cidadãos; não são os buracos fotografados atualmente pelo grupo nem uma lista completa de buracos da região.

**Tempos de deslocamento.** Estimados pelo grupo no Google Maps, de carro, entre pontos de referência de cada bairro (o arquivo não traz a rua). O aplicativo mostrou faixas de tempo; usamos o ponto médio de cada faixa e o mesmo valor nos dois sentidos:

| Trecho | Faixa informada | Valor usado |
|---|---|---|
| Subprefeitura São Mateus ↔ Parque São Rafael | 10–18 min | 14 min |
| Subprefeitura São Mateus ↔ Jardim São Rafael | 9–18 min | 13,5 min |
| Subprefeitura São Mateus ↔ Jardim Iguatemi | 10–17 min | 13,5 min |
| Parque São Rafael ↔ Jardim São Rafael | 4–6 min | 5 min |
| Parque São Rafael ↔ Jardim Iguatemi | 12–20 min | 16 min |
| Jardim São Rafael ↔ Jardim Iguatemi | 12–20 min | 16 min |

**Tempo de vistoria.** 10 minutos por pedido, valor assumido pelo grupo. O turno considerado é de 240 minutos.

**Resultado.** Com esses dados, o roteiro mínimo é de 48 min de deslocamento, contra 48,5 min na ordem cronológica de abertura dos pedidos (redução de cerca de 1,0%). Com apenas três pontos, a diferença é pequena; o ganho cresce com o número de pedidos do roteiro.


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

Com a instância dos pedidos reais do SP156 ou outro arquivo de dados:

```bash
python otimizar_rota.py dados_sp156.json
```

`test_otimizar_rota.py` (9 testes) cobre: rota mínima visitando todos os pedidos e voltando à base; cálculo da redução em relação à ordem original, inclusive quando essa ordem é impossível; soma de deslocamento e vistoria; turno insuficiente; ausência de rota quando os trechos estão indisponíveis; matriz malformada; roteiro sem pedidos; e a instância com pedidos reais do SP156.

## Limitações

O algoritmo visita todos os pedidos informados. Ele não prioriza por urgência, não prevê o tempo de reparo e não substitui decisões técnicas da Prefeitura. Os dados de demonstração são fictícios, e os tempos da instância do SP156 são estimativas do grupo, não medições de campo.

## Uso de IA

Os prompts utilizados estão registrados em `prompts.md`.
