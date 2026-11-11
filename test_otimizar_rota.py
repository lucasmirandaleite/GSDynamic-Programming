import json
import unittest
from pathlib import Path

from otimizar_rota import otimizar_rota


class TestRuaEmDia(unittest.TestCase):
    def setUp(self):
        self.instancia = json.loads(
            Path(__file__).with_name("dados_demo.json").read_text(encoding="utf-8")
        )

    def test_encontra_rota_minima_visitando_todos_e_retornando(self):
        resultado = otimizar_rota(self.instancia)
        self.assertTrue(resultado["rota_encontrada"])
        self.assertEqual(resultado["rota"][0], "Base de Manutenção")
        self.assertEqual(resultado["rota"][-1], "Base de Manutenção")
        self.assertCountEqual(
            resultado["rota"][1:-1], self.instancia["pedidos"]
        )
        self.assertEqual(resultado["tempo_deslocamento_minutos"], 27)

    def test_calcula_reducao_em_relacao_a_ordem_original(self):
        resultado = otimizar_rota(self.instancia)
        original = resultado["tempo_deslocamento_ordem_original_minutos"]
        self.assertGreaterEqual(original, resultado["tempo_deslocamento_minutos"])
        esperado = (original - resultado["tempo_deslocamento_minutos"]) / original * 100
        self.assertAlmostEqual(resultado["reducao_deslocamento_percentual"], esperado)

    def test_ordem_original_indisponivel_nao_gera_reducao(self):
        dados = {
            "base": "Base",
            "pedidos": ["A", "B"],
            "locais": ["Base", "A", "B"],
            "tempo_deslocamento_minutos": [
                [0, None, 4],
                [4, 0, 6],
                [5, 3, 0],
            ],
            "tempo_vistoria_minutos": {"A": 10, "B": 10},
            "limite_turno_minutos": 60,
        }
        resultado = otimizar_rota(dados)
        self.assertTrue(resultado["rota_encontrada"])
        self.assertEqual(resultado["rota"], ["Base", "B", "A", "Base"])
        self.assertIsNone(resultado["tempo_deslocamento_ordem_original_minutos"])
        self.assertIsNone(resultado["reducao_deslocamento_percentual"])

    def test_soma_tempo_de_vistoria_e_verifica_turno(self):
        resultado = otimizar_rota(self.instancia)
        self.assertEqual(resultado["tempo_vistoria_minutos"], 37)
        self.assertEqual(resultado["tempo_total_minutos"], 64)
        self.assertTrue(resultado["cabe_no_turno"])

    def test_identifica_turno_insuficiente_sem_alterar_rota(self):
        dados = dict(self.instancia)
        dados["limite_turno_minutos"] = 60
        resultado = otimizar_rota(dados)
        self.assertFalse(resultado["cabe_no_turno"])
        self.assertEqual(resultado["tempo_total_minutos"], 64)

    def test_retorna_sem_rota_quando_trechos_sao_indisponiveis(self):
        dados = {
            "base": "Base",
            "pedidos": ["A", "B"],
            "locais": ["Base", "A", "B"],
            "tempo_deslocamento_minutos": [
                [0, 5, None],
                [5, 0, None],
                [None, None, 0],
            ],
            "tempo_vistoria_minutos": {"A": 10, "B": 10},
            "limite_turno_minutos": 60,
        }
        resultado = otimizar_rota(dados)
        self.assertFalse(resultado["rota_encontrada"])

    def test_rejeita_matriz_fora_de_formato(self):
        dados = dict(self.instancia)
        dados["tempo_deslocamento_minutos"] = [[0, 1], [1, 0]]
        with self.assertRaises(ValueError):
            otimizar_rota(dados)

    def test_roteiro_sem_pedidos_retorna_a_base(self):
        dados = {
            "base": "Base",
            "pedidos": [],
            "locais": ["Base"],
            "tempo_deslocamento_minutos": [[0]],
            "tempo_vistoria_minutos": {},
            "limite_turno_minutos": 60,
        }
        resultado = otimizar_rota(dados)
        self.assertEqual(resultado["rota"], ["Base", "Base"])
        self.assertEqual(resultado["tempo_total_minutos"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
