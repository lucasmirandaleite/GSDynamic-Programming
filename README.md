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
| ODS conectados | **ODS 11 (Cidades e comunidades sustentáveis):** o roteiro de vistoria apoia a organização da manutenção de vias urbanas, contribuindo para cidades mais seguras e com infraestrutura em melhor estado. **ODS 3 (Saúde e bem-estar):** vias em melhor estado reduzem riscos de acidentes e lesões no trânsito (relacionado à meta 3.6). A contribuição é indireta e demonstrativa: o protótipo calcula uma ordem de vistoria, não repara buracos. |

## Descrição da funcionalidade

O módulo `otimizar_rota.py` calcula a menor ordem de deslocamento para uma equipe sair de uma base, visitar todos os pontos de pedidos de tapa-buraco escolhidos para um roteiro e retornar à base. Para cada local, a entrada fornece uma estimativa do tempo de deslocamento entre pares de locais e o tempo reservado à vistoria. A saída mostra a sequência otimizada, os tempos de deslocamento e de vistoria, o total estimado, se a soma cabe no limite de um turno e a redução percentual do deslocamento em relação à ordem original dos pedidos (o indicador de impacto). Na demonstração essa redução é 0%, porque a ordem original já é a ótima; na instância SP156 é de cerca de 1,0%.

A funcionalidade não diagnostica a condição do pavimento, não comprova que um buraco existe e não escolhe quais solicitações a Prefeitura deve reparar. Os pedidos do SP156 representam solicitações feitas por cidadãos, não todos os buracos da cidade.

## Dados e rastreabilidade

- `dados_demo.json`: quatro locais e tempos **inteiramente ilustrativos**. Servem para executar e testar o algoritmo e não representam ruas, medições ou pedidos reais.
- `dados_sp156.json`: instância com três solicitações de tapa-buraco do SP156, em Parque São Rafael, Jardim São Rafael e Jardim Iguatemi (São Paulo), e a Subprefeitura São Mateus como base. Os rótulos **P1, P2 e P3 são identificadores locais deste projeto**, não protocolos nem IDs da Prefeitura.
- `amostra_sp156_tapa_buraco_2014.csv`: amostra mínima das três linhas selecionadas e seus campos publicados, acrescida apenas da coluna local `ID local` (P1–P3).

### Origem da instância `dados_sp156.json`

**Fonte oficial:** Prefeitura de São Paulo, conjunto Dados do SP156: https://dados.prefeitura.sp.gov.br/dataset/0aecfa2b-aa3a-40d4-8183-0d4351b7fd0a/resource/a1e179d8-4c28-4f54-9d5f-47e4c40d45ea/download/arquivofinal2sem2014.xlsx.csv — arquivo `arquivofinal2sem2014.xlsx.csv`, 2º semestre de 2014, consultado em 12/11/2026. O CSV contém as colunas Data de abertura, Canal de atendimento, Assunto, Especificação do assunto, Bairro, Órgão, Status da solicitação e Data do parecer. **Não contém protocolo nem `_id`**; portanto, as três ocorrências são identificadas somente por atributos e recebem identificadores locais P1–P3 na amostra do projeto.

| ID local (projeto) | Bairro no arquivo | Órgão no arquivo | Abertura | Status | Data do parecer |
|---|---|---|---|---|---|
| P1 | PARQUE SAO RAFAEL | SPSM | 2014-07-07 | REALIZADA | 2014-10-13 |
| P2 | JARDIM SAO RAFAEL | SPCS | 2014-07-13 | REALIZADA | 2014-08-08 |
| P3 | JARDIM IGUATEMI | SPSM | 2014-07-23 | REALIZADA | 2014-10-13 |

No arquivo, o órgão responsável por P1 e P3 é SPSM, e o de P2 é SPCS, que parece corresponder a outra subprefeitura. A instância usa a Subprefeitura São Mateus como base única por simplificação do protótipo, e o tempo de deslocamento até o Jardim São Rafael foi estimado pelo grupo a partir dessa base; isso é uma limitação da instância. São solicitações antigas de cidadãos; não são os buracos fotografados atualmente pelo grupo nem uma lista completa de buracos da região. As datas, bairros, status, canal, assunto/especificação, órgão e parecer da amostra são reproduzidos do recurso oficial; os nomes com acentos usados no JSON são rótulos de leitura, e P1–P3 foram atribuídos localmente para referência estável.

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

