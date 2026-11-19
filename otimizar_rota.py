"""Rua em Dia: otimização exata da ordem de vistoria de pedidos de reparo.

O algoritmo Held-Karp usa programação dinâmica em um grafo ponderado, com duas
implementações equivalentes: memoização (top-down, padrão) e tabulação
(bottom-up). O exemplo dados_demo.json é fictício; dados_sp156.json traz três
pedidos reais do SP156 com tempos estimados pelo grupo (veja o README).
"""
from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

MAX_PARADAS_EXATAS = 15


def validar_e_preparar(dados: dict[str, Any]) -> tuple[list[str], list[str], list[list[float]], dict[str, float], float]:
    """Valida a instância e converte null da matriz em trecho indisponível."""
    base = dados.get("base")
    paradas = dados.get("pedidos", [])
    locais = dados.get("locais", [])
    matriz_original = dados.get("tempo_deslocamento_minutos", [])
    tempo_vistoria = dados.get("tempo_vistoria_minutos", {})
    limite_turno = dados.get("limite_turno_minutos", 240)

    if not isinstance(base, str) or not base:
        raise ValueError("Informe um nome não vazio em 'base'.")
    if not isinstance(paradas, list) or any(not isinstance(p, str) or not p for p in paradas):
        raise ValueError("'pedidos' deve ser uma lista de nomes não vazios.")
    if len(paradas) != len(set(paradas)) or base in paradas:
        raise ValueError("Os pedidos devem ser únicos e não podem incluir a base.")
    if len(paradas) > MAX_PARADAS_EXATAS:
        raise ValueError(
            f"A busca exata aceita até {MAX_PARADAS_EXATAS} pedidos por roteiro. "
            "Divida o conjunto em turnos ou áreas menores."
        )

    esperados = [base, *paradas]
    if locais != esperados:
        raise ValueError("'locais' deve conter primeiro a base e depois os pedidos na mesma ordem.")
    if not isinstance(matriz_original, list) or len(matriz_original) != len(esperados):
        raise ValueError("A matriz de deslocamento deve ter uma linha por local.")

    matriz: list[list[float]] = []
    for linha in matriz_original:
        if not isinstance(linha, list) or len(linha) != len(esperados):
            raise ValueError("A matriz de deslocamento precisa ser quadrada.")
        linha_convertida: list[float] = []
        for valor in linha:
            if valor is None:
                linha_convertida.append(math.inf)
            elif isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor >= 0:
                linha_convertida.append(float(valor))
            else:
                raise ValueError("Tempos devem ser números não negativos ou null para trecho indisponível.")
        matriz.append(linha_convertida)

    if any(matriz[i][i] != 0 for i in range(len(esperados))):
        raise ValueError("A diagonal da matriz deve ser zero (tempo do local para ele mesmo).")
    if not isinstance(tempo_vistoria, dict):
        raise ValueError("'tempo_vistoria_minutos' deve ser um objeto por pedido.")
    tempos: dict[str, float] = {}
    for pedido in paradas:
        valor = tempo_vistoria.get(pedido)
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor < 0:
            raise ValueError(f"Informe tempo de vistoria não negativo para {pedido}.")
        tempos[pedido] = float(valor)
    if not isinstance(limite_turno, (int, float)) or isinstance(limite_turno, bool) or limite_turno < 0:
        raise ValueError("'limite_turno_minutos' precisa ser um número não negativo.")

    return esperados, paradas, matriz, tempos, float(limite_turno)


