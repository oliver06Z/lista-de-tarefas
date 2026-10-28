"""Interface gráfica (tkinter) da Lista de Tarefas."""
import tkinter as tk
from tkinter import ttk, messagebox

from tarefas import GerenciadorTarefas, ErroValidacao, STATUS_VALIDOS

COR_FUNDO = "#f5f6fa"
COR_PRIMARIA = "#4c6ef5"
COR_TEXTO = "#212529"
CORES_STATUS = {"pendente": "#fff3bf", "em andamento": "#d0ebff", "concluída": "#d3f9d8"}


class FormularioTarefa(tk.Toplevel):
    """Janela para adicionar ou editar uma tarefa."""

    def __init__(self, master, tarefa=None):
        super().__init__(master)
        self.title("Editar tarefa" if tarefa else "Nova tarefa")
        self.configure(bg=COR_FUNDO, padx=20, pady=16)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.resultado = None

        self.vars = {c: tk.StringVar(value=(getattr(tarefa, c) or "") if tarefa else "")
                     for c in ("titulo", "data", "hora", "prazo")}
        self.var_status = tk.StringVar(value=tarefa.status if tarefa else "pendente")

        def linha(r, rotulo, widget):
            ttk.Label(self, text=rotulo).grid(row=r, column=0, sticky="nw", pady=5, padx=(0, 12))
            widget.grid(row=r, column=1, sticky="ew", pady=5)

        linha(0, "Título *", ttk.Entry(self, textvariable=self.vars["titulo"], width=38))
        self.txt_desc = tk.Text(self, width=38, height=4, relief="solid", bd=1, font=("Segoe UI", 10))
        self.txt_desc.insert("1.0", tarefa.descricao if tarefa else "")
        linha(1, "Descrição", self.txt_desc)
        linha(2, "Data (AAAA-MM-DD)", ttk.Entry(self, textvariable=self.vars["data"]))
        linha(3, "Hora (HH:MM)", ttk.Entry(self, textvariable=self.vars["hora"]))
        linha(4, "Prazo (opcional)", ttk.Entry(self, textvariable=self.vars["prazo"]))
        linha(5, "Status", ttk.Combobox(self, textvariable=self.var_status,
                                        values=STATUS_VALIDOS, state="readonly"))

        botoes = ttk.Frame(self)
        botoes.grid(row=6, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(botoes, text="Salvar", style="Primaria.TButton", command=self._salvar).pack(side="right")
        self.bind("<Return>", lambda e: self._salvar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _salvar(self):
        self.resultado = {
            "titulo": self.vars["titulo"].get(),
            "descricao": self.txt_desc.get("1.0", "end").strip(),
            "data": self.vars["data"].get().strip(),
            "hora": self.vars["hora"].get().strip(),
            "prazo": self.vars["prazo"].get().strip() or None,
            "status": self.var_status.get(),
        }
        self.destroy()


class App(tk.Tk):
    def __init__(self, gerenciador=None):
        super().__init__()
        self.gerenciador = gerenciador or GerenciadorTarefas()
        self.title("📝 Lista de Tarefas")
        self.geometry("860x520")
        self.minsize(720, 420)
        self.configure(bg=COR_FUNDO)
        self._estilo()
        self._montar()
        self.atualizar()

    def _estilo(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=COR_FUNDO, foreground=COR_TEXTO, font=("Segoe UI", 10))
        s.configure("Treeview", rowheight=30, fieldbackground="white", borderwidth=0)
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=6)
        s.configure("Titulo.TLabel", font=("Segoe UI", 18, "bold"), foreground=COR_PRIMARIA)
        s.configure("Primaria.TButton", background=COR_PRIMARIA, foreground="white", padding=6)
        s.map("Primaria.TButton", background=[("active", "#3b5bdb")])
        s.configure("TButton", padding=6)

    def _montar(self):
        topo = ttk.Frame(self, padding=(16, 14, 16, 6))
        topo.pack(fill="x")
        ttk.Label(topo, text="Minhas Tarefas", style="Titulo.TLabel").pack(side="left")
        ttk.Button(topo, text="＋ Nova tarefa", style="Primaria.TButton",
                   command=self.adicionar).pack(side="right")

        filtros = ttk.Frame(self, padding=(16, 4))
        filtros.pack(fill="x")
        ttk.Label(filtros, text="Buscar:").pack(side="left")
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *_: self.atualizar())
        ttk.Entry(filtros, textvariable=self.var_busca, width=28).pack(side="left", padx=(6, 16))
        ttk.Label(filtros, text="Status:").pack(side="left")
        self.var_filtro = tk.StringVar(value="todos")
        cb = ttk.Combobox(filtros, textvariable=self.var_filtro, state="readonly", width=14,
                          values=("todos", *STATUS_VALIDOS))
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar())

        meio = ttk.Frame(self, padding=(16, 8))
        meio.pack(fill="both", expand=True)
        colunas = ("titulo", "data", "hora", "prazo", "status")
        self.tabela = ttk.Treeview(meio, columns=colunas, show="headings", selectmode="browse")
        for col, texto, larg in (("titulo", "Título", 300), ("data", "Data", 100),
                                 ("hora", "Hora", 70), ("prazo", "Prazo", 100), ("status", "Status", 120)):
            self.tabela.heading(col, text=texto)
            self.tabela.column(col, width=larg, anchor="w" if col == "titulo" else "center")
        for status, cor in CORES_STATUS.items():
            self.tabela.tag_configure(status, background=cor)
        barra = ttk.Scrollbar(meio, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.tabela.bind("<Double-1>", lambda e: self.editar())
        self.tabela.bind("<Delete>", lambda e: self.remover())

        acoes = ttk.Frame(self, padding=(16, 4, 16, 8))
        acoes.pack(fill="x")
        ttk.Button(acoes, text="✏️ Editar", command=self.editar).pack(side="left")
        ttk.Button(acoes, text="🔄 Próximo status", command=self.proximo_status).pack(side="left", padx=6)
        ttk.Button(acoes, text="✅ Concluir", command=lambda: self.definir_status("concluída")).pack(side="left")
        ttk.Button(acoes, text="🗑️ Remover", command=self.remover).pack(side="left", padx=6)

        self.var_rodape = tk.StringVar()
        ttk.Label(self, textvariable=self.var_rodape, padding=(16, 0, 16, 10),
                  foreground="#868e96").pack(fill="x")

    # --- ações ---
    def atualizar(self):
        self.tabela.delete(*self.tabela.get_children())
        filtro = self.var_filtro.get()
        for t in self.gerenciador.listar(None if filtro == "todos" else filtro, self.var_busca.get()):
            self.tabela.insert("", "end", iid=str(t.id), tags=(t.status,),
                               values=(t.titulo, t.data, t.hora, t.prazo or "—", t.status))
        todas = self.gerenciador.tarefas
        feitas = sum(t.status == "concluída" for t in todas)
        self.var_rodape.set(f"{len(todas)} tarefa(s) • {feitas} concluída(s) • duplo clique para editar")

    def _selecionada(self):
        sel = self.tabela.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione uma tarefa primeiro.")
            return None
        return int(sel[0])

    def _executar(self, funcao, *args, **kwargs):
        try:
            funcao(*args, **kwargs)
        except ErroValidacao as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return False
        self.atualizar()
        return True

    def adicionar(self):
        while True:
            form = FormularioTarefa(self)
            self.wait_window(form)
            if form.resultado is None or self._executar(self.gerenciador.adicionar, **form.resultado):
                break

    def editar(self):
        id_ = self._selecionada()
        if id_ is None:
            return
        tarefa = self.gerenciador.obter(id_)
        form = FormularioTarefa(self, tarefa)
        self.wait_window(form)
        if form.resultado:
            self._executar(self.gerenciador.editar, id_, **form.resultado)

    def definir_status(self, status):
        id_ = self._selecionada()
        if id_ is not None:
            self._executar(self.gerenciador.atualizar_status, id_, status)
            self.tabela.selection_set(str(id_))

    def proximo_status(self):
        id_ = self._selecionada()
        if id_ is None:
            return
        atual = STATUS_VALIDOS.index(self.gerenciador.obter(id_).status)
        self.definir_status(STATUS_VALIDOS[(atual + 1) % len(STATUS_VALIDOS)])

    def remover(self):
        id_ = self._selecionada()
        if id_ is not None and messagebox.askyesno("Remover", "Deseja remover esta tarefa?"):
            self._executar(self.gerenciador.remover, id_)


if __name__ == "__main__":
    App().mainloop()
