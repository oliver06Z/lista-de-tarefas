import tempfile
import unittest
from pathlib import Path

from tarefas import GerenciadorTarefas, ErroValidacao


class TestGerenciador(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.caminho = Path(self.tmp.name) / "t.json"
        self.g = GerenciadorTarefas(self.caminho)

    def tearDown(self):
        self.tmp.cleanup()

    def test_adicionar_e_persistir(self):
        self.g.adicionar("Estudar", data="2026-11-01", hora="09:30")
        novo = GerenciadorTarefas(self.caminho)
        self.assertEqual(len(novo.tarefas), 1)
        self.assertEqual(novo.tarefas[0].titulo, "Estudar")

    def test_validacao(self):
        with self.assertRaises(ErroValidacao):
            self.g.adicionar("")
        with self.assertRaises(ErroValidacao):
            self.g.adicionar("X", data="01/11/2026")
        with self.assertRaises(ErroValidacao):
            self.g.adicionar("X", hora="25:00")

    def test_status_e_remocao(self):
        t = self.g.adicionar("A")
        self.g.atualizar_status(t.id, "concluída")
        self.assertEqual(self.g.obter(t.id).status, "concluída")
        with self.assertRaises(ErroValidacao):
            self.g.atualizar_status(t.id, "xyz")
        self.g.remover(t.id)
        self.assertEqual(self.g.tarefas, [])

    def test_filtro_e_busca(self):
        self.g.adicionar("Comprar pão")
        b = self.g.adicionar("Ler livro", status="em andamento")
        self.assertEqual([t.id for t in self.g.listar(status="em andamento")], [b.id])
        self.assertEqual(len(self.g.listar(busca="pão")), 1)

    def test_ids_nao_repetem(self):
        a = self.g.adicionar("A")
        self.g.remover(a.id)
        b = self.g.adicionar("B")
        self.assertEqual(b.id, 1)  # id recomeça pois a lista ficou vazia


if __name__ == "__main__":
    unittest.main()