def _resolver_memoizacao(tempos: list[list[float]], n: int) -> tuple[float, list[int], int]:
    """Held-Karp top-down: DP(mask, atual) com memoização (lru_cache).

    DP(mask, atual) = menor tempo restante para visitar os pedidos que ainda não
    estão em 'mask' e voltar à base, partindo de 'atual'. Índice 0 é a base e o
    pedido k (0-based) ocupa o índice k + 1.
    """
    completo = (1 << n) - 1
    proxima_parada: dict[tuple[int, int], int] = {}

    @lru_cache(maxsize=None)
    def dp_visitados(mask: int, atual: int) -> float:
        if mask == completo:
            return tempos[atual][0]

        melhor = math.inf
        escolhido: int | None = None
        for pedido_idx in range(n):
            bit = 1 << pedido_idx
            if mask & bit:
                continue
            destino_idx = pedido_idx + 1
            candidato = tempos[atual][destino_idx] + dp_visitados(mask | bit, destino_idx)
            if candidato < melhor:
                melhor = candidato
                escolhido = destino_idx

        if escolhido is not None:
            proxima_parada[(mask, atual)] = escolhido
        return melhor

    tempo_viagem = dp_visitados(0, 0)
    estados = dp_visitados.cache_info().currsize
    if math.isinf(tempo_viagem):
        return tempo_viagem, [], estados

    rota_idx = [0]
    mask = 0
    atual = 0
    while mask != completo:
        destino_idx = proxima_parada[(mask, atual)]
        rota_idx.append(destino_idx)
        mask |= 1 << (destino_idx - 1)
        atual = destino_idx
    rota_idx.append(0)
    return tempo_viagem, rota_idx, estados


def _resolver_tabulacao(tempos: list[list[float]], n: int) -> tuple[float, list[int], int]:
    """Held-Karp bottom-up: tabela dp[mask][ultimo] preenchida em ordem crescente de mask.

    dp[mask][ultimo] = menor tempo para sair da base, visitar exatamente os pedidos
    de 'mask' e terminar em 'ultimo' (que pertence a 'mask'). O custo final é o
    mínimo de dp[completo][ultimo] + tempo(ultimo, base). 'pai' guarda o pedido
    anterior para reconstruir a rota.
    """
    if n == 0:
        return tempos[0][0], [0, 0], 1

    inf = math.inf
    tamanho = 1 << n
    dp = [[inf] * n for _ in range(tamanho)]
    pai = [[-1] * n for _ in range(tamanho)]
    for j in range(n):
        dp[1 << j][j] = tempos[0][j + 1]

    for mask in range(1, tamanho):
        for ultimo in range(n):
            custo_atual = dp[mask][ultimo]
            if custo_atual == inf or not (mask >> ultimo) & 1:
                continue
            for proximo in range(n):
                if (mask >> proximo) & 1:
                    continue
                novo = custo_atual + tempos[ultimo + 1][proximo + 1]
                nova_mask = mask | (1 << proximo)
                if novo < dp[nova_mask][proximo]:
                    dp[nova_mask][proximo] = novo
                    pai[nova_mask][proximo] = ultimo

    completo = tamanho - 1
    estados = n * (1 << (n - 1))  # pares (mask, ultimo) com ultimo em mask
    melhor = inf
    fim = -1
    for ultimo in range(n):
        custo = dp[completo][ultimo] + tempos[ultimo + 1][0]
        if custo < melhor:
            melhor = custo
            fim = ultimo
    if math.isinf(melhor):
        return melhor, [], estados

    sequencia: list[int] = []
    mask, ultimo = completo, fim
    while ultimo != -1:
        sequencia.append(ultimo + 1)
        anterior = pai[mask][ultimo]
        mask ^= 1 << ultimo
        ultimo = anterior
    return melhor, [0, *reversed(sequencia), 0], estados


METODOS = ("memoizacao", "tabulacao")