**Resultado.** Com esses dados, o roteiro mínimo é de 48 min de deslocamento, contra 48,5 min na ordem cronológica de abertura dos pedidos (redução de cerca de 1,0%). Com apenas três pontos, a diferença é pequena; o ganho depende da instância e não é garantido.

Estrutura do JSON:

- `base`: origem e destino final.
- `pedidos`: identificadores/rótulos das paradas.
- `locais`: a base primeiro, depois os pedidos, na mesma ordem de `pedidos`.
- `tempo_deslocamento_minutos`: matriz quadrada de tempos direcionais, com zero na diagonal e `null` para trecho indisponível.
- `tempo_vistoria_minutos`: tempo de cada parada.
- `limite_turno_minutos`: duração do turno.

## Técnica de Programação Dinâmica

O problema é modelado como um grafo ponderado: a base e cada pedido são vértices, e cada trecho disponível é uma aresta dirigida com peso igual ao tempo estimado de deslocamento. O código implementa **Held–Karp** (caixeiro-viajante) com **memoização** — esta entrega seleciona memoização e grafos entre as técnicas de DP. A implementação não afirma usar tabulação.

```text
DP(S, i) = min( tempo(i, j) + DP(S ∪ {j}, j) )   para cada pedido j fora de S
DP(todos, i) = tempo(i, base)
```

`S` é o conjunto de pedidos já visitados (bitmask) e `i` é o local atual. A memoização guarda o resultado de cada estado `(S, i)`, evitando recalcular subproblemas. A rota é reconstruída a partir das próximas paradas escolhidas.

**Complexidade:** tempo `O(n² · 2ⁿ)` e espaço `O(n · 2ⁿ)`, onde `n` é o número de pedidos. Por isso o limite é de 15 pedidos por roteiro; áreas maiores devem ser divididas em roteiros menores.

### Validação e benchmark sintético

Execute `python benchmark_dp.py` para repetir a verificação. O script usa a semente fixa `20261112`, compara Held–Karp com enumeração por força bruta em 300 instâncias aleatórias com 1–7 pedidos (grafos dirigidos e arestas indisponíveis) e cronometra tamanhos 10, 12, 14 e 15. **São benchmarks sintéticos gerados pelo script, não dados de ruas nem estimativas de desempenho de navegação real.**

Medição observada nesta execução: Python 3.12.3, Linux x86_64 (`Linux-6.18.38+-x86_64-with-glibc2.39`), ambiente sandbox compartilhado. Varia com hardware e carga; os tempos são medidos com `time.perf_counter()` e foram capturados na saída do script:

| Pedidos | Estados DP | Tempo observado |
|---:|---:|---:|
| 10 | 5.121 | 0,006029 s |
| 12 | 24.577 | 0,035945 s |
| 14 | 114.689 | 0,213879 s |
| 15 | 245.761 | 0,513071 s |

## Como executar

Requer Python 3.10 ou superior, sem bibliotecas externas. A partir da pasta onde os arquivos foram extraídos:

```bash
python otimizar_rota.py
python -m unittest -v
python benchmark_dp.py
```

Com a instância SP156 ou outro arquivo de dados:

```bash
python otimizar_rota.py dados_sp156.json
```

Os testes cobrem rota mínima, cálculo da redução em relação à ordem original (inclusive ordem impossível), soma de deslocamento e vistoria, turno insuficiente, ausência de rota, matriz malformada, roteiro sem pedidos, instância SP156 identificada por atributos e conferência dos campos/linhas no CSV mínimo.

## Limitações

O algoritmo visita todos os pedidos informados. Ele não prioriza por urgência, não prevê o tempo de reparo e não substitui decisões técnicas da Prefeitura. Os dados de demonstração são fictícios, e os tempos da instância SP156 são estimativas do grupo, não medições de campo. Data e bairro identificam as linhas documentadas por atributos, mas não constituem chave oficial única; P1–P3 são identificadores locais.

## Uso de IA

Os prompts utilizados estão registrados em `prompts.md`.
