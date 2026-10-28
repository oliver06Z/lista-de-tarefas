"""Lógica de negócio e persistência da lista de tarefas (sem dependência de interface)."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path

STATUS_VALIDOS = ("pendente", "em andamento", "concluída")
ARQUIVO_PADRAO = Path.home() / ".lista_tarefas" / "tarefas.json"


class ErroValidacao(ValueError):
    """Levantado quando os dados de uma tarefa são inválidos."""


@dataclass
class Tarefa:
    id: int
    titulo: str
    descricao: str = ""
    data: str = ""
    hora: str = ""
    prazo: str | None = None
    status: str = "pendente"


def _validar(titulo: str, data: str, hora: str, prazo: str | None, status: str) -> None:
    if not titulo.strip():
        raise ErroValidacao("O título é obrigatório.")
    for valor, formato, nome in ((data, "%Y-%m-%d", "Data (AAAA-MM-DD)"),
                                 (hora, "%H:%M", "Hora (HH:MM)"),
                                 (prazo, "%Y-%m-%d", "Prazo (AAAA-MM-DD)")):
        if valor:
            try:
                datetime.strptime(valor, formato)
            except ValueError:
                raise ErroValidacao(f"{nome} inválida: '{valor}'.") from None
    if status not in STATUS_VALIDOS:
        raise ErroValidacao(f"Status inválido: '{status}'.")


@dataclass
class GerenciadorTarefas:
    caminho: Path = ARQUIVO_PADRAO
    tarefas: list[Tarefa] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.caminho = Path(self.caminho)
        self.carregar()

    # --- persistência ---
    def carregar(self) -> None:
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            self.tarefas = [Tarefa(**d) for d in dados]
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            self.tarefas = []

    def salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        conteudo = json.dumps([asdict(t) for t in self.tarefas], ensure_ascii=False, indent=2)
        self.caminho.write_text(conteudo, encoding="utf-8")

    # --- operações ---
    def _proximo_id(self) -> int:
        return max((t.id for t in self.tarefas), default=0) + 1

    def adicionar(self, titulo, descricao="", data="", hora="", prazo=None, status="pendente") -> Tarefa:
        prazo = prazo or None
        _validar(titulo, data, hora, prazo, status)
        tarefa = Tarefa(self._proximo_id(), titulo.strip(), descricao.strip(), data, hora, prazo, status)
        self.tarefas.append(tarefa)
        self.salvar()
        return tarefa

    def obter(self, id_: int) -> Tarefa:
        for t in self.tarefas:
            if t.id == id_:
                return t
        raise KeyError(f"Tarefa {id_} não encontrada.")

    def editar(self, id_: int, **campos) -> Tarefa:
        tarefa = self.obter(id_)
        novos = {**asdict(tarefa), **campos}
        novos["prazo"] = novos["prazo"] or None
        _validar(novos["titulo"], novos["data"], novos["hora"], novos["prazo"], novos["status"])
        for chave, valor in novos.items():
            setattr(tarefa, chave, valor.strip() if isinstance(valor, str) else valor)
        self.salvar()
        return tarefa

    def atualizar_status(self, id_: int, status: str) -> Tarefa:
        return self.editar(id_, status=status)

    def remover(self, id_: int) -> None:
        self.tarefas.remove(self.obter(id_))
        self.salvar()

    def listar(self, status: str | None = None, busca: str = "") -> list[Tarefa]:
        busca = busca.lower().strip()
        resultado = [
            t for t in self.tarefas
            if (not status or t.status == status)
            and (not busca or busca in t.titulo.lower() or busca in t.descricao.lower())
        ]
        return sorted(resultado, key=lambda t: (t.data or "9999", t.hora or "99:99", t.id))
