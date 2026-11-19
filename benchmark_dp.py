"""Validação e benchmark sintético do Held–Karp de Rua em Dia (memoização e tabulação).

Uso: python benchmark_dp.py
Nenhum dado de ruas é usado: todas as matrizes são geradas pelo script.
"""
from __future__ import annotations

import itertools
import platform
import random
import time

from otimizar_rota import METODOS, otimizar_rota

SEED = 20261112
CASOS_VALIDACAO = 300
TAMANHOS_BENCHMARK = (10, 12, 14, 15)
TAMANHOS_GANHO = (5, 8, 10)
INSTANCIAS_GANHO = 200


def criar_instancia(n: int, rng: random.Random, *, arestas_indisponiveis: bool) -> dict:
    """Cria grafo direcionado aleatório com base 0 e n pedidos."""
    nomes = [f"Pedido {i + 1}" for i in range(n)]
    locais = ["Base", *nomes]
    matriz: list[list[int | None]] = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(n + 1):
            if i == j:
                continue
            custo = rng.randint(1, 50)
            matriz[i][j] = None if arestas_indisponiveis and rng.random() < 0.22 else custo

    # Assegura trecho indisponível e assimetria quando há ao menos dois pedidos.
    if arestas_indisponiveis and n >= 2:
        matriz[1][2] = None
        matriz[2][1] = rng.randint(1, 50)

    return {
        "base": "Base",
        "pedidos": nomes,
        "locais": locais,
        "tempo_deslocamento_minutos": matriz,
        "tempo_vistoria_minutos": {nome: 0 for nome in nomes},
        "limite_turno_minutos": 10_000,
    }


def custo_forca_bruta(dados: dict) -> float:
    """Custo ótimo por enumeração explícita de todas as permutações."""
    matriz = dados["tempo_deslocamento_minutos"]
    n = len(dados["pedidos"])
    melhor = float("inf")
    for ordem in itertools.permutations(range(1, n + 1)):
        percurso = (0, *ordem, 0)
        custo = sum(
            float("inf") if matriz[a][b] is None else matriz[a][b]
            for a, b in zip(percurso, percurso[1:])
        )
        if custo < melhor:
            melhor = custo
    return melhor


def validar_contra_forca_bruta(rng: random.Random) -> None:
    for numero in range(1, CASOS_VALIDACAO + 1):
        n = rng.randint(1, 7)
        dados = criar_instancia(n, rng, arestas_indisponiveis=True)
        esperado = custo_forca_bruta(dados)
        for metodo in METODOS:
            obtido = otimizar_rota(dados, metodo)
            if math_is_infinite(esperado):
                if obtido["rota_encontrada"]:
                    raise AssertionError(f"Caso {numero} ({metodo}): DP achou rota, força bruta não.")
            elif not obtido["rota_encontrada"] or abs(
                obtido["tempo_deslocamento_minutos"] - esperado
            ) > 1e-9:
                raise AssertionError(
                    f"Caso {numero} ({metodo}): esperado {esperado}, resultado DP {obtido}."
                )
    print(
        f"Validação: {CASOS_VALIDACAO} instâncias aleatórias (1–7 pedidos), "
        "incluindo grafos dirigidos e arestas indisponíveis, "
        "com memoização e tabulação: OK."
    )


def math_is_infinite(valor: float) -> bool:
    return valor == float("inf")


def medir(rng: random.Random) -> None:
    print("\nBenchmark sintético (grafos dirigidos completos; tempos inteiros aleatórios).")
    print("Pedidos | Estados (memo.) | Tempo memoização (s) | Tempo tabulação (s)")
    print("---------|-----------------|----------------------|--------------------")
    for n in TAMANHOS_BENCHMARK:
        dados = criar_instancia(n, rng, arestas_indisponiveis=False)
        tempos = {}
        custos = {}
        estados = 0
        for metodo in METODOS:
            inicio = time.perf_counter()
            resultado = otimizar_rota(dados, metodo)
            tempos[metodo] = time.perf_counter() - inicio
            if not resultado["rota_encontrada"]:
                raise AssertionError(f"O benchmark sintético com {n} pedidos não achou rota.")
            custos[metodo] = resultado["tempo_deslocamento_minutos"]
            if metodo == "memoizacao":
                estados = resultado["estados_dp"]
        if abs(custos["memoizacao"] - custos["tabulacao"]) > 1e-9:
            raise AssertionError(f"Métodos divergem com {n} pedidos: {custos}")
        print(f"{n:>8} | {estados:>15,} | {tempos['memoizacao']:>20.6f} | {tempos['tabulacao']:>19.6f}")


def medir_ganho(rng: random.Random) -> None:
    """Redução média do deslocamento em relação à ordem original, em instâncias sintéticas."""
    print(f"\nRedução do deslocamento em relação à ordem original ({INSTANCIAS_GANHO} instâncias sintéticas por tamanho).")
    print("Pedidos | Redução média | Redução máxima")
    print("---------|---------------|---------------")
    for n in TAMANHOS_GANHO:
        reducoes = []
        for _ in range(INSTANCIAS_GANHO):
            dados = criar_instancia(n, rng, arestas_indisponiveis=False)
            r = otimizar_rota(dados)
            reducoes.append(r["reducao_deslocamento_percentual"])
        print(f"{n:>8} | {sum(reducoes) / len(reducoes):>12.1f}% | {max(reducoes):>13.1f}%")
    print("(Dados aleatórios, sem geometria de ruas: tendem a exagerar o ganho e não representam o desempenho em ruas reais.)")


def main() -> None:
    print(f"Ambiente: Python {platform.python_version()} — {platform.platform()}")
    print(f"Semente fixa: {SEED}")
    rng = random.Random(SEED)
    validar_contra_forca_bruta(rng)
    medir(rng)
    medir_ganho(rng)


if __name__ == "__main__":
    main()
