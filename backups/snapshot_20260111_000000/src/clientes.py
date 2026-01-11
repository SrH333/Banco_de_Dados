try:
    from src.db import get_conn
except Exception:
    try:
        from db import get_conn
    except Exception:
        from .db import get_conn

def criar_cliente(nome, email=None, telefone=None):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
            (nome, email, telefone)
        )
        conn.commit()
        print(f"Cliente '{nome}' cadastrado com sucesso.")
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {e}")
    finally:
        conn.close()


def listar_clientes():
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM clientes ORDER BY id")
        clientes = cur.fetchall()
        if not clientes:
            print("Nenhum cliente cadastrado.")
        else:
            for row in clientes:
                print(f"ID: {row['id']} | Nome: {row['nome']} | Email: {row['email']} | Telefone: {row['telefone']}")
    finally:
        conn.close()


def buscar_clientes():
    """Retorna lista de clientes (id e nome) para uso em reservas."""
    conn = get_conn()
    try:
        cur = conn.execute("SELECT id, nome FROM clientes ORDER BY id")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def editar_cliente(cliente_id, nome=None, email=None, telefone=None):
    conn = get_conn()
    try:
        cur = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cur.fetchone()
        if not cliente:
            print("Cliente não encontrado.")
            return

        novo_nome = nome if nome else cliente["nome"]
        novo_email = email if email else cliente["email"]
        novo_telefone = telefone if telefone else cliente["telefone"]

        conn.execute(
            "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?",
            (novo_nome, novo_email, novo_telefone, cliente_id)
        )
        conn.commit()
        print("Cliente atualizado com sucesso.")
    except Exception as e:
        print(f"Erro ao editar cliente: {e}")
    finally:
        conn.close()


def excluir_cliente(cliente_id):
    conn = get_conn()
    try:
        # Verifica se há reservas vinculadas
        cur = conn.execute("SELECT COUNT(*) AS total FROM reservas WHERE cliente_id = ?", (cliente_id,))
        total = cur.fetchone()["total"]
        if total > 0:
            print("Não é possível excluir: cliente possui reservas vinculadas.")
            return

        cur = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cur.fetchone()
        if not cliente:
            print("Cliente não encontrado.")
            return

        confirm = input(f"Confirmar exclusão do cliente '{cliente['nome']}'? (s/n): ").strip().lower()
        if confirm != "s":
            print("Exclusão cancelada.")
            return

        conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        print("Cliente excluído com sucesso.")
    except Exception as e:
        print(f"Erro ao excluir cliente: {e}")
    finally:
        conn.close()