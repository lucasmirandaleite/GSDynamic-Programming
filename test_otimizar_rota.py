import csv
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


class TestInstanciaSp156(unittest.TestCase):
    def test_instancia_com_pedidos_sp156_identificados_por_atributos(self):
        dados = json.loads(
            Path(__file__).with_name("dados_sp156.json").read_text(encoding="utf-8")
        )
        resultado = otimizar_rota(dados)
        self.assertTrue(resultado["rota_encontrada"])
        self.assertEqual(resultado["rota"][0], "Subprefeitura São Mateus")
        self.assertEqual(resultado["rota"][-1], "Subprefeitura São Mateus")
        self.assertCountEqual(resultado["rota"][1:-1], dados["pedidos"])
        self.assertAlmostEqual(resultado["tempo_deslocamento_minutos"], 48.0)
        self.assertAlmostEqual(resultado["tempo_deslocamento_ordem_original_minutos"], 48.5)
        self.assertTrue(resultado["cabe_no_turno"])
        self.assertEqual([p.split(" - ", 1)[0] for p in dados["pedidos"]], ["P1", "P2", "P3"])
        self.assertIn("não contém protocolo nem _id", dados["descricao"])

    def test_csv_minimo_tem_registros_confirmados_e_ids_locais(self):
        caminho = Path(__file__).with_name("amostra_sp156_tapa_buraco_2014.csv")
        with caminho.open(encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            self.assertEqual(leitor.fieldnames[0], "ID local")
            linhas = list(leitor)
        self.assertEqual([linha["ID local"] for linha in linhas], ["P1", "P2", "P3"])
        self.assertEqual(
            [(linha["Data de abertura"], linha["Bairro"], linha["Status da solicitação"], linha["Data do parecer"].split()[0]) for linha in linhas],
            [
                ("2014-07-07", "PARQUE SAO RAFAEL", "REALIZADA", "2014-10-13"),
                ("2014-07-13", "JARDIM SAO RAFAEL", "REALIZADA", "2014-08-08"),
                ("2014-07-23", "JARDIM IGUATEMI", "REALIZADA", "2014-10-13"),
            ],
        )


class TestTabulacaoESensibilidade(unittest.TestCase):
    def test_tabulacao_e_memoizacao_tem_o_mesmo_custo_minimo(self):
        import random

        rng = random.Random(7)
        for _ in range(60):
            n = rng.randint(0, 7)
            nomes = [f"P{i}" for i in range(n)]
            matriz = [
                [0 if i == j else (None if rng.random() < 0.2 else rng.randint(1, 30))
                 for j in range(n + 1)]
                for i in range(n + 1)
            ]
            dados = {
                "base": "Base",
                "pedidos": nomes,
                "locais": ["Base", *nomes],
                "tempo_deslocamento_minutos": matriz,
                "tempo_vistoria_minutos": {nome: 1 for nome in nomes},
                "limite_turno_minutos": 1000,
            }
            memo = otimizar_rota(dados, "memoizacao")
            tab = otimizar_rota(dados, "tabulacao")
            self.assertEqual(memo["rota_encontrada"], tab["rota_encontrada"])
            if memo["rota_encontrada"]:
                self.assertAlmostEqual(
                    memo["tempo_deslocamento_minutos"], tab["tempo_deslocamento_minutos"]
                )
                self.assertCountEqual(tab["rota"][1:-1], nomes)
                self.assertEqual(tab["rota"][0], "Base")
                self.assertEqual(tab["rota"][-1], "Base")

    def test_metodo_invalido_e_rejeitado(self):
        dados = json.loads(
            Path(__file__).with_name("dados_demo.json").read_text(encoding="utf-8")
        )
        with self.assertRaises(ValueError):
            otimizar_rota(dados, "forca_bruta")

    def test_analise_de_sensibilidade_cobre_as_64_combinacoes(self):
        from analise_sensibilidade import analisar

        dados = json.loads(
            Path(__file__).with_name("dados_sp156.json").read_text(encoding="utf-8")
        )
        resultado = analisar(dados)
        self.assertEqual(resultado["cenarios"], 64)
        self.assertLessEqual(resultado["deslocamento_min"], 48.0)
        self.assertGreaterEqual(resultado["deslocamento_max"], 48.0)
        self.assertGreaterEqual(resultado["reducao_min"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
