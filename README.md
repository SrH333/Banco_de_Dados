 # Sistema de Viagens

Pequeno sistema CLI para gerenciar clientes, destinos e reservas (SQLite).
# Sistema de Viagens

Pequeno sistema para gerenciar **clientes**, **destinos** e **reservas** usando SQLite.
O projeto originalmente era uma aplicação CLI e foi estendida com uma interface web em Flask.

## Recursos

- Gerenciamento de clientes (criar, listar, editar, excluir)
- Gerenciamento de destinos (criar, listar, editar, excluir)
- Reservas entre clientes e destinos (criar, aumentar, diminuir, excluir)
- Interface CLI (original) e interface web (Flask)

## Requisitos

- Python 3.8+ (recomendado 3.11+)
- venv (recomendado)

## Conteúdo importante do repositório

- `src/app.py` — versão CLI (menu no terminal)
- `src/web.py` — servidor Flask (interface web)
- `src/db.py` — conexão com SQLite e função `migrate()`
- `src/clientes.py`, `src/destinos.py`, `src/reservas.py` — lógica de domínio
- `src/templates/` — templates Jinja2 usados pela interface web
- `requirements.txt` — dependências (inclui `Flask`)

## Instalação e execução (rápido)

1. Clone o repositório e entre na pasta do projeto.

2. Crie e ative um ambiente virtual (recomendado):

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (cmd):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale dependências:

```bash
pip install -r requirements.txt
```

4. Crie as tabelas do banco (migração):

```bash
python -c "from src.db import migrate; migrate()"
```

Isso criará (ou verificará) o arquivo `viagens.db` na raiz do projeto.

## Executar a aplicação

Versão web (recomendada para visitantes):

```bash
# com a venv ativa, a partir da raiz do repositório
python -m src.web
```
Abra http://127.0.0.1:5000 no navegador. As páginas principais:

- `/clientes` — listar, criar, editar e excluir clientes
- `/destinos` — listar, criar, editar e excluir destinos
- `/reservas` — listar, criar reservas; editar reserva permite aumentar/diminuir/excluir

Versão CLI (original):

```bash
python -m src.app
```

## Observações sobre o banco

- O arquivo SQLite `viagens.db` fica na raiz do projeto. Faça backup antes de alterações destrutivas.
- A aplicação web e a CLI usam o mesmo banco.

## Desenvolvimento e contribuição

Pull requests são bem-vindos. Sugestões úteis:

- adicionar autenticação e autorização
- melhorar validações de entrada no front e back-end
- testes automatizados e CI
- melhorias de UI/UX

Se quiser, posso criar uma branch, preparar um commit com estas mudanças e abrir um PR de exemplo.

## Licença

Adicione a licença do projeto aqui (por exemplo: MIT).

---

Se desejar, eu faço o commit automático com mensagem padrão e crio uma branch; quer que eu faça isso agora?