def otimizar_rota(dados: dict[str, Any], metodo: str = "memoizacao") -> dict[str, Any]:
    """Encontra a menor rota que sai da base, visita todos os pedidos e retorna.

    'metodo' escolhe a implementação de programação dinâmica: "memoizacao"
    (padrão) ou "tabulacao". Ambas calculam o mesmo custo mínimo; em empates, a
    rota devolvida pode diferir. A busca exata é indicada para pequenos roteiros
    (até 15 pedidos). Trechos podem ser direcionais e indisponíveis (null).
    """
    if metodo not in METODOS:
        raise ValueError(f"Método inválido: {metodo!r}. Use um de {METODOS}.")
    locais, pedidos, tempos, vistoria, limite_turno = validar_e_preparar(dados)
    pedido_para_idx = {pedido: i for i, pedido in enumerate(locais) if i > 0}
    n = len(pedidos)

    resolver = _resolver_memoizacao if metodo == "memoizacao" else _resolver_tabulacao
    tempo_viagem, rota_idx, estados = resolver(tempos, n)

    if math.isinf(tempo_viagem):
        return {
            "rota_encontrada": False,
            "mensagem": "Não existe uma rota completa com os trechos disponíveis informados.",
            "metodo": metodo,
            "estados_dp": estados,
        }

    rota = [locais[i] for i in rota_idx]

    # Indicador de impacto: compara com a ordem original em que os pedidos foram informados.
    ordem_original_idx = [0] + [pedido_para_idx[p] for p in pedidos] + [0]
    tempo_ordem_original = sum(
        tempos[a][b] for a, b in zip(ordem_original_idx, ordem_original_idx[1:])
    )
    if math.isinf(tempo_ordem_original):
        tempo_ordem_original_saida = None
        reducao_percentual = None
    else:
        tempo_ordem_original_saida = tempo_ordem_original
        reducao_percentual = (
            (tempo_ordem_original - tempo_viagem) / tempo_ordem_original * 100
            if tempo_ordem_original > 0
            else 0.0
        )
    tempo_vistoria_total = sum(vistoria[pedido] for pedido in pedidos)
    tempo_total_turno = tempo_viagem + tempo_vistoria_total

    return {
        "rota_encontrada": True,
        "metodo": metodo,
        "rota": rota,
        "tempo_deslocamento_minutos": tempo_viagem,
        "tempo_deslocamento_ordem_original_minutos": tempo_ordem_original_saida,
        "reducao_deslocamento_percentual": reducao_percentual,
        "tempo_vistoria_minutos": tempo_vistoria_total,
        "tempo_total_minutos": tempo_total_turno,
        "limite_turno_minutos": limite_turno,
        "cabe_no_turno": tempo_total_turno <= limite_turno,
        "estados_dp": estados,
        "pedidos_visitados": n,
    }


def carregar_json(caminho: Path) -> dict[str, Any]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError("O arquivo JSON precisa conter um objeto na raiz.")
    return dados


def main() -> None:
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    metodo = "tabulacao" if "--tabulacao" in sys.argv[1:] else "memoizacao"
    caminho = Path(argumentos[0]) if argumentos else Path(__file__).with_name("dados_demo.json")
    try:
        resultado = otimizar_rota(carregar_json(caminho), metodo)
    except (OSError, json.JSONDecodeError, ValueError) as erro:
        print(f"Erro nos dados: {erro}")
        raise SystemExit(1)

    print("RUA EM DIA — ROTEIRO DE VISTORIA")
    print(f"Método de DP: {'tabulação (bottom-up)' if metodo == 'tabulacao' else 'memoização (top-down)'}")
    if not resultado["rota_encontrada"]:
        print(resultado["mensagem"])
        print(f"Estados de DP avaliados: {resultado['estados_dp']}")
        return
    print("Rota:", " -> ".join(resultado["rota"]))
    print(f"Deslocamento: {resultado['tempo_deslocamento_minutos']:.1f} min")
    original = resultado["tempo_deslocamento_ordem_original_minutos"]
    if original is None:
        print("Ordem original dos pedidos: não é possível percorrer com os trechos informados")
    else:
        print(f"Ordem original dos pedidos: {original:.1f} min")
        print(f"Redução do deslocamento: {resultado['reducao_deslocamento_percentual']:.1f}%")
    print(f"Vistorias: {resultado['tempo_vistoria_minutos']:.1f} min")
    print(f"Total estimado: {resultado['tempo_total_minutos']:.1f} min")
    print(f"Limite do turno: {resultado['limite_turno_minutos']:.0f} min")
    print("Cabe no turno:", "sim" if resultado["cabe_no_turno"] else "não")
    print(f"Estados de DP avaliados: {resultado['estados_dp']}")
    print("Aviso: tempos estimados, não medidos em campo. Veja a origem dos dados no README.")


if __name__ == "__main__":
    main()
