import sqlite3
from pathlib import Path

# Caminho absoluto para o arquivo viagens.db na raiz do projeto
DB_PATH = Path(__file__).resolve().parent.parent / "viagens.db"

def get_conn():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

def migrate():
    """Executa a criação das tabelas se ainda não existirem."""
    conn = get_conn()
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT
        );

        CREATE TABLE IF NOT EXISTS destinos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cidade TEXT NOT NULL,
            pais TEXT NOT NULL,
            vagas INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            destino_id INTEGER NOT NULL,
            vagas INTEGER NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (destino_id) REFERENCES destinos(id)
        );
        """)
        conn.commit()
        print("Migração concluída: tabelas criadas/verificadas.")
    except Exception as e:
        print(f"Erro na migração do banco: {e}")
    finally:
        conn.close()
