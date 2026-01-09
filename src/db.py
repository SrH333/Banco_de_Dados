import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "viagens.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def migrate():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        email TEXT,
        telefone TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS destinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cidade TEXT NOT NULL,
        pais TEXT NOT NULL,
        vagas_total INTEGER NOT NULL,
        vagas_disponiveis INTEGER NOT NULL,
        UNIQUE(cidade, pais)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        destino_id INTEGER NOT NULL,
        vagas_reservadas INTEGER NOT NULL,
        data_reserva TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(destino_id) REFERENCES destinos(id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
    print("Migrações aplicadas com sucesso.")
