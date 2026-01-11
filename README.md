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

Ou, dentro da pasta `src`:

```bash
cd src
python app.py
```

O menu principal oferece: `Clientes`, `Destinos` e `Reservas`.

- Em `Reservas` há a opção **3. Editar/Excluir reserva** que permite:
	- Aumentar número de vagas reservadas (se houver disponibilidade)
	- Diminuir número de vagas reservadas (devolve vagas ao destino)
	- Excluir reserva (devolve todas as vagas ao destino)

## Estrutura do projeto
- [src/app.py](src/app.py) — ponto de entrada e menus
- [src/db.py](src/db.py) — conexão e migração do banco
- [src/clientes.py](src/clientes.py) — operações de clientes
- [src/destinos.py](src/destinos.py) — operações de destinos
- [src/reservas.py](src/reservas.py) — operações de reservas
- `viagens.db` — arquivo SQLite (gerado após migrar)

## Dicas
- Execute sempre a partir da raiz do projeto (`python -m src.app`) para que os imports relativos funcionem corretamente.
- Para depurar, verifique `viagens.db` com um cliente SQLite (DB Browser for SQLite, etc.).

Se quiser, posso também adicionar instruções de contribution, testes automatizados ou um script `make`/`tasks` para facilitar execução.
