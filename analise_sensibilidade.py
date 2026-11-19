"""Análise de sensibilidade da instância SP156 às faixas de tempo informadas.

Os tempos de deslocamento de dados_sp156.json são o ponto médio de faixas
(mínimo–máximo) informadas pelo grupo. Este script resolve a instância em todas
as combinações de extremos das faixas (cada trecho no mínimo ou no máximo, igual
nos dois sentidos) para mostrar quanto o resultado depende dessas estimativas.

Uso: python analise_sensibilidade.py [arquivo.json]
"""
from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from otimizar_rota import otimizar_rota


def analisar(dados: dict[str, Any]) -> dict[str, Any]:
    """Resolve todas as combinações de extremos das faixas e resume os resultados."""
    faixas = dados.get("faixas_informadas_minutos")
    if not faixas:
        raise ValueError("A instância não tem 'faixas_informadas_minutos'.")
    n_locais = len(dados["locais"])
    cenarios = []
    for escolha in itertools.product((False, True), repeat=len(faixas)):
        matriz = [[0.0] * n_locais for _ in range(n_locais)]
        for faixa, usa_maximo in zip(faixas, escolha):
            valor = float(faixa["max"] if usa_maximo else faixa["min"])
            matriz[faixa["de"]][faixa["para"]] = valor
            matriz[faixa["para"]][faixa["de"]] = valor
        cenario = {**dados, "tempo_deslocamento_minutos": matriz}
        r = otimizar_rota(cenario)
        cenarios.append(
            {
                "deslocamento": r["tempo_deslocamento_minutos"],
                "original": r["tempo_deslocamento_ordem_original_minutos"],
                "reducao": r["reducao_deslocamento_percentual"],
                "primeira_parada": r["rota"][1],
            }
        )
    reducoes = [c["reducao"] for c in cenarios]
    deslocamentos = [c["deslocamento"] for c in cenarios]
    return {
        "cenarios": len(cenarios),
        "deslocamento_min": min(deslocamentos),
        "deslocamento_max": max(deslocamentos),
        "reducao_min": min(reducoes),
        "reducao_max": max(reducoes),
        "cenarios_sem_ganho": sum(1 for r in reducoes if r == 0),
        "primeiras_paradas": Counter(c["primeira_parada"] for c in cenarios),
    }


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("dados_sp156.json")
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    base = otimizar_rota(dados)
    r = analisar(dados)
    print("ANÁLISE DE SENSIBILIDADE — faixas de tempo informadas pelo grupo")
    print(f"Caso central (ponto médio): deslocamento {base['tempo_deslocamento_minutos']:.1f} min, "
          f"redução {base['reducao_deslocamento_percentual']:.1f}%")
    print(f"Cenários (cada trecho no mínimo ou no máximo da faixa): {r['cenarios']}")
    print(f"Deslocamento ótimo: de {r['deslocamento_min']:.1f} a {r['deslocamento_max']:.1f} min")
    print(f"Redução em relação à ordem original: de {r['reducao_min']:.1f}% a {r['reducao_max']:.1f}%")
    print(f"Cenários em que a ordem original já é a ótima (redução 0%): {r['cenarios_sem_ganho']} de {r['cenarios']}")
    print("Primeira parada da rota ótima:")
    for parada, qtd in r["primeiras_paradas"].most_common():
        print(f"  {parada}: {qtd} cenários")
    print("Leitura: o ganho percentual e a rota ótima dependem das estimativas de tempo; "
          "o resultado de cerca de 1% no caso central não deve ser lido como um valor firme.")


if __name__ == "__main__":
    main()
