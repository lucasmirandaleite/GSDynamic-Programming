"""Rua em Dia: otimização exata da ordem de vistoria de pedidos de reparo.

O algoritmo Held-Karp usa programação dinâmica por memoização em um grafo
ponderado. O exemplo incluído é fictício; substitua-o por pontos e estimativas
validados antes de usar como evidência do projeto.
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


def otimizar_rota(dados: dict[str, Any]) -> dict[str, Any]:
    """Encontra a menor rota que sai da base, visita todos os pedidos e retorna.

    DP[mask, atual] = menor tempo restante para visitar todos os pedidos que
    ainda não estão no bitmask e voltar à base, partindo do local 'atual'.

    A versão exata é indicada para pequenos roteiros (até 15 pedidos). Trechos
    podem ser direcionais e indisponíveis (null na matriz).
    """
    locais, pedidos, tempos, vistoria, limite_turno = validar_e_preparar(dados)
    base_idx = 0
    pedido_para_idx = {pedido: i for i, pedido in enumerate(locais) if i > 0}
    completo = (1 << len(pedidos)) - 1
    proxima_parada: dict[tuple[int, int], int] = {}

    @lru_cache(maxsize=None)
    def dp_visitados(mask: int, atual: int) -> float:
        if mask == completo:
            return tempos[atual][base_idx]

        melhor = math.inf
        escolhido: int | None = None
        for pedido_idx, pedido in enumerate(pedidos):
            bit = 1 << pedido_idx
            destino_idx = pedido_para_idx[pedido]
            if mask & bit:
                continue
            trecho = tempos[atual][destino_idx]
            restante = dp_visitados(mask | bit, destino_idx)
            candidato = trecho + restante
            if candidato < melhor:
                melhor = candidato
                escolhido = destino_idx

        if escolhido is not None:
            proxima_parada[(mask, atual)] = escolhido
        return melhor

    tempo_viagem = dp_visitados(0, base_idx)
    if math.isinf(tempo_viagem):
        return {
            "rota_encontrada": False,
            "mensagem": "Não existe uma rota completa com os trechos disponíveis informados.",
            "estados_dp": dp_visitados.cache_info().currsize,
        }

    rota_idx = [base_idx]
    mask = 0
    atual = base_idx
    while mask != completo:
        destino_idx = proxima_parada[(mask, atual)]
        rota_idx.append(destino_idx)
        mask |= 1 << (destino_idx - 1)
        atual = destino_idx
    rota_idx.append(base_idx)

    rota = [locais[i] for i in rota_idx]

    # Indicador de impacto: compara com a ordem original em que os pedidos foram informados.
    ordem_original_idx = [base_idx] + [pedido_para_idx[p] for p in pedidos] + [base_idx]
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
        "rota": rota,
        "tempo_deslocamento_minutos": tempo_viagem,
        "tempo_deslocamento_ordem_original_minutos": tempo_ordem_original_saida,
        "reducao_deslocamento_percentual": reducao_percentual,
        "tempo_vistoria_minutos": tempo_vistoria_total,
        "tempo_total_minutos": tempo_total_turno,
        "limite_turno_minutos": limite_turno,
        "cabe_no_turno": tempo_total_turno <= limite_turno,
        "estados_dp": dp_visitados.cache_info().currsize,
        "pedidos_visitados": len(pedidos),
    }


def carregar_json(caminho: Path) -> dict[str, Any]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError("O arquivo JSON precisa conter um objeto na raiz.")
    return dados


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("dados_demo.json")
    try:
        resultado = otimizar_rota(carregar_json(caminho))
    except (OSError, json.JSONDecodeError, ValueError) as erro:
        print(f"Erro nos dados: {erro}")
        raise SystemExit(1)

    print("RUA EM DIA — ROTEIRO DE VISTORIA")
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
