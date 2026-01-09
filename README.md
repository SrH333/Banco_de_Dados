 # Sistema de Viagens

Pequeno sistema CLI para gerenciar clientes, destinos e reservas (SQLite).

## Requisitos
- Python 3.8+ (recomendado 3.11+)
- `requirements.txt` (se houver dependências)

## Instalação rápida
1. Crie e ative um ambiente virtual (opcional, recomendado):

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

2. Instale dependências (se houver):
```bash
pip install -r requirements.txt
```

## Inicializar banco de dados
Antes de rodar o app, crie as tabelas executando a migração:

```bash
python -c "from src.db import migrate; migrate()"
```

Isso criará (ou verificará) o arquivo `viagens.db` na raiz do projeto.

## Executar o aplicativo
Recomendado executar a partir da raiz do projeto para evitar problemas de import:

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
