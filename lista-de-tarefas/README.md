# 📝 Lista de Tarefas

Aplicativo de lista de tarefas em Python com interface gráfica (tkinter), busca, filtro por status e armazenamento automático em JSON.

## Funcionalidades

- Adicionar, editar e remover tarefas (título, descrição, data, hora e prazo opcional)
- Status: `pendente`, `em andamento` e `concluída` (com cores na tabela)
- Busca por texto e filtro por status
- Validação de datas e horas
- Dados salvos automaticamente em `~/.lista_tarefas/tarefas.json`
- Sem dependências externas

## Como executar

Requer Python 3.9+ (tkinter já vem com o Python; no Linux, instale com `sudo apt install python3-tk` se necessário).

```bash
git clone https://github.com/SEU-USUARIO/lista-de-tarefas.git
cd lista-de-tarefas
python app.py
```

## Testes

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```
├── app.py            # interface gráfica
├── tarefas.py        # regras de negócio e persistência
├── tests/            # testes automatizados
├── requirements.txt
└── LICENSE
```

## Atalhos

- **Duplo clique** em uma tarefa: editar
- **Delete**: remover a tarefa selecionada
- **Enter / Esc** no formulário: salvar / cancelar

## Licença

MIT
